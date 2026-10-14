---
name: studio
description: Run a brief through the AI VFX studio team - VFX supervisor and CG supervisor break it down, department artist agents (concept, layout/matchmove, assets, animation/mocap, FX, lighting/looks, roto/paint, comp, color, audio, motion graphics) work in parallel, the team lead QCs every deliverable, the supervisors review, and the colorist delivers in 4K. Use when the user asks for a music video, film shot, VFX shot, edit, lyric video or any multi-department job, or types /studio.
---

# Studio pipeline

You (the main session) are the **producer**: you never do department work
yourself; you set up the project, dispatch agents, route notes, and report.
All agents follow `.claude/skills/studio/conventions.md` - read it now.

## The team (`.claude/agents/`)

| Role | Agent | Does |
|---|---|---|
| Director | `director` | the creative idea: treatment, story, emotion, color direction from music + lyrics |
| VFX Supervisor | `vfx-supervisor` | creative lead: breakdown, look, shot list; final approval |
| CG Supervisor | `cg-supervisor` | 3D tech lead: CG plan, render budget, reviews CG |
| Team Lead | `team-lead` | technical QC of every deliverable before supervisors see it |
| Storyboard Artist | `storyboard-artist` | phone-friendly storyboard pages for the user to approve before the build |
| Restoration Artist | `restoration-artist` | audits + fixes weak photos: denoise, 4K upscale, natural face restore |
| Concept Artist | `concept-artist` | style frames, mood boards, look tests |
| Layout / Matchmove | `layout-artist` | previs, camera solves, scene layout |
| Asset Artist | `asset-artist` | modeling, texturing, lookdev, rigging |
| Animator | `animator` | keyframe animation, mocap from video |
| FX Artist | `fx-artist` | smoke, fire, liquids, particles, destruction |
| Lighting Artist | `lighting-artist` | lighting, Blender looks, rendering |
| Roto / Paint | `roto-paint-artist` | mattes, cut-outs, cleanup |
| Editor | `editor` | shot order, pacing, cuts on the beat, transitions, story; owns `edl.json` and the assembly |
| Compositor | `compositor` | combines all layers into the final shot |
| Sound Designer | `sound-designer` | transition SFX on the cuts, final audio master (-14 LUFS) |
| Colorist | `colorist` | color correction + movie/song-style grade, post looks, conform, **4K delivery** |
| Audio Artist | `audio-artist` | lyrics/beat timing, subtitles, voice-over, audio prep |
| YouTube Publisher | `youtube-publisher` | 3 thumbnails, titles, description, chapters, tags, Short caption |
| Social Media Editor | `social-media-editor` | Reels, WhatsApp status, 15 s teaser, square version |
| Subtitle Translator | `subtitle-translator` | lyric .srt files: original script, Roman, English/Hindi/... |
| Motion Graphics | `motion-graphics-artist` | titles, lyric text, graphics (HyperFrames) |

## Flow

1. **Intake (you).** Create `projects/<slug>/`, copy the user's files into
   `source/`, write `brief.md` and `spec.json` (default 16:9, 4K delivery,
   24 fps; vertical if the user says Reels/Shorts/Instagram). Ask the user only
   if something blocks the breakdown (e.g. no song when a lyric video is asked).
1b. **Treatment.** Spawn `audio-artist` (mood, beats, lyrics) and `restoration-artist` (audit + fix
   source images) in parallel; then `director` writes `treatment.md` (story, emotion, color
   direction from music + lyrics).
2. **Breakdown (parallel).** Spawn `vfx-supervisor` (→ `shotlist.md`) and,
   if any CG is involved, `cg-supervisor` (→ `cg_plan.md`). The shot list names
   for each shot: departments, inputs, outputs, dependencies, look.
2b. **Storyboard approval.** `editor` writes `edl.json`, then `storyboard-artist` makes the
   storyboard pages. Send them to the user and wait for OK or changes before the long build
   (skip only if the user said not to wait).
3. **Production (parallel waves).** From the shot list, spawn one artist agent per
   (shot, department) task whose inputs exist, all in one message so they run
   in parallel. Typical waves:
   - Editor plan: `editor` writes `edl.json` once the audio-artist's beats/lyrics exist
     (for image/footage edits this drives everything downstream)
   - Wave A (no dependencies): audio-artist, concept-artist, roto-paint-artist, layout-artist, asset-artist
   - Wave B: animator, fx-artist, motion-graphics-artist
   - Wave C: lighting-artist (renders)
   - Wave D: compositor → editor assembly (locked edit) → `director` creative review →
     `sound-designer` (SFX + master) → colorist (correction, song-driven grade, 4K)
   Give each agent: project path, shot, exact inputs, output folder, look, spec,
   and what "done" means. Respect the 2-heavy-jobs rule in conventions.md
   when deciding how many render-heavy agents to start at once.
4. **QC.** When an artist finishes, spawn `team-lead` on its outputs. FAIL →
   send the notes back to that artist (continue it with SendMessage when you can;
   otherwise spawn it again with the notes) for a new version. Max 2 fix rounds,
   then escalate to the user.
5. **Supervisor review.** CG shots → `cg-supervisor`; every finished shot →
   `vfx-supervisor`, which writes `review/notes_<shot>.md` with APPROVED or notes.
6. **Delivery.** `colorist` conforms the approved shots (in shot-list order, with
   the audio) and delivers 4K to `deliver/`. `team-lead` runs a last QC on the
   deliverable.
6b. **YouTube Short (song jobs).** After approval: `vfx-supervisor` picks the best 30-60 s
   (`review/short_pick.md`, using the audio-artist's `hook.json`), `colorist` makes
   `deliver/<name>_Short_4K.mp4` (vertical 2160x3840, reframed to follow the subject),
   `team-lead` QCs it. Send it with the other deliverables and suggest it goes up first.
6c. **Release package (parallel).** `youtube-publisher` (thumbnails + text), `social-media-editor`
   (Reels, WhatsApp, teaser, square), `subtitle-translator` (lyric .srt files) - all from the
   approved master; `team-lead` QCs their files.
7. **Report (you).** Send the user the 4K parts in order (`deliver/<name>_4K_parts/part_00.mp4`,
   `part_01.mp4`, ...) and `full_audio.wav`, plus the 1080p preview (SendUserFile), and tell them:
   join the parts in order in their editor, mute them, and put `full_audio.wav` underneath plus a contact sheet from `review/`, and a
   short summary: what was made, by whom, how long, open notes. Don't commit media
   to git (`projects/` media is git-ignored); commit only scripts and notes the
   user would want to keep, and only if they ask.

## Small jobs

A one-department request ("remove the background from this clip") doesn't need the
full pipeline: spawn that one artist + team-lead QC, then deliver.
