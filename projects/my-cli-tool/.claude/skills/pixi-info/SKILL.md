---
name: pixi-info
description: Run pixi environment diagnostics. Use this skill when the user asks about their pixi version, pixi environment info, or pixi config — including any combination of "pixi info", "pixi version", "pixi config", or "show me pixi settings".
---

# Pixi Info

Run the following five commands in sequence and display all output to the user:

1. `pixi --version`
2. `pixi info`
3. `pixi config list --local`
4. `pixi config list --global`
5. `pixi config list --system`

Run commands 1 and 2 in parallel (no dependencies), then run commands 3, 4, and 5 in parallel after those complete.

Present the output of each command under a clear heading so the user can easily distinguish them.
