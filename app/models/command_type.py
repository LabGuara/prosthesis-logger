from __future__ import annotations
from enum import IntEnum


class CommandType(IntEnum):
    GAIT_MODE = 1
    POWER = 2
    ACTUATOR_CURRENT = 3

    @staticmethod
    def parse_type(value: int) -> CommandType | None:
        try:
            return CommandType(value)
        except ValueError:
            return None
