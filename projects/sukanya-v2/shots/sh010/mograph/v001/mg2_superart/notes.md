# MG2 SUPER ART FX v001 (master f243-f276)
Build: `python3 tools/build.py` (re-reads roll/v001/roll_rows.json, color/v001/plates/B01.mp4, cues.json; writes compositions/mg2.html, index.html, proxy/index.html, assets/).
Proxy: `cd proxy && hyperframes render . --format webm -f 25 -o ../mg2_proxy_540.webm` (about 20 s).

## Mount (comp lead)
- `compositions/mg2.html`, id `mg2`, data-start 9.72, data-duration 1.36, 2160x3840, transparent. See index.html (it runs on master time).
- Layer toggles via host data-variable-values (all default on): cursor, motes, shake, shatter, band, rings, speedlines, sparks, name, flash.
  e.g. `{"band":false}` if MG3 owns the band from f261.
- fx_handoff.json: the shake offsets for the other layers, the push-in curve, the settled name pose (for MG3/MG4), band and cursor geometry.

## Overlaps to resolve (comp lead)
- MG1 also draws cursor lock, motes and push-in f243-260 (`charge_fx`). Geometry is identical; turn ONE off (MG1 charge_fx=false, or MG2 cursor/motes=false). If MG2 owns them, MG2's charge layer is pushed with the same curve and origin as MG1's camera.
- The roll comp is visible until f260. MG2 owns the rows from f261 (27 cards from roll_rows.json f261, her_row_index 62).
- The B01 band is drawn f261-276. MG3 must match fx_handoff.band_settled_f267 at f277, or set band=false here.
- Flash is a plain 85/45/0% Ki White layer (screen ~= over on near-white). Ring refraction and CA only distort MG2's own pixels (cards and band).

## Inputs used
- roll_rows.json (FINAL, 79 rows, her_row_index 62, parked y 1536). B01 = color/v001/plates/B01.mp4 (graded), re-encoded to yuv420p.
- Fonts: director/v001/fonts only. Colours: palette only.

## Known
- B01 is soft at 1.575x (the counter-skewed plate has to cover the -12 deg parallelogram). The type is native vector, crisp at 4K.
- lint: `text_occluded` comes from the flash (intended); the 413-line file is one scene on purpose.
