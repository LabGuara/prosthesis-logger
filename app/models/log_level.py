from __future__ import annotations
from enum import IntEnum


class LogLevel(IntEnum):
    INFO = 1
    ERROR = 2

    @staticmethod
    def parse_level(value: str) -> LogLevel | None:
        try:
            return LogLevel[value.strip().upper()]
        except KeyError:
            return None
