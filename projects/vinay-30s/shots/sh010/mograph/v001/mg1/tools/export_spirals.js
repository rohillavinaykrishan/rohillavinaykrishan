// Writes spiral_handoff.json: per-frame head positions of the 8 hue streaks f336-356 (+ orbit at f335) for MG2.
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const D = JSON.parse(fs.readFileSync(path.join(ROOT, 'mg1_data.json')));
const FX = require(path.join(ROOT, 'assets/mg1/kit/kit.js'));
const ST = require(path.join(ROOT, 'assets/mg1/js/mg1_streaks.js'))(D.streaks);
const hues = D.roster.map(r => ({ id: r.id, char: r.char, hue: r.hue }));
const out = { owner: 'MG1 (mograph/v001/mg1)', note: 'MG2 owns the spirals f336-356. MG1 draws orbiting streaks only up to f335. orbit_heads_f326_336 are where MG2 picks each hue up (clockwise, 10-frame trails). head[] is the MG1 reference spiral, not rendered.', units: '4K px, master frames', centre: D.streaks.centre,
  spiral: { f0: D.streaks.spiralF0, f1: D.streaks.spiralF1, turns: D.streaks.turns, r_end: D.streaks.rEnd,
    direction: 'clockwise on screen (angle increasing, y down)', trail_frames: D.streakTrail,
    speed: 'arc-length speed ramps linearly from 115 px/f (orbit speed) to v_end so the head reaches r_end exactly at f1',
    code: 'assets/mg1/js/mg1_streaks.js (pos(k, f))' },
  streaks: hues.map((h, k) => ({ ...h, r0: +ST.spir[k].r0.toFixed(2), theta0_rad: +ST.spir[k].th0.toFixed(5),
    orbit_heads_f326_336: Array.from({ length: 11 }, (_, i) => { const f = 326 + i, p = ST.pos(k, f, FX.ease.out, false); return { f, x: +p[0].toFixed(2), y: +p[1].toFixed(2) }; }),
    orbit_speed_at_f336_px_per_f: 115,
    v_end_px_per_f: +ST.spir[k].vEnd.toFixed(2),
    head: Array.from({ length: D.streaks.spiralF1 - D.streaks.spiralF0 + 1 }, (_, i) => {
      const f = D.streaks.spiralF0 + i, p = ST.pos(k, f, FX.ease.out, true); return { f, x: +p[0].toFixed(2), y: +p[1].toFixed(2) }; }) })) };
fs.writeFileSync(path.join(ROOT, 'spiral_handoff.json'), JSON.stringify(out, null, 1));
console.log(out.streaks.map(s => [s.id, s.r0, s.v_end_px_per_f, s.head[s.head.length - 1]]));
