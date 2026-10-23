#!/bin/bash
# Installs the inference.sh CLI (belt) used by the ai-video-generation skill.
# Run `belt login` once per session to authenticate.
set -uo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

command -v belt >/dev/null || npm i -g @inferencesh/belt >/tmp/belt-install.log 2>&1 || true
echo "belt: $(belt --version 2>&1 || echo 'install failed, see /tmp/belt-install.log')"
