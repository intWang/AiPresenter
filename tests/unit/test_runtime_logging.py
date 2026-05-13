import logging

from ai_presenter.runtime.logging import configure_logging, redact_value


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
