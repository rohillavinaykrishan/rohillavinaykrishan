# Producer sign-off: Vinay 30s SPECTRUM 4K (24 Oct 2026, 09:20 IST)
APPROVED for delivery. Waived auto_qc gates:
- Black frames f0-19 (cold open) and f357-364 (designed silence) are ink #07060A by design. f237 is 1 frame of the slam opening (not noticeable at speed).
- R>=B: the f122-196 Chun-Li blue / M. Bison violet beats are designed palette, not a cast. The ink frames come out at R-B about -4 because of 8-bit rounding. f197 is 1 frame of the wipe.
- Whisper: the only vocals are the sung "I'm a street fighter" and the chanted count (library audio_map). There is no spoken dialogue. "man of tomorrow" is a medium-model repetition artifact.
Follow-ups: auto_qc should allow designed black/hue ranges and an ink tolerance of -4.5, and its faster-whisper call crashes.
