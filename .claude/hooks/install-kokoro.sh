#!/bin/bash
# Installs Kokoro TTS (kokoro + espeak-ng) in Claude Code cloud sessions.
# The pip install pulls PyTorch (~several minutes), so it runs in the background.
# Progress: /tmp/kokoro-install.log; done when /opt/kokoro/.ready exists.
set -uo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

if [ -f /opt/kokoro/.ready ] && python3 -c "import kokoro" 2>/dev/null; then
  echo "Kokoro TTS: ready."
  exit 0
fi

install() {
  set -e
  mkdir -p /opt/kokoro
  # A killed apt run can leave dpkg half-configured; repair it before installing.
  dpkg --configure -a || true
  command -v espeak-ng >/dev/null || {
    apt-get update -qq
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq espeak-ng
  }

  # docopt 0.6.2 (needed by num2words) fails to build with current setuptools,
  # so build its wheel with an older setuptools in a throwaway venv.
  if ! python3 -c "import docopt" 2>/dev/null; then
    python3 -m venv /opt/kokoro/buildenv
    /opt/kokoro/buildenv/bin/pip install -q "setuptools<70" wheel
    /opt/kokoro/buildenv/bin/pip wheel -q --no-build-isolation --no-deps docopt==0.6.2 -w /opt/kokoro/wheels
    pip install --break-system-packages -q /opt/kokoro/wheels/docopt-*.whl
  fi

  # Without this pin pip picks a spaCy 4 pre-release that has to build from source and fails.
  echo "spacy<4" > /opt/kokoro/constraints.txt
  pip install --break-system-packages -q --only-binary=spacy -c /opt/kokoro/constraints.txt kokoro soundfile
  python3 -c "import kokoro"
  touch /opt/kokoro/.ready
}
export -f install

setsid nohup bash -c install >/tmp/kokoro-install.log 2>&1 < /dev/null &
echo "Kokoro TTS: installing in background (log: /tmp/kokoro-install.log)."
