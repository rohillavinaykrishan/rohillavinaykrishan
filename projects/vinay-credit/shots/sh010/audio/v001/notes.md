# sh010 audio v001 - music bed (Audio Artist)

## Deliverable
- `music_bed.wav`: trailer 61.00-76.00 s (window locked by the director), ONE continuous take, no stitch.
  48 kHz stereo, 24-bit, 720000 samples (exactly 15.000 s). Fade-in 0.15 s, fade-out 14.30-15.00 (director spec;
  supersedes the 0.3/1.2 s of the original task). Unmastered, no focus-pull, no SFX.
  Command: `ffmpeg -i source/trailer.mp4 -vn -af "aresample=48000,atrim=start_sample=2928000:end_sample=3648000,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.15,afade=t=out:st=14.3:d=0.7" -ac 2 -c:a pcm_s24le music_bed.wav`
- `beats.json`: beats, hits (with type, frame at 25 fps, trailer time), native whooshes, silence, sections, dialogue spans.
- `bed_envelope.png`: RMS + >4 kHz envelope with the hits marked.

## Verified timings (10 ms analysis hop, window-relative)
| event | treatment | measured | frame@25 |
|---|---|---|---|
| opening hit | 1.0 | attack 1.00, peak 1.04 (+14 dB jump) | 25 |
| lock hit (loudest) | 10.20 | attack 10.18-10.19, peak 10.24-10.26 at -7.9 dB | 255 |
| silence | 11.94-12.22 | < -30 dB 11.96-12.26 (-34..-39 dB 11.98-12.24) | 299-306 |
| drop | 12.28 | attack 12.26-12.28, transient peak 12.36 | 307 (peak 309) |
All three match the treatment within 1 frame (40 ms). Other trailer-native hits: 4.77, 5.62, 6.00, 6.21, 6.84, 7.63, 11.41, 14.44, 14.77.
Native whooshes (high-band rises) into the hits: 0.60-1.00 and 9.40-10.17.
BPM: 115.4 (librosa beat_track) / 117.5 (song_mood); the score is not on a rigid grid, so use hits over beats. D minor.

## KNOWN ISSUE: there IS a voice in the locked window
Trailer 62.70-63.66 (bed t = 1.70-2.66): an announcer-style shout "Round one!", centre-panned. The whole-trailer
VAD pass missed it (transcript gap 59.6-78.2 looked clean), but re-transcribing the bed gives "Round one!" with
transcribe.py, and Whisper small and medium (with and without VAD, on full, mid and voice-band versions) all agree.
The spectrogram (`voice_in_window_spectrogram.png`) shows voiced, gliding harmonics at 1.75-2.05 and 2.30-2.60. It is not in the side channel.
Rest of the bed: no words (apart from the usual "Thanks for watching" hallucination on the side channel only, p 0.0).
Options for the director and sound designer:
1. Keep it. It is the film's own "Round one!" call, on-genre, and it lands right after the opening hit. It is still a voice, though.
2. `music_bed_novox.wav`: same bed with the centre 180-4000 Hz notched over 1.70-2.66 (40 ms ramps). transcribe.py
   then returns 0 segments, but you can hear a ~1 s dip about 8 dB down (bass and air stay). The sub layer at 1.03 could mask it.
3. Alternative window: the clean music runs 63.66-78.2 (next speech "I won't deny it" from ~78.2-79.1). That is only 14.5 s,
   so 63.70-78.70 with the fade-out from 78.0 would need the timing re-cut (all hits move -2.70 s). Not recommended.
Other dialogue-free stretches checked: 113-128 has low-confidence voice hits ("You lose" 117.9, "I'm a street fighter" 126-127.7);
130-157 has a lot of speech that the VAD pass missed ("My business is a fight", "To live is to fight"...).

## Verification
- ffprobe: pcm_s24le, 48000 Hz, 2 ch, 720000 samples.
- RMS envelope checked (png): fade-in, hit 1.0, dip 8.0-9.5, peak 10.2, silence 11.96-12.26, drop 12.28, fade 14.3.
- Re-transcription of the bed: "Round one!" (see above). novox variant: no words.
