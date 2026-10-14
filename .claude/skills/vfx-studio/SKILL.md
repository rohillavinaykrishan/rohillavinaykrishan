---
name: vfx-studio
description: Free, credit-free VFX studio for music videos and films, organised by department (concept, previs, modeling, rigging, animation, mocap, matchmove, roto, paint/cleanup, FX, lighting/rendering, compositing, color grading, upscaling, voice, subtitles, delivery). Use whenever the user wants VFX or post-production work done on footage, images or audio, or wants a 3D shot built, and it should be done with free local tools (Blender, Krita, GIMP, Inkscape, COLMAP, ffmpeg, rembg, SAM 2, LaMa, Real-ESRGAN, MediaPipe, Whisper, Piper) instead of paid credit-based services.
---

# VFX Studio (free tools only)

Everything here is open source, runs on CPU in the cloud container, and costs
no credits. The SessionStart hook installs it; check with
`tools/vfx/check.sh`. If the AI tools are not ready yet, wait for
`/opt/vfx-ai/.ready` (log: `/tmp/vfx-ai-install.log`) or run
`tools/vfx/install.sh ai`.

- AI scripts live in `tools/vfx/bin/` and run with `vfx-python` (Python 3.12 venv at `/opt/vfx-ai`).
- Models download on first use into `~/.cache/vfx-studio`, `~/.rembg`, `~/.cache/huggingface`.
- Do not use Runway, ElevenLabs or other credit-based connectors for this work unless the user asks.

## Department map

| Department | Tool | Command |
|---|---|---|
| Concept art / design | Krita, GIMP, Inkscape (scripted) | see *Image tools* |
| Previs, layout, modeling, texturing, rigging, animation, CFX, environments | Blender 5.2 (bpy scripts) | `blender -b -P script.py` |
| FX (smoke, fire, fluids, destruction, particles) | Blender Mantaflow / rigid bodies | bake in background, keep domain res low |
| Lighting & rendering | Blender Cycles (CPU) / Eevee | see *Blender* |
| Mocap (from normal video) | MediaPipe | `vfx-python tools/vfx/bin/mocap.py in.mp4 out.json --preview check.mp4` |
| Matchmove / camera solve | COLMAP | see *Matchmove* |
| Roto (automatic subject) | rembg | `vfx-python tools/vfx/bin/roto.py in.mp4 out.mov [--mode alpha\|matte\|green] [--model u2net_human_seg]` |
| Roto (click a specific object) | SAM 2 | `vfx-python tools/vfx/bin/sam_roto.py in.mp4 out.mov --point x,y [--neg x,y] [--frame N]` |
| Paint / prep / cleanup | LaMa inpainting | `vfx-python tools/vfx/bin/cleanup.py in.mp4 out.mp4 --mask mask.png` or `--box x1,y1,x2,y2` |
| Compositing | ffmpeg filters, Blender compositor, HyperFrames | see *Compositing* |
| Color grading | ffmpeg looks / .cube LUTs, OpenColorIO | `tools/vfx/bin/grade.sh look in.mp4 out.mp4 teal-orange` / `grade.sh lut in out my.cube` |
| Slow motion / retime | ffmpeg motion interpolation | `tools/vfx/bin/grade.sh slowmo in.mp4 out.mp4 2` |
| Upscale | Real-ESRGAN (spandrel) | `vfx-python tools/vfx/bin/upscale.py in.png out.png [--scale 2] [--kind anime] [--frames N]` |
| Voice-over | Piper TTS (offline) | `vfx-python tools/vfx/bin/tts.py "text or file.txt" vo.wav [--voice hi_IN-pratham-medium]` |
| Subtitles / lyric timing | faster-whisper | `vfx-python tools/vfx/bin/transcribe.py song.mp3 out.srt\|.vtt\|.json [--language hi]` |
| Audio clean-up / mix | sox, ffmpeg; mixing inside HyperFrames via `hyperframes-audio` | |
| Motion graphics, titles, lyric videos | HyperFrames | use the `hyperframes` skill |
| Stylized post looks | ffmpeg | `tools/vfx/bin/post_look.sh <glow\|dream\|pixel\|scanlines\|rgbsplit\|vhs\|film\|comic\|mirror\|kaleido> in out` |
| Blender style looks | Blender | `tools/vfx/blender/looks.py`: realistic, toon, ink, sketch, neon, hologram, clay, xray, gold, glass, retro |
| Final delivery (4K default) | ffmpeg | `tools/vfx/bin/grade.sh deliver in.mp4 out.mp4 uhd\|uhd-vertical\|youtube\|reels\|master` |

