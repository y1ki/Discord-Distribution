import aiohttp
import asyncio
from typing import Optional, Dict, Any

try:
    from aiohttp_socks import ProxyConnector, ProxyType
    SOCKS_AVAILABLE = True
except ImportError:
    SOCKS_AVAILABLE = False


class TokenChecker:
    API_URL = "https://discord.com/api/v9/users/@me"
    GUILDS_URL = "https://discord.com/api/v9/users/@me/guilds"
    CHANNELS_URL = "https://discord.com/api/v9/users/@me/channels"
    
    def __init__(self, timeout: int = 10):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
    
    async def check_token(self, token: str, proxy: Optional[Dict[str, str]] = None, detailed: bool = False) -> Dict[str, Any]:
        headers = {
            "authorization": token,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        connector = None
        proxy_url = None
        
        if proxy:
            protocol = proxy.get('protocol', 'http').lower()
            ip = proxy['ip']
            port = proxy['port']
            login = proxy.get('login')
            password = proxy.get('password')
            
            if protocol in ['socks4', 'socks5']:
                if not SOCKS_AVAILABLE:
                    return {"valid": False, "error": "aiohttp-socks not installed"}
                
                proxy_type = ProxyType.SOCKS5 if protocol == 'socks5' else ProxyType.SOCKS4
                
                connector = ProxyConnector(
                    proxy_type=proxy_type,
                    host=ip,
                    port=port,
                    username=login,
                    password=password,
                    rdns=True,
                    verify_ssl=False
                )
            else:
                if login and password:
                    proxy_url = f"http://{login}:{password}@{ip}:{port}"
                else:
                    proxy_url = f"http://{ip}:{port}"
                connector = aiohttp.TCPConnector(ssl=False)
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout, connector=connector) as session:
                async with session.get(
                    self.API_URL,
                    headers=headers,
                    proxy=proxy_url if proxy_url else None
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = {
                            "valid": True,
                            "username": data.get("username", "Unknown"),
                            "user_id": str(data.get("id", "")),
                            "email": data.get("email"),
                            "phone": data.get("phone"),
                            "discriminator": data.get("discriminator", "0"),
                            "nitro": self._parse_nitro(data.get("premium_type", 0)),
                            "guilds_count": 0,
                            "dm_channels_count": 0,
                            "error": None
                        }
                        
                        if detailed:
                            guilds_count = await self._fetch_guilds_count(session, headers, proxy_url)
                            dm_count = await self._fetch_dm_channels_count(session, headers, proxy_url)
                            result["guilds_count"] = guilds_count
                            result["dm_channels_count"] = dm_count
                        
                        return result
                    elif response.status == 429:
                        await asyncio.sleep(2)
                        return await self.check_token(token, proxy, detailed)
                    else:
                        return {
                            "valid": False,
                            "error": f"HTTP {response.status}"
                        }
        except asyncio.TimeoutError:
            return {"valid": False, "error": "Timeout"}
        except Exception as e:
            return {"valid": False, "error": f"{type(e).__name__}: {str(e)[:50]}"}
    
    async def _fetch_guilds_count(self, session: aiohttp.ClientSession, headers: dict, proxy_url: Optional[str] = None) -> int:
        try:
            async with session.get(self.GUILDS_URL, headers=headers, proxy=proxy_url) as response:
                if response.status == 200:
                    guilds = await response.json()
                    return len(guilds) if isinstance(guilds, list) else 0
                return 0
        except:
            return 0
    
    async def _fetch_dm_channels_count(self, session: aiohttp.ClientSession, headers: dict, proxy_url: Optional[str] = None) -> int:
        try:
            async with session.get(self.CHANNELS_URL, headers=headers, proxy=proxy_url) as response:
                if response.status == 200:
                    channels = await response.json()
                    return len(channels) if isinstance(channels, list) else 0
                return 0
        except:
            return 0
    
    def _parse_nitro(self, premium_type: int) -> str:
        nitro_types = {
            0: "None",
            1: "Classic",
            2: "Full",
            3: "Basic"
        }
        return nitro_types.get(premium_type, "Unknown")
