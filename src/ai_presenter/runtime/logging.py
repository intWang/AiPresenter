import logging

SECRET_PREFIXES = ("sk-", "rk-", "pk-")


def redact_value(value: object) -> object:
    if isinstance(value, str) and value.startswith(SECRET_PREFIXES):
        return "***REDACTED***"
    return value


def configure_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logging.getLogger("ai_presenter").setLevel(level)
