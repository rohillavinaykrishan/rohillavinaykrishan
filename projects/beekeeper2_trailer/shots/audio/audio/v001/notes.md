# Audio v001 - Beekeeper 2 trailer soundtrack map

Source: `source/trailer_audio.wav` (48 kHz stereo, 87.24 s). Integrated -15.5 LUFS, LRA 14.5 LU, true peak -0.3 dBTP.
Real audio ends with a hard cut at **75.38 s**; 75.38-87.24 is digital silence (end card).
Music has a steady pulse of about **120 BPM** (librosa says 123; beat period ~0.49-0.51 s) from ~7.6 s to 75.4 s. Downbeats not checked.

## Timeline (seconds)
| Time | What happens |
|---|---|
| 0.00-0.70 | silence |
| 0.70-7.38 | Cold open: ambient drone swells up (riser) |
| 6.93-14.07 | VO 1 "You were the most dangerous operative they've ever created, but now the beekeepers have gone rogue," |
| 12.05 | boom (under VO) |
| 15.87-18.55 | VO 2 "and you're the only one who can stop them." |
| 15.9-20.0 | build/riser -> **BIG BOOM 19.5** |
| 21.65-27.59 | VO 3 "The beekeepers want complete control of the government, and they're prepared to kill anyone who gets in the way." over booms about 1 s apart (21.9, 23.5, 25.5, 26.5, 27.5, 28.1) |
| 29.3-30.19 | suck-out (low end drops) -> **BIG BOOM 30.19** |
| 30.72-34.14 | "If we're gonna go up against the beekeepers, we're gonna do it my way." (music drops out) |
| 33.02 / 34.83 / 36.80 | stings between lines; near-silence 33.98-34.81 and 36.06-36.65 |
| 34.88-35.98 | "I would hope for nothing less." |
| 37.43 | **SLAM back into action music** (act 2) |
| 39.26-40.58 | "I got you a car." -> **impact 40.77** |
| 42.48-44.52 | "1969 Dodge Super Bee." (hit 43.3, impact 44.84) |
| 45.42-47.40 | "Fully loaded with Stinger." -> **BIG IMPACT 47.67** |
| 47.67-58.9 | Action peak, loudest sustained part, no dialogue (impact 54.89) |
| 59.28-61.10 | "Welcome back, Clay." (music dips, impact 60.74) |
| 61.0-69.5 | Climax montage, full energy, no dialogue |
| 69.86-71.36 | "Next time, don't be so hard-headed." (energy pulls back) |
| 71.33-71.52 | short gap |
| **71.82** | **TITLE SLAM** (biggest late hit) |
| 71.82-75.38 | title sting / button, final hit 74.77, hard cut 75.38 |
| 75.38-87.24 | silence (end card) |

## Cuttable (music only, no speech; 0.15 s pad around words)
0.00-6.78 intro swell | 14.22-15.72 | 18.70-21.50 (contains boom 19.5) | 27.74-30.57 (suck-out + boom 30.19) |
36.13-39.11 (silence + slam 37.43) | 40.73-42.33 | **47.55-59.13 (11.6 s, action peak, best for fast cutting)** |
**61.25-69.71 (8.5 s, climax montage)** | 71.51-75.38 (title slam + button) | 75.38-87.24 silence.
Never cut inside the dialogue spans in `dialogue.json` (word timings are there). The 30.7-36.0 exchange is speech plus stings in near-silence, so keep it in one piece or cut only in the 34.14-34.88 gap.

## Edit suggestions
- Use the 19.5, 30.19, 37.43, 40.77, 47.67 and 71.82 hits for the main picture cuts and the title. 71.82 is the title card hit.
- 75.38 hard cut: the re-cut should end on the button or add a tail. Do not run the 12 s of silence.
- Master: about +1.5 dB to -14 LUFS with a limiter at -1 dBTP (the source peaks at -0.3).

## Method / known issues
- faster-whisper small with VAD (17 s), then a no-VAD pass and a medium re-check on 5 short clips. Fixes: "go up against" (small heard "cop against"); "I got you a car" re-timed 36.96 -> 39.26; "Welcome back, Clay." recovered (VAD had dropped it); "hard-headed" (small heard "hot-headed"); a "Thank you very much" hallucination in the silent tail was removed.
- Uncertain: "Stinger" may be "Stingers". Speaker identities not labelled.
- Hits, risers and sections come from librosa RMS, a <150 Hz band and onset envelope (automatic heuristics, not checked by ear). Section energy 0-1 = mean RMS mapped from -60..-12 dB.
