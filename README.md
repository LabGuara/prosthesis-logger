# Prosthesis MQTT Terminal Logger

A Python terminal app that follows the prosthesis' MQTT traffic and renders it as colored log
lines with timestamps:

- sensor readings (`prosthesis/logs/validated`), one line per reading;
- commands sent from the app (`prosthesis/actions/validated`);
- command feedback from the prosthesis (`prosthesis/actions/feedback/validated`).

## Levels

Messages carry no level of their own; the logger derives one for display:

- `ERROR`: a command the prosthesis failed to carry out (feedback with `status` `failure`);
- `INFO`: everything else.

Filtering by `ERROR` therefore shows only failed commands.

## Run

```bash
python -m app.main --mqtt_broker localhost --mqtt_port 1883
```

Optional flags:

- `--mqtt_logs_topic`, `--mqtt_command_logs_topic`, `--mqtt_command_feedback_topic`
- `--mqtt_username`, `--mqtt_password`
- `--min-log-level INFO|ERROR`
- `--sensor-names Prosthesis,Action,Feedback`

No filters are applied if you omit the filter flags.

## Runtime controls

- `h` show shortcuts help
- `1` show everything (minimum level `INFO`)
- `2` show only failed commands (minimum level `ERROR`)
- `n` set sensor name filter (comma separated: `Prosthesis`, `Action`, `Feedback`)
- `c` clear all filters
- `q` quit

## Env fallback

You can use `.env` variables:

- `MQTT_HOST`
- `MQTT_PORT`
- `MQTT_USERNAME`
- `MQTT_PASSWORD`
- `MQTT_TLS`
- `MQTT_LOGS_VALIDATED_TOPIC`
- `MQTT_COMMAND_LOGS_VALIDATED_TOPIC`
- `MQTT_POWER_FEEDBACK_VALIDATED_TOPIC`
- `MQTT_QOS`
- `MQTT_CLIENT_ID`
- `MIN_LOG_LEVEL`

CLI values override env values.
