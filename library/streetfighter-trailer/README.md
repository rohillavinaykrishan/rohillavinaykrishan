# Street Fighter trailer - shot library

Shared, reusable catalogue of the theatrical *Street Fighter* trailer. Watch it here instead of re-scrubbing the source.
Built 2026-10-23 by the Shot Librarian with free tools only (ffmpeg, OpenCV, rembg, faster-whisper, librosa).

## Source

| | |
|---|---|
| File | `projects/sukanya-v2/source/trailer.mp4` (do not modify) |
| Video | 1280x720 H.264 Constrained Baseline, ~1.13 Mb/s, yuv420p, bt709 |
| FPS | 24000/1001 (23.976), 4046 frames, 168.752 s |
| Audio | AAC LC 128 kb/s |
| Active picture | **`crop=1280:536:0:92`** (2.39:1, letterbox bars of 92 px above and below) |
| Block grid | Measured: inside the 536-px crop the 8x8 block edges sit on rows 4, 12, 20... (full-frame rows that are multiples of 8); columns are aligned (x = 0, 8, 16...). **Pad 4 rows on top before any deblock**, e.g. `crop=1280:536:0:92,pad=1280:544:0:4,<deblock>,crop=1280:536:0:4` (or deblock the full 720 frame first and crop afterwards). |
| Quality | Heavy compression: dark and smoky shots (bathhouse sf057-sf073, opening alley sf006-sf017) are blocky. Check `quality` and `blockiness` before upscaling. |

Time / frame conversion: `t = frame * 1001 / 24000`. Extract a frame exactly: `ffmpeg -i trailer.mp4 -vf "select=eq(n\,FRAME),crop=1280:536:0:92" -frames:v 1 out.png`.
Cut a shot frame-accurately: `ffmpeg -i trailer.mp4 -vf "trim=start_frame=IN:end_frame=OUT+1,setpts=PTS-STARTPTS,crop=1280:536:0:92" ...`.

## Files

| Path | What |
|---|---|
| `shots.json` | 144 shots (`sf001`-`sf144`). See the field list below. |
| `audio_map.json` | Speech spans (Whisper, **VAD off**) labelled `dialogue` / `sung`, music sections, RMS curve, onsets, silences, loudest hits, `clean_music_windows`. |
| `heroes.png` | 28 standout shots with id, time range, quality, characters and the 9:16 crop window (green lines). |
| `sheets/sheet_01..04.jpg` | Contact sheets, 40 shots each, with id, in-out time, quality, characters, camera and action burned in, plus the 9:16 crop window. |
| `stills/sfNNN.jpg` | One 480x201 JPEG per shot (active picture only), taken from the sharpest frame in the middle 70 % of the shot (`still_frame`). |
| `tools/` | The scripts that built all this, plus the raw Whisper outputs (full pass and gap passes). `notes.py` holds the by-eye annotations. |

## shots.json fields

- `in` / `out`: seconds (`out` exclusive). `in_frame` / `out_frame`: 0-based source frames (`out_frame` inclusive). `frames`, `duration`.
- `characters`: named **only when certain** from costume or face continuity; otherwise `unknown`; `[]` means no people (logos, inserts, establishing shots).
  Named characters: Ryu, Ken, Chun-Li, Guile, Cammy, Blanka, Dhalsim, E. Honda, Balrog, M. Bison.
  Not named on purpose: the man in the pink gi in the car scene (sf138-sf141; the dialogue says "Dan", but it is unverified), the bearded man with the horse (sf083), the man in the white suit or tracksuit (sf075/079/081), the man in the pink suit with the megaphone (sf087), and the masked figure (sf102).
- `action`: one line.
- `camera.move`: locked / pan / tilt / handheld / dolly / whip, from Farneback optical flow on the active picture (affine fit; `flow_px_per_frame` and `net_travel_px` at 320 px width; `parallax_residual` = median non-affine flow). `camera.solvable` = real camera travel with parallax, bright enough and not too blocky; **sf112 (beach oner) is confirmed solvable by COLMAP for 124.37-126.54**. sf032, sf040, sf116 and sf122 are candidates only; test them before relying on them.
- `mean_rgb` (0-255, active picture, whole shot), `dominant_hue` (name and `dominant_hue_deg`, `neutral` = desaturated), `blue_cast` (mean B > mean R).
- `best_vertical_crop_cx`: subject centre as a 0-1 fraction of the 1280-px active width (rembg human mask, upper body weighted; `crop_cx_source` says `human_mask`, `saliency` or `by_eye`). `best_vertical_crop_x_px` = left edge of a 9:16 window (301.5 x 536) in active-picture pixels, already clamped. For 9:16: `crop=302:536:X:92` on the full frame, then scale.
- `quality` 1-5: Laplacian sharpness percentile at full resolution, minus penalties for blockiness and darkness, with some by-eye corrections (shallow-focus close-ups are rated up). `sharpness_lapvar`, `blockiness` (8x8 boundary/interior gradient ratio, 1 = clean, >3 = visibly blocky) and `mean_luma` are the raw numbers.
- `hero`: standout frame for montages, posters and thumbnails.
- `audio`: speech spans that overlap the shot. `in_clean_music_window`: the shot lies inside a span with no dialogue that is at least 10 s long.

## audio_map.json - key facts

- Whisper `small` (int8, CPU) with `vad_filter=False` over the whole trailer, then each gap re-run as a short clip with `small` and `medium`. This recovers lines the earlier VAD-on transcript dropped ("Do you suffer?", "Forgive me", "Put him down!", "Round one", "You win", "To live is to fight / To fight is to live", "Oh, I don't know, Dan", the claw-hand line...).
- `sung` spans: "I won't deny it, I'ma show you" 79.06-81.42, "Ain't no stopping me" 84.3-87.0, the **rap hook 112.1-116.1** (words unclear), "I'm a street fighter" 126.16-127.58, and a chanted count 144.0-153.92 (low confidence).
- Brief-checked dialogue: "You lose" 117.37-118.46; Cammy "It might sting a little" 121.00-122.46 (over sf108/sf109); "You did that to your face, ..." 156.69-159.0 (the last word, "Kyle", is low-confidence).
- Labels come from the content and these known facts. The pYIN pitch metrics are attached for reference, but on the full mix they are dominated by the music, so they do **not** separate speech from singing reliably.
- `clean_music_windows` (no dialogue, at least 10 s): **63.89-82.70** (18.8 s, bathhouse fight into nightclub, contains sung lyric 79-81) and **144.27-156.54** (12.3 s, arena and Chun-Li to the title card, contains the chant). With no vocals at all: 63.89-78.91 (15.0 s).
- Silences below -40 dBFS: 33.55-33.69, 87.24-87.79, 104.88-105.14 (natural cut points). Biggest hit: 105.21 s.

## Corrections to earlier notes

- The studio logos are at **21.02-23.00 s** (sf018: Paramount, then Legendary, then Capcom dissolving over a seascape), not ~19-21. 18.3-21.0 s is the hadoken alley hit and a red explosion (sf016-sf017).
- The SF title card is sf136, 153.94-157.12 (the logo is fully formed from ~154.7).

## Using it

```python
import json
lib = json.load(open('library/streetfighter-trailer/shots.json'))['shots']
fight = [s for s in lib if s['quality'] >= 4 and 'unknown' not in s['characters'] and s['characters']]
by_char = {}
for s in lib:
    for c in s['characters']:
        by_char.setdefault(c, []).append(s['id'])
```
Open `heroes.png` first, then the sheets. Shot ids are stable; if you re-cut the list, add new ids rather than renumbering.
