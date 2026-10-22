#!/bin/bash
# Installs the Python packages the agent swarm needs (tools/agent-swarm) in
# Claude Code cloud sessions: numpy, eth-account (blockchain), ccxt (exchange).
set -uo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

pip install -q -r "$CLAUDE_PROJECT_DIR/tools/agent-swarm/requirements.txt" >/tmp/agent-swarm-install.log 2>&1 \
  && echo "Agent swarm: numpy, eth-account, ccxt ready." \
  || echo "Agent swarm: package install failed, see /tmp/agent-swarm-install.log"
