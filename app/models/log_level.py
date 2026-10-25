from __future__ import annotations
from enum import IntEnum


class LogLevel(IntEnum):
    """Display level, derived by the logger: messages carry no level of their own.
    ERROR is a command the prosthesis failed to carry out; everything else is INFO."""

    INFO = 1
    ERROR = 2

    @staticmethod
    def parse_level(value: str) -> LogLevel | None:
        try:
            return LogLevel[value.strip().upper()]
        except KeyError:
            return None
