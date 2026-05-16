import logging

import pytest

from ai_presenter.runtime.logging import configure_logging, elapsed_ms, log_timed_event, redact_value


def test_redact_value_masks_secret_like_values() -> None:
    assert redact_value("sk-test-secret") == "***REDACTED***"
    assert redact_value("rk-test-secret") == "***REDACTED***"
    assert redact_value("normal-profile-name") == "normal-profile-name"


def test_configure_logging_sets_ai_presenter_level() -> None:
    configure_logging(debug=False)

    assert logging.getLogger("ai_presenter").level == logging.INFO


def test_configure_logging_sets_debug_level() -> None:
    configure_logging(debug=True)

    assert logging.getLogger("ai_presenter").level == logging.DEBUG


def test_elapsed_ms_returns_milliseconds() -> None:
    assert elapsed_ms(1.25, 1.5) == 250.0


def test_log_timed_event_redacts_secret_fields(caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("ai_presenter.test.telemetry")

    with caplog.at_level(logging.INFO, logger="ai_presenter.test.telemetry"):
        log_timed_event(
            logger,
            "demo_event",
            duration_ms=12.34,
            status="ok",
            api_key="sk-secret",
            package="demo",
            omitted=None,
        )

    message = caplog.records[-1].getMessage()
    assert "demo_event" in message
    assert "duration_ms=12.34" in message
    assert "status=ok" in message
    assert "api_key=***REDACTED***" in message
    assert "sk-secret" not in message
    assert "omitted=" not in message
