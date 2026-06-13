# Module and Test Templates

Replace all `<angle-bracket>` tokens before writing the file. Never leave placeholder names in generated output.

---

## Module template

```python
"""<module_name> — <one-line description of what this module does>."""

from __future__ import annotations

import structlog

log = structlog.get_logger(__name__)


class <ClassName>:
    """<One-line summary ending with a period.>

    Args:
        value: <What this argument represents.>
    """

    def __init__(self, value: str) -> None:
        self._value = value

    def run(self) -> str:
        """<One-line summary ending with a period.>

        Returns:
            <What is returned.>

        Raises:
            ValueError: If <condition that would cause this>.
        """
        log.info("<module_name>.run", value=self._value)
        return self._value
```

**Conventions enforced by this template:**
- `from __future__ import annotations` for deferred evaluation — always first import
- `structlog.get_logger(__name__)` at module level — never `logging.getLogger`
- No `print()` anywhere
- All public methods have return type annotations
- Google-style docstrings on the class and every public method
- Bare `except:` is forbidden; catch specific types or let exceptions propagate

---

## Unit test template

```python
"""Unit tests for <module_name>."""

from __future__ import annotations

import pytest

from <package>.<module_name> import <ClassName>


class Test<ClassName>:
    def test_run_returns_value(self) -> None:
        obj = <ClassName>("hello")
        assert obj.run() == "hello"

    def test_run_with_empty_string(self) -> None:
        obj = <ClassName>("")
        assert obj.run() == ""
```

**Conventions enforced by this template:**
- Tests grouped in a class named `Test<ClassName>` — no `test_` prefix needed on the class itself under pytest
- No mocking of the filesystem — use `tmp_path` if I/O is needed
- Each test name describes the behaviour being verified, not the method name
- No `@pytest.mark.skip` or `@pytest.mark.xfail` without a comment linking to an open issue

---

## Integration test template

```python
"""Integration tests for <module_name>."""

from __future__ import annotations

import pytest

from <package>.<module_name> import <ClassName>


@pytest.mark.integration
class Test<ClassName>Integration:
    def test_end_to_end(self, tmp_path: pytest.TempPathFactory) -> None:
        # TODO: exercise the real resource this module depends on
        # (filesystem, network endpoint, database — not a mock)
        obj = <ClassName>("integration")
        result = obj.run()
        assert result == "integration"
```

**Conventions enforced by this template:**
- Every test in this file carries `@pytest.mark.integration` on the class (applies to all methods)
- Use `tmp_path` for filesystem, real DB instances for database code, `respx` for HTTP interception
- Each test must leave resources in the state it found them — use setup/teardown or transactions that roll back
