"""my_module — example module scaffolded by new-py-module skill."""

from __future__ import annotations

import structlog

log = structlog.get_logger(__name__)


class MyModule:
    """Processes a value and returns it.

    Args:
        value: The string value to process.
    """

    def __init__(self, value: str) -> None:
        """Initialize with a string value."""
        self._value = value

    def run(self) -> str:
        """Process the value and return it.

        Returns:
            The stored string value.

        Raises:
            ValueError: If value is not a valid string.
        """
        log.info("my_module.run", value=self._value)
        return self._value
