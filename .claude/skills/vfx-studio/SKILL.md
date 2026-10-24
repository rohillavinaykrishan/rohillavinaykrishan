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
| Color grading | ffmpeg looks / .cube LUTs, OpenColorIO | `tools/vfx/bin/grade.sh look in out <look>`: movie (cinematic, blockbuster, moody, bleach, noir), song (bollywood, romantic, golden-hour, night-neon, dreamy), punjabi (punjabi-gold, punjabi-night, punjabi-desi, punjabi-romance, punjabi-dark), basic (teal-orange, warm, cool, bw, vintage, punchy, filmic); `grade.sh lut in out my.cube` |
| Slow motion / retime | ffmpeg motion interpolation | `tools/vfx/bin/grade.sh slowmo in.mp4 out.mp4 2` |
| Upscale | Real-ESRGAN (spandrel) | `vfx-python tools/vfx/bin/upscale.py in.png out.png [--scale 2] [--kind anime] [--frames N]` |
| Voice-over | Piper TTS (offline) | `vfx-python tools/vfx/bin/tts.py "text or file.txt" vo.wav [--voice hi_IN-pratham-medium]` |
| Subtitles / lyric timing | faster-whisper | `vfx-python tools/vfx/bin/transcribe.py song.mp3 out.srt\|.vtt\|.json [--language hi]` |
| Audio clean-up / mix | sox, ffmpeg; mixing inside HyperFrames via `hyperframes-audio` | |
| Motion graphics, titles, lyric videos | HyperFrames | use the `hyperframes` skill |
| Stylized post looks | ffmpeg | `tools/vfx/bin/post_look.sh <glow\|dream\|pixel\|scanlines\|rgbsplit\|vhs\|film\|comic\|mirror\|kaleido> in out` |
| Blender style looks | Blender | `tools/vfx/blender/looks.py`: realistic, toon, ink, sketch, neon, hologram, clay, xray, gold, glass, retro |
| Final delivery (4K default) | ffmpeg | `tools/vfx/bin/grade.sh deliver in.mp4 out.mp4 uhd\|uhd-vertical\|youtube\|reels\|master` |
| 4K master mux (client delivery encode) | ffmpeg libx264 + AAC | `THREADS=2 tools/vfx/bin/deliver_4k.sh picture.mp4 master.wav out_4K.mp4` → x264 slow crf 12 film High L5.2 yuv420p 25 fps g50 BT.709, AAC 320k 48 kHz, +faststart, -shortest; prints ffprobe + ebur128; refuses to overwrite (heavy: ~1.4 s/frame at 4K) |
| Delivery QC (auto) | ffprobe, ebur128, numpy, faster-whisper | `vfx-python tools/vfx/bin/auto_qc.py master.mp4 --expect-frames 750 [--fps 25 --size 2160x3840] [--names "VINAY KRISHAN ROHILLA"] [--no-words] --out review/qc_auto.md` → specs/CFR/a-v start, -14 LUFS ±0.5 & ≤ -1 dBTP, black/frozen spans, R≥B per frame, Whisper VAD-off segments (hallucinations flagged), 12-frame `_sheet.png`; exit 0 pass / 1 fail; ~30-50 s for 15-18 s 4K. Names = manual spelling checklist (no OCR) |
| Shorts / Reels reframe | rembg + ffmpeg | `vfx-python tools/vfx/bin/reframe.py in.mp4 short.mp4 --start S --duration D` → 2160x3840, crop follows the subject |
| Song mood → grade | librosa | `vfx-python tools/vfx/bin/song_mood.py song.wav mood.json` (tempo, key/mode, energy, sections, grade suggestion) |
| Restoration | Real-ESRGAN + GFPGAN + OpenCV | `vfx-python tools/vfx/bin/restore.py in.jpg out.png [--target 3840] [--denoise 6] [--face-strength 0.5]` (folders too) |
| Sound effects | numpy synth | `vfx-python tools/vfx/bin/sfx.py make all kit/`; `sfx.py place song.wav cues.json mix.wav` |
| Audio master | ffmpeg loudnorm | `tools/vfx/bin/master_audio.sh mix.wav master.wav youtube\|instagram` |
| Thumbnails / boards / cards | Chromium | `tools/vfx/bin/html2png.sh design.html out.png 1280x720` |
| Burned subtitles | ffmpeg + libass + Noto fonts | `-vf "subtitles=l.srt:force_style='FontName=Noto Sans Gurmukhi,Bold=1,Outline=2'"` |
| Project files zip | zip + Blender | `tools/vfx/bin/package_project.sh projects/<name>` → everything except rendered video, .blend packed |
| Depth from a photo ("AI LiDAR") + 3D parallax | Depth Anything V2 Small (Apache-2.0) | `vfx-python tools/vfx/bin/depth.py map img.jpg depth.png`; `depth.py parallax img.jpg out.mp4 --move dolly-in\|dolly-out\|orbit\|pan-left\|pan-right\|rise\|drift --dur 5 [--amount 0.8] [--size 1920x1080]` (~0.3 s/frame at 1080p) |
| Split delivery into parts | ffmpeg | `tools/vfx/bin/grade.sh split in.mp4 out_dir 45` → frame-exact parts + `full_audio.wav` |

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
