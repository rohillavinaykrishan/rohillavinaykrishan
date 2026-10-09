#!/bin/bash
# Installs the HyperFrames CLI, its agent skills, and the headless Chrome it
# renders with. Runs only in Claude Code cloud sessions (containers are fresh).
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# FFmpeg/FFprobe for rendering, audio extraction and compositing; Blender for
# headless node compositing and scene export (python3-numpy is its FBX
# exporter's dependency); COLMAP for camera solves (matchmove skill).
apt_pkgs=()
if ! command -v ffmpeg >/dev/null 2>&1 || ! command -v ffprobe >/dev/null 2>&1; then
  apt_pkgs+=(ffmpeg)
fi
if ! command -v blender >/dev/null 2>&1; then
  apt_pkgs+=(blender)
fi
if ! dpkg -s python3-numpy >/dev/null 2>&1; then
  apt_pkgs+=(python3-numpy)
fi
if ! command -v colmap >/dev/null 2>&1; then
  apt_pkgs+=(colmap)
fi
if [ ${#apt_pkgs[@]} -gt 0 ]; then
  (apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "${apt_pkgs[@]}") >/dev/null 2>&1 || true
fi

# OpenCV for the matchmove pipeline (masks, QC overlay).
if ! python3 -c "import cv2" >/dev/null 2>&1; then
  pip install -q opencv-python-headless >/dev/null 2>&1 || true
fi

if ! command -v hyperframes >/dev/null 2>&1; then
  npm install -g hyperframes@latest >/dev/null 2>&1
fi

# Core skills -> ~/.claude/skills (the router installs workflows on demand).
hyperframes skills update >/dev/null 2>&1 || true

# Chrome Headless Shell for local rendering.
hyperframes browser ensure >/dev/null 2>&1 || true

echo "HyperFrames $(hyperframes --version) ready. $(ffmpeg -version 2>/dev/null | head -1 | cut -d' ' -f1-3 || echo 'ffmpeg missing'). $(blender --version 2>/dev/null | head -1 || echo 'Blender missing'). $(command -v colmap >/dev/null 2>&1 && echo 'COLMAP ready' || echo 'COLMAP missing')."
