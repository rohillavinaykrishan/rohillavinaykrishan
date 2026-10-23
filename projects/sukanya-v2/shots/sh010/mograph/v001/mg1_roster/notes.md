# MG1 Roster comp (Acts 1-2) v001
- Scene: compositions/mg1.html (composition id `mg1`), master f0-f260 = data-start 0, data-duration 10.44, 2160x3840 stage (scales to any 9:16 host).
- Includes compositions/roll.html = verbatim copy of shots/sh010/roll/v001/roll.html (nested host id `roll`). Roll does its own scroll, dimming and her-name Saffron; MG1's mask dim is off (auto-on only with the placeholder roll).
- Cursor tracks her row from roll_rows.json (her_row_index read from file; y = cap centre). Cell x 1146, width measured from Montserrat 500 54 px.
- Panels: P1 cy 1300 / P2 cy 2500, 2160x1180, skew -12deg, 60% opacity, 0.6x drift (11.4 px/f, reset per shot), 6 f expo-out slash-open, 3 f ease-in close, 2 f saffron-edged wipes on the fills; A02 tail rides P2 from f63. Hold: P1 drops into a 900 px C00 band (cy 1750) at f243.
- Charge (f243-260, flag `charge_fx` in build.py): bracket snap 1.25->1.0, P1 LOCKED at f254, 40 ki motes, push-in 1.00->1.03 with origin at her cell (1509, 1536). These overlap MG2's spec list: comp lead picks one owner.
- Rebuild: python3 tools/sync_inputs.py (plates; chain colour plates > edit+colorist cube > edit+MG1 temp cube > trailer placeholder), then python3 tools/build.py.
- Proxy: ../mg1_proxy540 (own root, symlinked assets/compositions) -> renders/mg1_proxy_540.mp4.
