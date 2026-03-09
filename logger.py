from __future__ import annotations

import os
from pathlib import Path
from sys import stderr
from typing import Callable, Optional

from loguru import logger

__all__ = ("Logger",)

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = Path(os.getenv("LOGS_DIR", str(BASE_DIR / "logs"))).resolve()
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logger_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<light-green>user_id</light-green>: <white>{extra[user_id]}</white> | "
    "<light-green>message</light-green>: <level>{message}</level>"
)

logger.configure(extra={"user_id": ""})
logger.remove()
logger.add(stderr, format=logger_format)
logger.add(LOGS_DIR / "file_{time}.log", format=logger_format, rotation="5 MB")


class Logger:
    def __init__(self, user_id: Optional[int] = None) -> None:
        self.user_id = user_id
        self.kwargs = {"user_id": user_id}

    def _send_log(self, log_func: Callable, content: str) -> None:
        log_func(content, **self.kwargs)

    def log_error(self, *, content: str, error: Exception | None = None) -> None:
        message = content + ".\n"
        if error:
            message += f"Ошибка: {error}"
        self._send_log(logger.exception, message)

    def log_info(self, *, content: str) -> None:
        self._send_log(logger.info, content)

    def log_success(self, *, content: str) -> None:
        self._send_log(logger.success, content)
