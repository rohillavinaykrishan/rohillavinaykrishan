# Studio conventions (every agent reads this first)

## Project layout

```
projects/<project>/
  brief.md              # what the client (the user) asked for
  spec.json             # delivery spec - see below
  shotlist.md           # VFX supervisor's breakdown: shots, departments, look, dependencies
  cg_plan.md            # CG supervisor's plan for CG shots + render budget
  source/               # the user's footage, audio, references (never modify)
  shots/<shot>/<dept>/v001/   # each artist writes ONLY inside its own dept folder
  shots/<shot>/<dept>/v001/notes.md   # what was done, commands used, known issues
  review/               # contact sheets + supervisor/lead notes
  deliver/              # final 4K files only
```

- Shot names: `sh010`, `sh020`, ... Versions: `v001`, `v002` (never overwrite a reviewed version).
- Hand-off = files. Read upstream files, write to your folder, list the output paths in your final message.
- Image sequences: `name.%04d.png`; alpha video: `.mov` (ProRes 4444); review video: `.mp4` (H.264).

## spec.json

```json
{"delivery": "3840x2160", "work_res": "1920x1080", "proxy_res": "960x540",
 "fps": 24, "aspect": "16:9", "look": "", "audio": "source/song.wav"}
```
Vertical (Reels/Shorts): delivery `2160x3840`, work `1080x1920`, proxy `540x960`.

## Resolution policy (4K always, delivered smartly)

This machine has 4 CPU cores and no GPU. Measured: Blender Cycles demo frame
= ~80 s at 1080p, ~330 s at native 4K. Therefore:

1. Iterate at `proxy_res` (fast tests, 1-3 s of the shot).
2. Final department work at `work_res` (1080p).
3. The colorist delivers every final at 4K with `tools/vfx/bin/grade.sh deliver in out uhd` (or `uhd-vertical`).
4. Native 4K renders and Real-ESRGAN upscales only for stills, thumbnails, posters or a hero
   shot of a few seconds, when the CG supervisor approves the budget.

## Shared machine = shared CPU

Agents run in parallel but share 4 cores. Planning, scripting, reviewing can
run together; **heavy jobs (Blender renders/sims, SAM 2, LaMa, upscales) run at
most 2 at a time**. Before starting one, check `pgrep -fa "blender|sam_roto|cleanup.py|upscale.py" | wc -l`;
if 2 are running, do your setup work first and start when one finishes. Run long
jobs with `run_in_background` and log to your version folder.

## Tools

The `vfx-studio` skill (.claude/skills/vfx-studio/SKILL.md) is the tool manual:
department → tool → command, speeds, gotchas. Blender looks:
`tools/vfx/blender/looks.py` (realistic, toon, ink, sketch, neon, hologram, clay,
xray, gold, glass, retro). Post looks: `tools/vfx/bin/post_look.sh` (glow, dream,
pixel, scanlines, rgbsplit, vhs, film, comic, mirror, kaleido). Free tools only:
never use credit-based connectors (Runway, ElevenLabs...) unless the user asks.

## Quality bar (checked by the team lead)

- Correct resolution, fps, duration and frame count for the spec; no dropped/duplicated frames.
- No black/empty frames, no NaN fireflies, no flicker in mattes, no visible seams from cleanup.
- Alpha edges clean (check over black AND white), audio in sync.
- Verify your own output before reporting: `ffprobe` it, extract 2-3 frames
  (`ffmpeg -ss T -i f -frames:v 1 x.png`) and look at them with Read.

## Final message format (every artist)

```
STATUS: done | blocked
OUTPUTS: <paths>
NOTES: <1-3 lines: what, how long it took, known issues>
```
