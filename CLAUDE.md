# Video tooling (cloud sessions)

`.claude/hooks/install-video-tools.sh` installs these in the background at session
start. Wait for `/opt/video-tools/.ready` before using them (log:
`/tmp/video-tools-install.log`).

| Need | Tool | How to call |
|---|---|---|
| Programmatic cut / join / overlay | MoviePy 2 | `video-python script.py` (`from moviepy import ...`) |
| Remove silence / dead air | auto-editor | `auto-editor in.mp4 -o out.mp4 --no-open` |
| Find shot changes | PySceneDetect | `scenedetect -i in.mp4 detect-adaptive list-scenes` |
| Speech-to-text, word timings | faster-whisper | `video-python` + `from faster_whisper import WhisperModel` (CPU: `compute_type="int8"`) |
| Background removal | rembg | `rembg i in.png out.png` (models download on first use) |
| Node compositing, keying, tracking | Blender 4.5 LTS | `blender -b --python script.py` |

Also available: HyperFrames (see its skills), ffmpeg, ImageMagick.

There is no GPU here: run AI video models (Wan, LTX-Video, HunyuanVideo, ComfyUI)
in a Kaggle/Colab notebook instead, or use the Runway connector.

Video tools live in their own venv (`/opt/video-tools`); don't `pip install` them
into system Python, since MoviePy's `pillow<12` pin breaks other packages there.
