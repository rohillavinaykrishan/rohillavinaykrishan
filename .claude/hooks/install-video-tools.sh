#!/bin/bash
# Installs video editing / compositing tools for Claude Code cloud sessions:
#   MoviePy, auto-editor, PySceneDetect, faster-whisper, rembg -> /opt/video-tools (venv)
#   Blender LTS (headless compositing)                         -> /opt/blender
# The install runs in the background so the session starts immediately.
# Progress: /tmp/video-tools-install.log; /opt/video-tools/.ready appears when done.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

VENV=/opt/video-tools
BLENDER_SERIES=4.5
BLENDER_VERSION=4.5.14

install() {
  # Own venv: these pins (e.g. moviepy's pillow<12) would otherwise break
  # system Python packages.
  if [ ! -x "$VENV/bin/python" ]; then
    python3 -m venv "$VENV"
  fi
  # av<17: faster-whisper 1.2.1 passes an argument PyAV 17+ no longer accepts.
  "$VENV/bin/pip" install -q \
    moviepy==2.2.1 \
    auto-editor==29.3.1 \
    scenedetect==0.7.1 \
    opencv-python-headless==5.0.0.93 \
    faster-whisper==1.2.1 \
    "av>=16,<17" \
    "rembg[cpu,cli]==2.0.69"

  for bin in auto-editor scenedetect rembg; do
    ln -sf "$VENV/bin/$bin" "/usr/local/bin/$bin"
  done
  # `video-python script.py` runs scripts that import moviepy / faster_whisper / rembg.
  # A wrapper, not a symlink: a symlinked venv python outside bin/ loses the venv.
  printf '#!/bin/sh\nexec %s/bin/python "$@"\n' "$VENV" >/usr/local/bin/video-python
  chmod +x /usr/local/bin/video-python

  if ! command -v blender >/dev/null 2>&1; then
    curl -sSL "https://download.blender.org/release/Blender${BLENDER_SERIES}/blender-${BLENDER_VERSION}-linux-x64.tar.xz" \
      | tar -xJ -C /opt
    ln -sfn "/opt/blender-${BLENDER_VERSION}-linux-x64" /opt/blender
    ln -sf /opt/blender/blender /usr/local/bin/blender
  fi

  touch "$VENV/.ready"
}

if [ -f "$VENV/.ready" ]; then
  echo "Video tools ready."
  exit 0
fi

# flock: a second session start (e.g. resume) must not race the running install.
nohup flock -n /tmp/video-tools-install.lock \
  bash -c "$(declare -f install); VENV=$VENV BLENDER_SERIES=$BLENDER_SERIES BLENDER_VERSION=$BLENDER_VERSION; set -euo pipefail; install" \
  >>/tmp/video-tools-install.log 2>&1 &
echo "Installing video tools in the background (~3 min); see /tmp/video-tools-install.log."
