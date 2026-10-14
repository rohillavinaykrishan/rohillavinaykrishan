#!/bin/bash
# Prints which VFX Studio tools are installed.
ok()  { printf '  ✅ %-22s %s\n' "$1" "$2"; }
bad() { printf '  ❌ %-22s %s\n' "$1" "missing"; }
ver() { "$@" 2>/dev/null | head -1; }

echo "VFX Studio toolkit:"
command -v blender  >/dev/null && ok Blender   "$(ver blender --version)"            || bad Blender
command -v ffmpeg   >/dev/null && ok ffmpeg    "$(ver ffmpeg -version | cut -d' ' -f1-3)" || bad ffmpeg
command -v sox      >/dev/null && ok sox       "$(ver sox --version)"                 || bad sox
command -v magick   >/dev/null || command -v convert >/dev/null && ok ImageMagick "" || bad ImageMagick
command -v krita    >/dev/null && ok Krita     ""                                     || bad Krita
command -v gimp     >/dev/null && ok GIMP      "$(ver gimp --version)"                || bad GIMP
command -v inkscape >/dev/null && ok Inkscape  "$(ver inkscape --version)"            || bad Inkscape
command -v colmap   >/dev/null && ok COLMAP    ""                                     || bad COLMAP
command -v ociocheck >/dev/null && ok OpenColorIO ""                                  || bad OpenColorIO
command -v hyperframes >/dev/null && ok HyperFrames "$(ver hyperframes --version)"    || bad HyperFrames

PY=/opt/vfx-ai/bin/python
if [ -x "$PY" ]; then
  for mod in torch cv2 rembg mediapipe faster_whisper piper simple_lama_inpainting spandrel sam2; do
    "$PY" -c "import $mod" >/dev/null 2>&1 && ok "py:$mod" "" || bad "py:$mod"
  done
else
  bad "AI venv (/opt/vfx-ai)"
fi
