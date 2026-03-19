"""Tests for logging configuration."""
import logging
import pytest

from app.core.logging import setup_logging, get_logger, StructuredFormatter


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_info_level(self):
        """Test setting up logging with INFO level."""
        setup_logging(level="INFO", format_type="simple")
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

    def test_setup_logging_debug_level(self):
        """Test setting up logging with DEBUG level."""
        setup_logging(level="DEBUG", format_type="simple")
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

    def test_setup_logging_warning_level(self):
        """Test setting up logging with WARNING level."""
        setup_logging(level="WARNING", format_type="simple")
        root_logger = logging.getLogger()
        assert root_logger.level == logging.WARNING

    def test_setup_logging_invalid_level_defaults_to_info(self):
        """Test that invalid level defaults to INFO."""
        setup_logging(level="INVALID", format_type="simple")
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a Logger instance."""
        logger = get_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_get_logger_same_name_same_instance(self):
        """Test that get_logger returns same instance for same name."""
        logger1 = get_logger("same_name")
        logger2 = get_logger("same_name")
        assert logger1 is logger2


class TestStructuredFormatter:
    """Tests for StructuredFormatter."""

    def test_structured_formatter_basic(self):
        """Test basic log formatting."""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(record)
        assert "timestamp=" in formatted
        assert "level=INFO" in formatted
        assert "logger=test" in formatted
        assert "message=Test message" in formatted

    def test_structured_formatter_with_extra_fields(self):
        """Test log formatting with extra fields."""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.request_id = "test-123"
        record.user_id = "user-456"
        record.path = "/test"
        record.method = "GET"
        record.status_code = 200
        record.duration_ms = 100.5
        
        formatted = formatter.format(record)
        assert "request_id=test-123" in formatted
        assert "user_id=user-456" in formatted
        assert "path=/test" in formatted
        assert "method=GET" in formatted
        assert "status_code=200" in formatted
        assert "duration_ms=100.5" in formatted

    def test_structured_formatter_with_exception(self):
        """Test log formatting with exception."""
        formatter = StructuredFormatter()
        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="",
                lineno=0,
                msg="Error occurred",
                args=(),
                exc_info=exc_info,
            )
            formatted = formatter.format(record)
            assert "exception=" in formatted
            assert "Test exception" in formatted
