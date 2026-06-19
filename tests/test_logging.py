"""Tests for src.utils.logging."""

import logging

from src.utils.logging import get_logger, setup_logging


class TestGetLogger:
    def test_returns_logger_instance(self) -> None:
        lg = get_logger("test.module")
        assert isinstance(lg, logging.Logger)
        assert lg.name == "test.module"

    def test_same_name_returns_same_logger(self) -> None:
        a = get_logger("test.same")
        b = get_logger("test.same")
        assert a is b

    def test_different_names_return_different_loggers(self) -> None:
        a = get_logger("test.one")
        b = get_logger("test.two")
        assert a is not b


class TestSetupLogging:
    def test_setup_is_idempotent(self) -> None:
        setup_logging(level=logging.WARNING)
        setup_logging(level=logging.DEBUG)
        root = logging.getLogger()
        assert root.level in (logging.WARNING, logging.INFO)

    def test_logger_can_log_without_error(self) -> None:
        lg = get_logger("test.log_output")
        lg.info("This should not raise")
