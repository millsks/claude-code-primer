"""Unit tests for my_module."""

from __future__ import annotations

from skills_work.my_module import MyModule


class TestMyModule:
    """Tests for MyModule."""

    def test_run_returns_value(self) -> None:
        """run() returns the value passed at construction."""
        obj = MyModule("hello")
        assert obj.run() == "hello"

    def test_run_with_empty_string(self) -> None:
        """run() returns an empty string when constructed with one."""
        obj = MyModule("")
        assert obj.run() == ""
