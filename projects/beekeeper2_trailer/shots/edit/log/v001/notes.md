# Footage log v001 - source/trailer_original.mp4

Source: 1280x720, 24000/1001 fps, 2092 frames, 87.254 s. Picture is ALREADY letterboxed 2.39:1
(active 1280x536 at y=92, cropdetect) on every shot except the red channel bumper s061.
=> For the 2.39 framing, crop `1280:536:0:92` and rebuild the bars at work res. Don't add bars on top of the existing ones.

61 shots logged in `footage_log.json` (id, frames, start/end s, duration, thumb, description, size,
burned-in text, exposure/colour notes + numeric stats on the active area, usable flag, dialogue over the shot).
Contact sheet: `review/footage_contact_sheet.jpg`. Dialogue transcript with word timings: `dialogue.json`.

## Structure of the original
| time | shots | content |
|---|---|---|
| 0.00-19.85 | s001-s002 | cold open: dusk hillside, long tilt to Statham MCU, VO "most dangerous operative..." |
| 19.85-22.90 | s003-s004 | MGM + Miramax logos (DROP) |
| 22.90-30.49 | s005-s011 | bee emblem, villain hall, DC night, Irons/Statham park, blonde agent corridor fight |
| 30.49-31.11 | s012 | black |
| 31.11-37.66 | s013-s016 | Irons/Statham dialogue ("my way" / "nothing less" / "I got you a car") |
| 37.66-38.66 | s017-s018 | "JASON" / "STATHAM" cards (burned text) |
| 38.66-55.26 | s019-s041 | car reveal + Super Bee inserts + tarmac shoot-out, fast cutting (0.4-1.8 s), ends in a flash strobe |
| 55.26-59.10 | s042 | main title "THE BEEKEEPER 2" (burned) |
| 59.10-69.49 | s043-s057 | tunnel fight: flamethrower, fireball, melee, explosions (very short shots, dark/amber) |
| 69.49-69.90 | s058 | black |
| 69.90-71.74 | s059 | button: Statham CU, "...don't be so hot-headed" |
| 71.74-75.33 | s060 | "ONLY IN THEATERS JANUARY 15" end card (burned text, billing) |
| 75.33-87.25 | s061 | third-party "NET WORK - NEW TRAILERS EVERY DAY" red bumper (DROP; I have not checked the audio under it yet. Listen before using it.) |

Usable picture: about 50 s of clean (non-text, non-black) footage. Burned-in text/logos: s003, s004, s017, s018, s042, s060, s061.

## Dialogue (faster-whisper base, check by ear)
6.93-14.07 "You were the most dangerous operative they've ever created, but now the beekeepers have gone rogue,"
15.87-18.55 "and you're the only one who can stop them."
21.65-27.59 "The beekeepers want complete control of the government, and they're prepared to kill anyone who gets in the way."
30.54-33.76 "If we're gonna [go up] against the beekeepers, we're gonna do it my way."
34.40-35.92 "I would hope for nothing less."   36.96-40.38 "I got you a car."
42.48-44.52 "1969 Dodge Super Bee."   45.42-47.40 "Fully loaded with Stinger."
69.84-71.22 "...don't be so hot-headed." (start of the line is misheard)
VO runs across cuts (e.g. 21.65-27.59 runs over s004-s010), so recut sections must keep audio blocks intact or cut between lines.

## Colour/exposure notes (for the colorist)
- Three looks in the source: (1) warm dusk pink/orange (s001-s002); (2) flat overcast daylight, neutral-cool (park s008-s021, tarmac s024-s039, blue-teal cast, sky near clip); (3) dark tunnels, amber/olive + green fluorescent (s043-s059).
- Very dark / crushed, need a lift: s022, s023, s049, s051 (35-47 % of active pixels below Y 8), s007.
- Clipping: s032 (~5 % muzzle flash), s047/s048 fireball, s041 strobe white frames.
- Fades already baked in: s001 head (from black ~0.6 s), s013 head (frames 746-765), s059 head (frames 1676-~1700). Don't use those frames in a hard cut.
- s041 is a strobe that alternates frame by frame between near-white and dark (photosensitivity), and s011 has a motion-blur tail. Treat both as transition material.

## Method
ffmpeg `select=gte(scene,0)` per-frame scene scores (320 px) + `signalstats` YAVG. I checked every candidate above 0.08
by eye on before/after frame pairs. I rejected muzzle flashes, whip-pans and the text animation, and found the
black spans and fades from the luma curve. Re-run stats/thumbs/sheet with:
`python3 -I shots/edit/log/v001/tools/log_stats.py source/trailer_original.mp4 shots/edit/log/v001 review`
(the shot boundary list is hard-coded in that script). Dialogue: `vfx-python tools/vfx/bin/transcribe.py source/trailer_audio.wav .../dialogue.json`.
