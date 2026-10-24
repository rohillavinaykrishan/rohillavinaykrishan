/* MG1 streak paths (orbit around the Act-2 window, then the 2-turn log-spiral charge).
 * Pure functions of master frame (float). 4K px. UMD: browser -> window.MG1Streaks, node -> module.exports.
 * Spiral spec (treatment s3/s6): 2 turns, r0 (= distance at f336) -> 40 px around the name centre,
 * clockwise, arrives f356; arc-length speed ramps linearly from the orbit speed to v_end so the charge accelerates. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory;
  else root.MG1Streaks = factory;
})(typeof self !== "undefined" ? self : this, function (cfg) {
  "use strict";
  // cfg: {win2:[x,y,w,h], clashCuts:[f...], speeds:[px/f per cut], burstF, spiralF0, spiralF1, centre:[x,y], rEnd, turns, n}
  var W = cfg.win2, inset = 28, rad = 60;
  var x0 = W[0] + inset, x1 = W[0] + W[2] - inset, y0 = W[1] - inset, y1 = W[1] + W[3] + inset;
  var ex = x1 - x0 - 2 * rad, ey = y1 - y0 - 2 * rad, arc = Math.PI * rad / 2;
  var segs = [ // clockwise from the top-left corner end
    { t: "l", L: ex, a: [x0 + rad, y0], d: [1, 0] },
    { t: "c", L: arc, c: [x1 - rad, y0 + rad], a0: -Math.PI / 2 },
    { t: "l", L: ey, a: [x1, y0 + rad], d: [0, 1] },
    { t: "c", L: arc, c: [x1 - rad, y1 - rad], a0: 0 },
    { t: "l", L: ex, a: [x1 - rad, y1], d: [-1, 0] },
    { t: "c", L: arc, c: [x0 + rad, y1 - rad], a0: Math.PI / 2 },
    { t: "l", L: ey, a: [x0, y1 - rad], d: [0, -1] },
    { t: "c", L: arc, c: [x0 + rad, y0 + rad], a0: Math.PI }
  ];
  var P = 0; segs.forEach(function (s) { P += s.L; });
  function perim(s) {
    s = ((s % P) + P) % P;
    for (var i = 0; i < segs.length; i++) {
      var g = segs[i];
      if (s <= g.L || i === segs.length - 1) {
        if (g.t === "l") return [g.a[0] + g.d[0] * s, g.a[1] + g.d[1] * s];
        var a = g.a0 + (s / rad);
        return [g.c[0] + Math.cos(a) * rad, g.c[1] + Math.sin(a) * rad];
      }
      s -= g.L;
    }
  }
  var cuts = cfg.clashCuts, sp = cfg.speeds;
  function travelled(f) { // integral of speed from burstF to f
    var d = 0;
    for (var i = 0; i < cuts.length; i++) {
      var a = cuts[i], b = i + 1 < cuts.length ? cuts[i + 1] : Infinity;
      if (f <= a) break;
      d += (Math.min(f, b) - a) * sp[i];
    }
    return d;
  }
  var n = cfg.n || 8, C = cfg.centre, rEnd = cfg.rEnd || 40, turns = cfg.turns || 2;
  var F0 = cfg.spiralF0, F1 = cfg.spiralF1, T = F1 - F0, B = cfg.burstF;
  // streak k starts at s0 = (k + 0.5) * P / n measured from the top-left: k 0-3 land on top / right, 4-7 bottom / left
  function orbit(k, f) { return perim((k + 0.25) * P / n + travelled(f)); }
  var vIn = sp[sp.length - 1];
  var spir = [];
  for (var k = 0; k < n; k++) {
    var p0 = orbit(k, F0), dx = p0[0] - C[0], dy = p0[1] - C[1];
    var r0 = Math.hypot(dx, dy), th0 = Math.atan2(dy, dx);
    var b = Math.log(r0 / rEnd) / (turns * 2 * Math.PI), q = Math.sqrt(1 + b * b) / b;
    var L = (r0 - rEnd) * q, vEnd = 2 * L / T - vIn;
    spir.push({ r0: r0, th0: th0, b: b, q: q, L: L, vEnd: vEnd });
  }
  function spiral(k, f) {
    var S = spir[k], t = Math.max(0, Math.min(T, f - F0));
    var s = vIn * t + (S.vEnd - vIn) * t * t / (2 * T);
    var r = Math.max(rEnd, S.r0 - s / S.q), ph = Math.log(S.r0 / r) / S.b;
    var a = S.th0 + ph;
    return [C[0] + Math.cos(a) * r, C[1] + Math.sin(a) * r];
  }
  // burst start: from the collapsed shutter bundle (8 lines, centre y of win2)
  var cy = W[1] + W[3] / 2;
  function burstStart(k) { var t = orbit(k, B); return [Math.max(200, Math.min(1960, t[0])), cy + (k - 3.5) * 8]; }
  return {
    P: P, perim: perim, orbit: orbit, spiral: spiral, spir: spir, burstStart: burstStart,
    /* head position of streak k at master frame f (float). easeOut = burst ease; useSpiral false -> orbit only */
    pos: function (k, f, easeOut, useSpiral) {
      if (useSpiral !== false && f >= F0) return spiral(k, f);
      var o = orbit(k, f);
      var u = (f - B) / 4;
      if (u < 1) { var e = easeOut(Math.max(0, u)), s0 = burstStart(k); return [s0[0] + (o[0] - s0[0]) * e, s0[1] + (o[1] - s0[1]) * e]; }
      return o;
    }
  };
});
