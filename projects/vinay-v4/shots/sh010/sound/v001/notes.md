# sh010 sound v001 - real trailer bed, no SFX

## Result
- `mix_master.wav`: built to the spec in section 10. It uses source/trailer.mp4 112.10-127.10, with a 3-frame fade-in and a fade-out from 14.40 to 15.00. Nothing is added: no SFX, no EQ, no stereo processing.
  It is 720000 samples (15.000 s), 48 kHz stereo, 24-bit, and sample-aligned with the raw bed (cross-correlation lag 0).
  - Loudness: -14.0 LUFS integrated, -1.50 dBTP (4x), sample peak -1.56 dBFS.
  - AAC 320k `-cutoff 20000`: -1.47 dBTP. AAC 192k `-aac_coder fast -cutoff 20000`: -1.30 dBTP. Both are within -1.0.
- `mix_master_altfade_13.40-14.00.wav`: an option, not the spec. Same chain, but the fade runs 13.40-14.00, so the tail line "I'm a street fighter" is not heard. -14.0 LUFS, -1.50 dBTP, AAC 320k -1.48, AAC 192k fast -1.42.
- Since there are no SFX, the version without effects is the same file as the master.

## BLOCKER: the bed is NOT dialogue-free
Treatment section 2 says 112.10-127.10 has no words. Re-transcribing proves it does.
1. **"You lose"**, source about 117.37/117.64-118.46 (bed 5.27-6.36, frames about 132-159). This is the announcer line, and it ends exactly where the near-silence begins.
   - Whisper small and medium both hear it on 4 clip offsets, on the whole raw bed (medium) and on the delivered master.
   - The spectrogram shows the formants (see qc/).
   - So the "silence" used for REGISTRATION is the gap right after "YOU LOSE". For a career-pride credit, that line is the wrong message.
2. **"I'm a street fighter"**, source from 126.16 (bed 14.06). The 14.40-15.00 fade does not hide it: "I'm a str-" is transcribed from mix_master.wav. The alt-fade master removes it.
3. "(Let's) go" at about 121.7-122.3 is not confirmed. Only 1 of 8 windows picked it up, and the spectrogram shows a pitched lead, which reads as music.

The director's clip pass (cand_110.json) missed items 1 and 2. assets_prev/trailer_dialogue_words.json already had both ("lose", mis-timed to 112.05-112.91, and "I'm a strength" at 126.27).

Options for the director (not done here, because the picture is cut to this window and treatment 10 bans changes to the music):
- (a) Use the alt-fade tail. This fixes item 2 only.
- (b) Pick another window, or recut the picture to one.
- (c) Try source separation (demucs, free, not installed) to remove the voice in 117.3-118.5 and 126.1-127.1. Quality is unknown, and it is a change to the music.
- (d) Accept "You lose" as in-game announcer sound. I would not recommend this.

## Cue measurement (10 ms RMS, 5 ms band onsets, librosa onsets, waveform; src = t + 112.10)
No cue is off by more than one frame.
- **Silence:** measured 118.47-118.70, under -30 dB (-30 to -35). This matches 118.46-118.70.
- **HERO f173:** main attack 6.92 (119.02), with a pre-attack at 6.88 (f172).
  - The "+21 dB in one bin" claim does not hold at 10 ms. The level climbs from -31 dB (6.60) to -21 dB (6.85) and reaches -12 dB at 6.95.
- **TITLE f275:** onset 11.00 (123.10), body peaks at 11.02.
- **Other cues:** f6 0.24 (a ramp, not a hit), f69 2.75, f81 3.24, f113 4.50, f121 4.84, dip f137 5.48, pickup f141 5.65, f208 8.31, f251 10.04, f291 11.66, f304 12.16.
- **Ambiguous cues:**
  - f81: no spectral onset at its frame; neighbours at 3.15 and 3.33.
  - f291: the strongest spectral onset is at 11.57.
  - f304: a smaller pre-event at 12.085.
  - The loudness and waveform peaks still sit on the cue frames.

## How
- Bed: `ffmpeg -i source/trailer.mp4 -af "aresample=48000:resampler=soxr:precision=28,atrim=112.10:127.10,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.12,afade=t=out:st=14.40:d=0.60"`. Trimmed to 720000 samples, because soxr gave one extra sample.
- Master: `vfx-python scripts/master.py bed.wav mix_master.wav -1.5 -14.0`. This is +0.40 dB static gain plus a 4x-oversampled lookahead peak limiter (10 ms).
  - Max gain reduction is 1.69 dB, only on the loudest peaks (1.44% of samples). The silence and the HERO hit are untouched (+0.40 dB uniform). The TITLE hit loses about 1.2 dB for about 40 ms.
  - I did not use master_audio.sh. Its loudnorm can fall back to dynamic mode and would reshape the real near-silence.
- QC: qc/qc_envelope_cues.png, qc/cue_waveforms.png, qc/cue_windows_rms_flux.png, the spectrogram of the voice regions, qc/transcripts/*.json, and the AAC test encodes in qc/*.m4a.
- Time: about 35 min.
