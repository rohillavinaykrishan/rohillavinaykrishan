#!/bin/bash
# Installs the free VFX Studio toolkit (no licenses, no credits, CPU-only).
#   install.sh core   -> apt tools + Blender           (~2-4 min)
#   install.sh ai     -> Python AI venv at /opt/vfx-ai  (~5-8 min)
#   install.sh all    -> both (default)
# Idempotent: re-running skips anything already installed.
set -uo pipefail

MODE="${1:-all}"
BLENDER_VERSION="5.2.2"
BLENDER_SERIES="5.2"
VENV=/opt/vfx-ai
LOG_PREFIX="[vfx-install]"
log() { echo "$LOG_PREFIX $*"; }

install_core() {
  local pkgs=(ffmpeg sox imagemagick krita gimp inkscape colmap fonts-noto-core
              opencolorio-tools xvfb libgl1 libgl1-mesa-dri libegl1 libegl-mesa0 libgles2 libxi6 libxkbcommon0 libsm6 libxrender1)
  local missing=()
  for p in "${pkgs[@]}"; do dpkg -s "$p" >/dev/null 2>&1 || missing+=("$p"); done
  if [ ${#missing[@]} -gt 0 ]; then
    log "apt: ${missing[*]}"
    apt-get -o DPkg::Lock::Timeout=300 update -qq >/dev/null 2>&1
    DEBIAN_FRONTEND=noninteractive apt-get -o DPkg::Lock::Timeout=300 install -y -qq --no-install-recommends "${missing[@]}" >/dev/null 2>&1 \
      || log "WARNING: some apt packages failed"
  fi

  if ! command -v blender >/dev/null 2>&1; then
    log "Blender $BLENDER_VERSION"
    local tarball="blender-${BLENDER_VERSION}-linux-x64.tar.xz"
    curl -fsSL "https://download.blender.org/release/Blender${BLENDER_SERIES}/${tarball}" -o "/tmp/${tarball}" \
      && tar -xJf "/tmp/${tarball}" -C /opt \
      && ln -sfn "/opt/blender-${BLENDER_VERSION}-linux-x64" /opt/blender \
      && ln -sf /opt/blender/blender /usr/local/bin/blender \
      && rm -f "/tmp/${tarball}" \
      || log "WARNING: Blender install failed"
  fi
}

install_ai() {
  if [ ! -x "$VENV/bin/python" ]; then
    log "Python 3.12 venv at $VENV"
    uv venv -q --python 3.12 "$VENV" || { log "WARNING: venv failed"; return; }
  fi
  if [ ! -f "$VENV/.ready" ]; then
    log "PyTorch (CPU) + AI tools"
    VIRTUAL_ENV="$VENV" uv pip install -q \
      --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple \
      --index-strategy unsafe-best-match \
      torch torchvision \
      opencv-python-headless numpy pillow \
      "rembg[cpu]" \
      mediapipe \
      faster-whisper "av<16" \
      piper-tts \
      simple-lama-inpainting \
      spandrel \
      sam2 \
      huggingface_hub librosa transformers \
      && touch "$VENV/.ready" \
      || log "WARNING: AI tools install failed"
  fi
  # A wrapper, not a symlink: a symlinked venv python resolves to the base interpreter
  # and loses the venv's packages.
  rm -f /usr/local/bin/vfx-python
  printf '#!/bin/sh\nexec %s/bin/python "$@"\n' "$VENV" > /usr/local/bin/vfx-python
  chmod +x /usr/local/bin/vfx-python
}

case "$MODE" in
  core) install_core ;;
  ai)   install_ai ;;
  all)  install_core; install_ai ;;
  *)    echo "usage: $0 [core|ai|all]"; exit 2 ;;
esac

"$(dirname "$0")/check.sh" 2>/dev/null || true
