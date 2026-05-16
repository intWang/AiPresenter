import logging

SECRET_PREFIXES = ("sk-", "rk-", "pk-")


def redact_value(value: object) -> object:
    if isinstance(value, str) and value.startswith(SECRET_PREFIXES):
        return "***REDACTED***"
    return value


def elapsed_ms(start: float, end: float) -> float:
    return round((end - start) * 1000, 2)


def log_timed_event(
    logger: logging.Logger,
    event: str,
    *,
    duration_ms: float,
    status: str,
    **fields: object,
) -> None:
    parts = [event, f"status={status}", f"duration_ms={duration_ms:.2f}"]
    for key, value in fields.items():
        if value is None:
            continue
        parts.append(f"{key}={redact_value(value)}")
    logger.info(" ".join(parts))


def configure_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logging.getLogger("ai_presenter").setLevel(level)
