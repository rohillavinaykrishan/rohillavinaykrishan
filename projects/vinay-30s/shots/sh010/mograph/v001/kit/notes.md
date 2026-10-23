# FX kit v001 notes (FX Elements)
- Built: kit_src.js (eases, cues/beat lookup, brush wipe matte + fringe, plume, glow, dust, sparks, light point, glowStroke),
  make_kit.py (inlines cues.json -> kit.js), bake.js (PNG assets + review/fx_kit_v001.png via chrome-headless-shell).
- Commands: `python3 make_kit.py && node bake.js` (~20 s, light CPU). Determinism test: the same frame drawn twice,
  out of order, gives a byte-identical canvas.
- Fixed during build: brushWipe originally applied the matte row by row in destination-in mode, which erased the new layer. It now goes through a separate matte canvas.
- Open question for Director: with the spec ease.out over 6 f the wipe front is at 69/90/97/99/100% on frames +1..+5,
  so it reads as a fast snap rather than a visible sweep. `opt.ease` overrides it (e.g. FX.ease.linear) if the Director wants a slower sweep.
- Not in the kit, owned by the MGs: hue rays, shockwave, name copies (glowStroke/glow cover the drawing).
