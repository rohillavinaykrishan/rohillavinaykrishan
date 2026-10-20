# sh010 roto v001 - v3 title-design assets from review/logo_x4.png (2880x5120)

- sf_logo_alpha.png (1618x862 RGBA, source bbox x619-2237 y110-972). Key = max(smoothstep(G,4,42), smoothstep(R,135,205))
  (bg red: R<=125, G=0), speck removal (<400 px blobs), 0.7 px feather, colour un-premultiplied against the local bg and
  edge colour pulled from the solid interior, so there is no red halo. Header line cut off at y=972 (it starts at y~985). Checked over black and white.
- lineup.png (2880x1760 RGBA) = source y 3360-5120, alpha smoothstep 0->1 over its first 480 rows (source y 3360-3840).
  The fighters start around row 510 (Bison's hat). The treatment's "y 3800-5120" crop starts at row 440.
  LaMa removed the crew names "AAQUIB DANYAL / ANDREW HELLEN" (y 3845-3915, box masks, plus a 2nd pass on a stray L stem)
  and the DNEG watermark (x 1130-1770, y 4900-5045, letter-shaped hand mask). Masks are in scripts/.
- red_base.png (2880x5120 RGB, opaque) = clean field y 1120-2860, low-frequency flattened to a uniform mean (~R59), stacked
  with vertical mirroring, a flipped copy crossfaded over the 2 mirror seams (y 1690, 3430), and the left/right edges crossfaded so it tiles horizontally.
  Known: the source macro-blocking (from the 720p reel) is visible at 100%. Intended at ~35% under footage, so fine there.
- dneg_note.md: the watermark is too faint and busy to extract. Typeset "DNEG" instead.
Commands: vfx-python -I scripts/logo.py | scripts/masks.py | tools/vfx/bin/cleanup.py (LaMa, crops only) | scripts/assets.py
