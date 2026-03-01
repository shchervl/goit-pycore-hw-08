"""Tests for handlers/general.py — hello and help commands."""

import handlers  # noqa: F401 — ensures all @command decorators run before help_cmd is tested
from handlers.general import hello_cmd, help_cmd


class TestHelloCmd:
    def test_returns_non_empty_greeting(self, book):
        result = hello_cmd([], book)
        assert result and len(result.strip()) > 0

    def test_greeting_message_is_exact(self, book):
        assert "How can I help you?" in hello_cmd([], book)


class TestHelpCmd:
    def test_returns_non_empty_table(self, book):
        result = help_cmd([], book)
        assert result and len(result.strip()) > 0

    def test_table_contains_known_commands(self, book):
        result = help_cmd([], book)
        assert "add" in result
        assert "phone" in result
        assert "birthdays" in result

    def test_table_contains_usage_descriptions(self, book):
        # Each usage string contains "<name>" argument placeholders
        result = help_cmd([], book)
        assert "<" in result
