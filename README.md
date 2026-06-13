# Claude Code Primer

A comprehensive, hands-on guide to mastering [Claude Code](https://claude.ai/code) — Anthropic's agentic coding tool — from first install through production-grade multi-agent orchestration.

## What's Inside

The guide ([docs/claude_code_complete_guide.md](docs/claude_code_complete_guide.md)) is structured as a progressive learning path across five parts, with mini-projects, quizzes, and a full capstone at the end.

---

### Part I — Beginner: Foundations

- What Claude Code is and how it differs from code-completion tools
- Installation, environment setup, and authentication
- Core commands and the interaction model
- The permission system
- **Mini-Project:** Scaffold a Python CLI tool

### Part II — Intermediate: Configuration & Customization

- `CLAUDE.md` — teaching Claude your project conventions
- Context management and session strategy
- The Skills system: reusable slash-command workflows
- The Hook system: deterministic pre/post-action automation
- **Mini-Project:** Build a custom development environment

### Part III — Advanced: Integration & Programmatic Control

- MCP (Model Context Protocol): connecting Claude to external systems
- The Python Agent SDK
- Multi-turn workflows and CI/CD automation
- Memory deep dive: persistence, context, and session management
- **Mini-Project:** Build an automated code review pipeline

### Part IV — Expert: Multi-Agent Orchestration

- Subagents: delegation and isolation
- Background agents and parallel execution
- Agent teams: collaborative multi-agent systems
- **Mini-Project:** Parallel security audit system

### Part V — Capstone: Multi-Agent Development System

A complete implementation of a 4-agent development team with persistent memory, distinct agent personalities, and a full orchestration engine.

---

## Appendices

| Appendix | Contents |
| -------- | -------- |
| A | Claude Design — the visual frontier |
| B | Quick reference card |
| C | Quiz answer key |
| D | Pro tips and power patterns |

---

## Who This Is For

Developers who want to move beyond ad-hoc prompting and build real, repeatable workflows with Claude Code. The guide assumes programming familiarity (Python examples throughout) but no prior experience with Claude Code or agent frameworks.

## License

[MIT](LICENSE)
