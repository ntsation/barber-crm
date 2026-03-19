"""Tests for logging configuration edge cases."""
import logging
import pytest

from app.core.logging import setup_logging


class TestSetupLoggingEdgeCases:
    """Tests for setup_logging edge cases."""

    def test_setup_logging_invalid_format_type_defaults_to_structured(self, capsys):
        """Test that invalid format_type defaults to structured formatter."""
        setup_logging(level="INFO", format_type="invalid_type")
        logger = logging.getLogger("test_invalid_format")
        
        logger.info("Test message with invalid format")
        
        # Capture stdout
        captured = capsys.readouterr()
        output = captured.out
        
        # Should use structured format (contains = signs)
        assert "message=Test message" in output
