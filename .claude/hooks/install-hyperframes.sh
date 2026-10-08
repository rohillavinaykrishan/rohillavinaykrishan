#!/bin/bash
# Installs the HyperFrames CLI, its agent skills, and the headless Chrome it
# renders with. Runs only in Claude Code cloud sessions (containers are fresh).
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

if ! command -v hyperframes >/dev/null 2>&1; then
  npm install -g hyperframes@latest >/dev/null 2>&1
fi

# Core skills -> ~/.claude/skills (the router installs workflows on demand).
hyperframes skills update >/dev/null 2>&1 || true

# Chrome Headless Shell for local rendering.
hyperframes browser ensure >/dev/null 2>&1 || true

echo "HyperFrames $(hyperframes --version) ready."
