import asyncio
import sys
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from src.core.database import Database
from src.core.token_checker import TokenChecker


NITRO_MAP = {"None": 0, "Classic": 1, "Full": 2, "Basic": 3}

ERROR_PATTERNS = [
    (("clientconnectorerror", "cannot connect to host"), "Connection Error"),
    (("proxyconnectionerror", "couldn't connect to proxy"), "Proxy Error"),
    (("timeout",), "Timeout"),
    (("unauthorized", "401"), "Invalid Token"),
    (("forbidden", "403"), "Forbidden"),
    (("rate limit", "429"), "Rate Limited"),
    (("ssl",), "SSL Error"),
]


def _shorten_error(error: str) -> str:
    lower = error.lower()
    for needles, label in ERROR_PATTERNS:
        if any(n in lower for n in needles):
            return label
    return error[:30] + ("..." if len(error) > 30 else "")


def _proxy_row_to_dict(row) -> dict:
    return {
        "id": row[0] if len(row) > 0 else None,
        "ip": row[1] if len(row) > 1 else None,
        "port": row[2] if len(row) > 2 else None,
        "protocol": row[3] if len(row) > 3 else "http",
        "login": row[4] if len(row) > 4 and row[4] else None,
        "password": row[5] if len(row) > 5 and row[5] else None,
    }


class AccountCheckWorker(QThread):
    progress_signal = pyqtSignal(int, int)
    log_signal = pyqtSignal(str, str)
    finished_signal = pyqtSignal(dict)

    def __init__(self, tokens: list, proxies: list, max_workers: int,
                 detailed: bool = False, parent=None):
        super().__init__(parent)
        self.tokens = tokens
        self.proxies = proxies
        self.max_workers = max_workers
        self.detailed = detailed
        self.should_stop = False
        self._loop: asyncio.AbstractEventLoop | None = None
        self._tasks: list[asyncio.Task] = []

        self.db = Database()
        self.checker = TokenChecker(timeout=10)
        self.output_dir = Path("checks") / datetime.now().strftime("%d.%m.%Y_%H-%M")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.valid_tokens: list[str] = []
        self.invalid_tokens: list[str] = []
        self.stats = {"total": len(tokens), "valid": 0, "invalid": 0}

    def stop(self):
        self.should_stop = True
        if self._loop and not self._loop.is_closed():
            self._loop.call_soon_threadsafe(self._cancel_tasks)

    def _cancel_tasks(self):
        for task in self._tasks:
            task.cancel()

    def run(self):
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._loop = loop
        try:
            loop.run_until_complete(self._dispatch())
            self._save_results()
            self.finished_signal.emit(self.stats)
        except Exception:
            return
        finally:
            self._loop = None
            loop.close()

    async def _dispatch(self):
        semaphore = asyncio.Semaphore(self.max_workers)
        self._tasks = [
            asyncio.ensure_future(self._check(semaphore, token, self._proxy_for(i)))
            for i, token in enumerate(self.tokens)
        ]
        await asyncio.gather(*self._tasks, return_exceptions=True)

    def _proxy_for(self, index: int) -> dict | None:
        if not self.proxies:
            return None
        return _proxy_row_to_dict(self.proxies[index % len(self.proxies)])

    async def _check(self, semaphore: asyncio.Semaphore, token: str, proxy: dict | None):
        async with semaphore:
            if self.should_stop:
                return

            result = await self.checker.check_token(token, proxy, self.detailed)

            if result.get("valid"):
                self._on_valid(token, result, proxy)
            else:
                self._on_invalid(token, result.get("error"))

            self.progress_signal.emit(
                len(self.valid_tokens) + len(self.invalid_tokens),
                self.stats["total"],
            )

    def _on_valid(self, token: str, result: dict, proxy: dict | None):
        self.stats["valid"] += 1
        self.valid_tokens.append(token)

        guilds = result.get("guilds_count", 0)
        dms = result.get("dm_channels_count", 0)

        try:
            self.db.save_account(
                token=token,
                username=result.get("username", "Unknown"),
                user_id=result.get("user_id", ""),
                email=result.get("email"),
                phone=result.get("phone"),
                discriminator=result.get("discriminator", "0"),
                nitro=NITRO_MAP.get(result.get("nitro", "None"), 0),
                proxy_id=proxy["id"] if proxy else None,
                guilds_count=guilds,
                dm_channels_count=dms,
            )
        except Exception as exc:
            self.log_signal.emit(f"Ошибка сохранения: {exc}", "red")

        message = f"{token} | Valid | Nitro: {result.get('nitro', 'None')}"
        if self.detailed:
            message += f" | Серверов: {guilds} | Чатов: {dms}"
        self.log_signal.emit(message, "green")

    def _on_invalid(self, token: str, error: str | None):
        self.stats["invalid"] += 1
        self.invalid_tokens.append(token)

        message = f"{token} | INVALID"
        if error:
            message += f" ({_shorten_error(error)})"
        self.log_signal.emit(message, "red")

    def _save_results(self):
        if self.valid_tokens:
            (self.output_dir / "valid.txt").write_text("\n".join(self.valid_tokens), encoding="utf-8")
        if self.invalid_tokens:
            (self.output_dir / "invalid.txt").write_text("\n".join(self.invalid_tokens), encoding="utf-8")
