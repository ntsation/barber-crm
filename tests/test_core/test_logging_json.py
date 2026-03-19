"""Tests for JSON logging formatter."""
import json
import logging
import pytest

from app.core.logging import setup_logging


class TestJSONFormatter:
    """Tests for JSON formatter."""

    def test_json_formatter_output(self, capsys):
        """Test JSON formatter outputs valid JSON."""
        setup_logging(level="INFO", format_type="json")
        logger = logging.getLogger("test_json_direct")
        
        logger.info("Test JSON message")
        
        # Capture stdout
        captured = capsys.readouterr()
        output = captured.out
        
        # Should be valid JSON
        assert "Test JSON message" in output
        # Verify it contains expected fields
        assert "timestamp" in output
        assert "level" in output
        assert "logger" in output
        assert "message" in output

    def test_json_formatter_with_exception(self, capsys):
        """Test JSON formatter with exception includes exception info."""
        setup_logging(level="ERROR", format_type="json")
        logger = logging.getLogger("test_json_exc_direct")
        
        try:
            raise ValueError("Test JSON exception")
        except ValueError:
            logger.exception("Error occurred")
        
        # Capture stdout
        captured = capsys.readouterr()
        output = captured.out
        
        # Should contain exception info
        assert "Error occurred" in output
        assert "Test JSON exception" in output
