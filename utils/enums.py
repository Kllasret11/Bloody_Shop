from enum import Enum

__all__ = (
    'LogLevel',
)


class LogLevel(Enum):
    Info = 'INFO'
    Exception = 'EXCEPTION'
    Success = 'SUCCESS'
