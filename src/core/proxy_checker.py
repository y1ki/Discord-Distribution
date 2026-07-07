import asyncio
import time
import ssl
import aiohttp
from aiohttp_socks import ProxyConnector
from dataclasses import dataclass
from typing import Optional, List, Callable
from pathlib import Path


@dataclass
class ProxyResult:
    ip: str
    port: int
    login: Optional[str]
    password: Optional[str]
    protocol: str
    status: str
    response_time: Optional[float]
    country: str = "UN"


class ProxyChecker:
    def __init__(self, timeout: int = 10, max_workers: int = 100):
        self.timeout = timeout
        self.autodetect_timeout = 2
        self.max_workers = max_workers
        self.test_url = "http://httpbin.org/ip"
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    async def get_country_code(self, ip: str, session: aiohttp.ClientSession) -> str:
        try:
            timeout = aiohttp.ClientTimeout(total=3)
            async with session.get(f"http://ip-api.com/json/{ip}?fields=countryCode", timeout=timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("countryCode", "UN")
        except Exception:
            return "UN"
        return "UN"

    async def check_single_proxy(self, ip: str, port: int, protocol: str,
                                  login: Optional[str] = None,
                                  password: Optional[str] = None,
                                  custom_timeout: Optional[int] = None) -> ProxyResult:
        start_time = time.time()
        country = "UN"
        
        try:
            timeout_val = custom_timeout if custom_timeout else self.timeout
            timeout = aiohttp.ClientTimeout(total=timeout_val, connect=1)
            
            proxy_url = self._build_proxy_url(ip, port, protocol, login, password)
            connector = ProxyConnector.from_url(proxy_url, ssl=self.ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(self.test_url, timeout=timeout, ssl=self.ssl_context) as response:
                    if response.status == 200:
                        elapsed = time.time() - start_time
                        
                        async with aiohttp.ClientSession() as geo_session:
                            country = await self.get_country_code(ip, geo_session)
                        
                        return ProxyResult(
                            ip=ip, port=port, login=login, password=password,
                            protocol=protocol, status="alive", response_time=elapsed, country=country
                        )
        except Exception:
            return ProxyResult(
                ip=ip, port=port, login=login, password=password,
                protocol=protocol, status="dead", response_time=None, country=country
            )

        return ProxyResult(
            ip=ip, port=port, login=login, password=password,
            protocol=protocol, status="dead", response_time=None, country=country
        )

    async def check_single_proxy_autodetect(self, ip: str, port: int,
                                            login: Optional[str] = None,
                                            password: Optional[str] = None) -> ProxyResult:
        protocols = ["HTTP", "SOCKS5", "SOCKS4", "HTTPS"]
        
        for protocol in protocols:
            result = await self.check_single_proxy(ip, port, protocol, login, password,
                                                   custom_timeout=self.autodetect_timeout)
            if result.status == "alive":
                return result
        
        return ProxyResult(
            ip=ip, port=port, login=login, password=password,
            protocol="UNKNOWN", status="dead", response_time=None
        )

    async def check_proxies(self, proxies: List[tuple],
                            progress_callback: Optional[Callable] = None,
                            log_callback: Optional[Callable] = None,
                            should_stop_callback: Optional[Callable] = None,
                            force_protocol: Optional[str] = None) -> List[ProxyResult]:
        completed = 0
        total = len(proxies)
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def check_with_semaphore(proxy_data, index):
            nonlocal completed
            if should_stop_callback and should_stop_callback():
                return None
            
            async with semaphore:
                if should_stop_callback and should_stop_callback():
                    return None
                
                ip, port, protocol, login, password = proxy_data
                
                if not force_protocol or force_protocol == "autodetect":
                    result = await self.check_single_proxy_autodetect(ip, port, login, password)
                else:
                    result = await self.check_single_proxy(ip, port, force_protocol.upper(), login, password)
                
                completed += 1
                if progress_callback and (completed % 2 == 0 or completed == total):
                    progress_callback(completed, total)
                
                if log_callback:
                    if result.status == "alive":
                        proto_info = f" [{result.protocol}]" if (not force_protocol or force_protocol == "autodetect") else ""
                        log_callback(f"{ip}:{port}{proto_info} | alive", "green")
                    else:
                        log_callback(f"{ip}:{port} | dead", "red")
                
                return result
        
        tasks = [check_with_semaphore(proxy, i) for i, proxy in enumerate(proxies)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        if progress_callback:
            progress_callback(total, total)
        
        return [r for r in results if r is not None and not isinstance(r, Exception)]

    def _build_proxy_url(self, ip: str, port: int, protocol: str,
                         login: Optional[str] = None,
                         password: Optional[str] = None) -> str:
        protocol_lower = protocol.lower()
        
        if login and password:
            auth = f"{login}:{password}@"
        else:
            auth = ""
        
        return f"{protocol_lower}://{auth}{ip}:{port}"

    @staticmethod
    def parse_proxy_line(line: str) -> Optional[tuple]:
        line = line.strip()
        if not line or line.startswith("#"):
            return None
        
        protocol = "HTTP"
        login = None
        password = None
        
        if "://" in line:
            protocol_part, rest = line.split("://", 1)
            protocol = protocol_part.upper()
        else:
            rest = line
        
        if "@" in rest:
            auth_part, addr_part = rest.split("@", 1)
            if ":" in auth_part:
                parts = auth_part.split(":", 1)
                login = parts[0]
                password = parts[1] if len(parts) > 1 else None
        else:
            addr_part = rest
            colon_count = addr_part.count(":")
            
            if colon_count == 3:
                parts = addr_part.split(":")
                addr_part = f"{parts[0]}:{parts[1]}"
                login = parts[2]
                password = parts[3]
        
        if ":" not in addr_part:
            return None
        
        addr_parts = addr_part.split(":", 1)
        if len(addr_parts) != 2:
            return None
        
        ip = addr_parts[0].strip()
        port_str = addr_parts[1].strip()
        
        try:
            port = int(port_str)
        except ValueError:
            return None
        
        return (ip, port, protocol, login, password)

    @staticmethod
    def load_proxies_from_file(file_path: str) -> tuple[List[tuple], int]:
        proxies = []
        seen = set()
        duplicates = 0
        path = Path(file_path)
        
        if not path.exists():
            return proxies, 0
        
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                parsed = ProxyChecker.parse_proxy_line(line)
                if parsed:
                    ip, port, protocol, login, password = parsed
                    key = (ip, port)
                    if key not in seen:
                        seen.add(key)
                        proxies.append(parsed)
                    else:
                        duplicates += 1
        
        return proxies, duplicates
