---
name: block-dangerous-rm
enabled: true
event: bash
pattern: rm\s+.*(-[a-zA-Z]*[rR][a-zA-Z]*|--r[a-z]+|[*?\[])
action: block
---

**Blocked: dangerous rm command detected.**

This command matches one or more high-risk patterns:
- Recursive flag (`-r`, `-R`, `-rf`, `-fr`, etc.) — deletes entire directory trees
- `--recursive` long flag
- Glob characters (`*`, `?`, `[`) — may match far more files than intended

Do not proceed. If you need to delete files, ask the user to confirm the exact paths and run the command themselves.
