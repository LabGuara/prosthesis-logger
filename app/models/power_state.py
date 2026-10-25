from __future__ import annotations
from enum import IntEnum


class PowerState(IntEnum):
    ON = (1, "On")
    OFF = (2, "Off")

    label: str

    def __new__(cls, value: int, label: str) -> PowerState:
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    @staticmethod
    def parse_state(value: int) -> PowerState | None:
        try:
            return PowerState(value)
        except ValueError:
            return None