Video outputs: `.mov` = ProRes 4444 with alpha (for compositing), `.webm` =
VP9 with alpha, `.mp4` = H.264.

## Measured speed in this container (4 CPU cores, no GPU)

| Job | Time |
|---|---|
| rembg roto, 768×576 | ~0.7 s/frame |
| SAM 2 tiny roto, 768×576 | ~3.5 s/frame |
| LaMa cleanup, 768×576 | ~4 s/frame |
| MediaPipe mocap, 854×480 | ~0.1 s/frame |
| Real-ESRGAN 4× of a 274×171 still | ~15 s |
| Blender Cycles 640×360, 32 samples + denoise | ~5 s/frame (simple scene) |
| Blender Eevee 640×360 (software OpenGL) | ~12 s/frame - Cycles is usually faster here |
| Blender Cycles demo scene, 32 samples | ~80 s at 1080p, ~330 s at native 4K |
| 4K delivery (lanczos upscale + encode) | ~0.5 s/frame |
| COLMAP solve, 30 frames 640×360 | ~40 s |
| Piper TTS / Whisper `base` | a few seconds per sentence |

For multi-department jobs use the `studio` skill (agent team). Plan accordingly: test on 1-3 seconds (or `--frames N`) before running a whole
shot, and run long jobs with `run_in_background`. A 3-4 minute music video is
realistic; heavy CG or AI work on a feature-length film is not.

## Blender

- Write a bpy script, run `blender -b -P script.py -- args`. Use absolute
  output paths (`//` resolves to nothing when no .blend is open).
- Cycles: `scene.cycles.device = "CPU"`, low samples (16-64) + `use_denoising = True`.
- Eevee needs a display: `xvfb-run -a -s "-screen 0 1920x1080x24" blender -b ...`.
- Save the .blend (`bpy.ops.wm.save_as_mainfile`) next to renders so shots can be reopened.
- Mocap JSON from `mocap.py` holds 33 MediaPipe joints per frame (MediaPipe world
  coordinates: metres, hip centred): drive empties or an armature from it in a bpy script.

## Matchmove

```bash
mkdir -p mm/images && ffmpeg -i plate.mp4 -vf fps=10 mm/images/%04d.jpg
colmap automatic_reconstructor --workspace_path mm --image_path mm/images --sparse 1 --dense 0 --use_gpu 0
colmap model_converter --input_path mm/sparse/0 --output_path mm --output_type TXT   # cameras.txt / images.txt
```
Needs camera movement (parallax). A locked-off tripod shot cannot be solved,
and it doesn't need to be. Convert `images.txt` (world-to-camera quaternion +
translation) into Blender camera keyframes with a bpy script.

## Compositing

- Layer a cut-out over a new background: `ffmpeg -i bg.mp4 -i fg.mov -filter_complex "[0][1]overlay=format=auto" -c:v libx264 -pix_fmt yuv420p out.mp4`
- Green screen key: `-filter_complex "[1]chromakey=0x00B140:0.12:0.05[k];[0][k]overlay"`
- Blender's compositor (nodes via bpy) for multi-pass CG comps; HyperFrames for titles and graphics on top.

## Image tools

- Inkscape: `inkscape in.svg --export-type=png --export-filename=out.png`
- GIMP batch: `gimp -i -b '(script-fu ...)' -b '(gimp-quit 0)'`
- Krita needs a display: `xvfb-run -a krita --export --export-filename out.png in.kra`
- ImageMagick 6: `convert`, `montage` (there is no `magick` command).

## Not available here

- AI image or video generation (Stable Diffusion, Wan...): too slow without a GPU.
  Free GPU alternative: Kaggle notebooks (Kaggle connector).
- Natron: its download host is blocked; use Blender's compositor or ffmpeg.
- DaVinci Resolve, Maya, Houdini, Nuke: desktop-only and/or licensed.
