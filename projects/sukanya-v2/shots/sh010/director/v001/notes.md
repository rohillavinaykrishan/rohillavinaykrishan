# director v001 notes (2026-10-23, 16:17-16:50 IST)
- Treatment: projects/sukanya-v2/treatment.md ("SUPER ART"). Timing source of truth: cues.json (regenerate with make_cues.py).
- Music: client_music.mp3 116.30-134.30; drop 126.74 = f261. Analysis: librosa RMS/sub-band/onset (20 ms and 10 ms). Whisper small, vad_filter=False: audio/whisper_vadoff.py.
- Sheets: ffmpeg fps=1 / fps=4 tiles of crop=1280:536:0:92; selects_v001.png = every chosen shot.
- Roll measured from movie.mp4 64.0/65.0 s: pitch 23 px, 117 px/s, gutter x 361 (720 wide).
- Fonts fetched from the Google Fonts CSS API into fonts/.
- lookdev/board.html -> director_board_v001.png via tools/vfx/bin/html2png.sh (a direction mock; its band colour is too green, see treatment section 5).
- Known: the "?" character IDs need the Shot Librarian; ~27 roll rows above SAMITH must be transcribed from movie.mp4.
