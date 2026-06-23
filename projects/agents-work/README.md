# agents-work

Hands-on examples for Parts IV and V of the [Claude Code Mastery Guide](../../docs/claude_code_complete_guide.md) — multi-agent orchestration, subagent delegation, background agents, agent teams, and the capstone multi-agent development system.

## Installation

```sh
pixi install
pixi run bootstrap   # installs pre-commit hooks
```

## Development

```sh
pixi run test                    # unit tests
pixi run test-integration        # integration tests
pixi run ci                      # full gate: fmt → lint → check → cov

# Run a single test
pixi run -- pytest tests/unit/test_foo.py::test_bar -v
```

## License

[MIT](../../LICENSE)
