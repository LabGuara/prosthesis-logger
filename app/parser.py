from __future__ import annotations
import json
from datetime import datetime

from app.models.command_type import CommandType
from app.models.gait_mode import GaitMode
from app.models.log_level import LogLevel
from app.models.power_state import PowerState
from app.models.sensor_event import ParseError, SensorEvent


ParsedResult = tuple[list[SensorEvent], ParseError | None]

MINIMUM_ACTUATOR_CURRENT = 3000
MAXIMUM_ACTUATOR_CURRENT = 15000


def parse_event_payload(
    topic: str,
    payload: str,
    command_topic: str,
    command_feedback_topic: str,
) -> ParsedResult:
    if topic == command_topic:
        return _parse_command(topic, payload)
    if topic == command_feedback_topic:
        return _parse_command_feedback(topic, payload)
    return _parse_sensor_batch(topic, payload)


def _error(reason: str, topic: str, payload: str) -> ParsedResult:
    return [], ParseError(
        reason=reason,
        topic=topic,
        raw_payload=payload,
        timestamp=datetime.now(),
    )


def _load_object(topic: str, payload: str, what: str) -> tuple[dict | None, ParsedResult | None]:
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as exc:
        return None, _error(f"invalid {what} json: {exc.msg}", topic, payload)

    if not isinstance(parsed, dict):
        return None, _error(f"{what} must be a json object", topic, payload)

    return parsed, None


def _parse_sensor_batch(topic: str, payload: str) -> ParsedResult:
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as exc:
        return _error(f"invalid json: {exc.msg}", topic, payload)

    if isinstance(parsed, dict) and isinstance(parsed.get("value"), list):
        readings = parsed["value"]
    elif isinstance(parsed, list):
        readings = parsed
    else:
        return _error("expected an array of readings or an object with a 'value' array", topic, payload)

    return _parse_sensor_readings(readings, topic, payload, datetime.now())


def _parse_command(topic: str, payload: str) -> ParsedResult:
    parsed, failure = _load_object(topic, payload, "command")
    if failure is not None:
        return failure
    assert parsed is not None

    command_type = _read_int(parsed, "command_type")
    value = _read_int(parsed, "value")
    if command_type is None or value is None:
        return _error("command must have integer fields command_type and value", topic, payload)

    match CommandType.parse_type(command_type):
        case CommandType.GAIT_MODE:
            gait_mode = GaitMode.parse_mode(value)
            if gait_mode is None:
                return _error(f"invalid gait mode; expected 1-9 and got: {value}", topic, payload)
            message = f"Gait mode changed to {gait_mode.label}({value})."
        case CommandType.POWER:
            power_state = PowerState.parse_state(value)
            if power_state is None:
                return _error(f"invalid power state; expected 1 or 2 and got: {value}", topic, payload)
            message = f"Power state changed to {power_state.label}({value})."
        case CommandType.ACTUATOR_CURRENT:
            if not MINIMUM_ACTUATOR_CURRENT <= value <= MAXIMUM_ACTUATOR_CURRENT:
                return _error(
                    "invalid actuator current; expected "
                    f"{MINIMUM_ACTUATOR_CURRENT}-{MAXIMUM_ACTUATOR_CURRENT} and got: {value}",
                    topic,
                    payload,
                )
            message = f"Actuator current changed to {value} mA."
        case _:
            return _error(f"invalid command_type; expected 1, 2 or 3 and got: {command_type}", topic, payload)

    command_id = _read_int(parsed, "command_id")
    if command_id is not None:
        message = f"#{command_id} {message}"

    return (
        [SensorEvent(
            level=LogLevel.INFO,
            sensor_name="Action",
            message=message,
            timestamp=datetime.now(),
            topic=topic,
        )],
        None,
    )


def _parse_command_feedback(topic: str, payload: str) -> ParsedResult:
    parsed, failure = _load_object(topic, payload, "feedback")
    if failure is not None:
        return failure
    assert parsed is not None

    command = parsed.get("command")
    status = parsed.get("status")
    state = parsed.get("state")
    message = parsed.get("message")
    if not all(isinstance(field, str) for field in (command, status, state, message)):
        return _error("feedback must have string fields command, status, state and message", topic, payload)
    if status not in ("success", "failure"):
        return _error(f"invalid status; expected success or failure and got: {status!r}", topic, payload)

    details = [f"state={state}"]
    gait = _read_int(parsed, "gait")
    if gait is not None:
        gait_mode = GaitMode.parse_mode(gait)
        details.append(f"gait={gait_mode.label if gait_mode else gait}")
    current = _read_int(parsed, "current")
    if current is not None:
        details.append(f"current={current} mA")

    command_id = _read_int(parsed, "command_id")
    source = f"#{command_id} " if command_id is not None else ""
    if parsed.get("origin") == "internal":
        source = "internal "

    return (
        [SensorEvent(
            level=LogLevel.INFO if status == "success" else LogLevel.ERROR,
            sensor_name="Feedback",
            message=f"{source}{command} {status} ({', '.join(details)}): {message}",
            timestamp=datetime.now(),
            topic=topic,
        )],
        None,
    )


def _read_int(payload: dict, key: str) -> int | None:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _parse_sensor_readings(
    readings: list,
    topic: str,
    payload: str,
    now: datetime,
) -> ParsedResult:
    if not readings:
        return _error("readings array is empty", topic, payload)

    for index, reading in enumerate(readings):
        if not isinstance(reading, dict):
            return _error(f"reading at index {index} must be an object", topic, payload)

    events = [
        SensorEvent(
            level=LogLevel.INFO,
            sensor_name="Prosthesis",
            message=" ".join(f"{key}={value}" for key, value in reading.items()),
            timestamp=now,
            topic=topic,
        )
        for reading in readings
    ]

    return events, None
