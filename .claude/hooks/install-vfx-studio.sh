#!/bin/bash
# Installs the free VFX Studio toolkit in Claude Code cloud sessions.
# Core tools (Blender, Krita, GIMP, Inkscape, COLMAP...) install now (~1.5 min);
# the AI tools (~3 min) install in the background so the session starts sooner.
# Progress: /tmp/vfx-ai-install.log; done when /opt/vfx-ai/.ready exists.
set -uo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

TOOLS="$CLAUDE_PROJECT_DIR/tools/vfx"
"$TOOLS/install.sh" core >/tmp/vfx-core-install.log 2>&1 || true

if [ ! -f /opt/vfx-ai/.ready ]; then
  setsid nohup "$TOOLS/install.sh" ai >/tmp/vfx-ai-install.log 2>&1 < /dev/null &
  ai_status="AI tools installing in background"
else
  ai_status="AI tools ready"
fi

echo "VFX Studio: $(blender --version 2>/dev/null | head -1 || echo 'Blender missing'); $ai_status."
