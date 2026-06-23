# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Context

This project is part of the `projects/` mono-repo in the Claude Code Mastery Guide. It contains hands-on examples for Parts IV and V of the guide — multi-agent orchestration, subagent delegation, background agents, and agent teams.

The global CLAUDE.md (two levels up) governs the toolchain, commit conventions, CI gate, and test requirements. This file only documents what differs or is specific to this project.

## Commands

```sh
pixi run test                    # unit tests only
pixi run test-integration        # integration tests only
pixi run ci                      # full gate: fmt → lint → check → cov

# Run a single test by node ID
pixi run -- pytest tests/unit/test_foo.py::test_bar -v
```

## Agent SDK

The primary dependency is `claude-agent-sdk`. When writing examples:

- Always pass `model` explicitly when spawning agents — never rely on SDK defaults, since readers need to see the model selection.
- Pin `claude-agent-sdk` to an explicit upper bound in `pixi.toml` if the agent API surface changes during active development.
- Integration tests that make live API calls must be marked `@pytest.mark.integration` and must not run in `pixi run test`.
