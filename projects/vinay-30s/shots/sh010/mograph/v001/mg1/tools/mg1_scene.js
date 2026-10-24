/* MG1 "Roster + Clash" scene logic (master frames 0-356). Inlined into compositions/mg1.html by build_mg1.py.
 * Everything visible is a pure function of the master frame f = round(local time * 25).
 * Uses the shared kit (window.FX: eases, brush wipe, plume, dust, glowStroke) and MG1Streaks. */
(function () {
  var D = window.MG1_DATA;                // generated from cues.json by build_mg1.py
  var FX = window.FX;
  var E_OUT = FX.ease.out, E_IN = FX.ease.in, cl = FX.clamp01;
  var vars = {};
  try { vars = (window.__hyperframes && window.__hyperframes.getVariables && window.__hyperframes.getVariables()) || {}; } catch (e) {}
  var fxScale = +(vars.fxScale || D.defaults.fxScale), useSpirals = vars.spirals == null ? D.defaults.spirals : !!vars.spirals;
  var usePush = vars.push == null ? D.defaults.push : !!vars.push;
  var $ = function (id) { return document.getElementById(id); };
  var stage = $("mg1-stage"), bgC = $("mg1-bgfx"), fgC = $("mg1-fgfx");
  [bgC, fgC].forEach(function (c) { c.width = Math.round(D.W * fxScale); c.height = Math.round(D.H * fxScale); });
  var bg = bgC.getContext("2d"), fg = fgC.getContext("2d");
  var tmpA = FX.canvas(bgC.width, bgC.height), tmpB = FX.canvas(bgC.width, bgC.height), tmpM = FX.canvas(bgC.width, bgC.height);

  var R = D.roster, NR = R.length, CARD = D.cardRect, WIN1 = D.win1, WIN2 = D.win2;
  var SH0 = D.shutter.f0, SH1 = D.shutter.f1; // 223, 236
  var CL0 = D.clash.f0, SP0 = D.charge.f0, LAST = D.lastFrame; // 237, 336, 356
  var cards = R.map(function (r) {
    return { r: r, el: $("mg1-card-" + r.id), hold: $("mg1-h-" + r.id), name: $("mg1-n-" + r.id), tags: $("mg1-t-" + r.id) };
  });
  var card0 = $("mg1-card-C0"), label = $("mg1-label"), hair = $("mg1-hair");
  var shutter = $("mg1-shutter"), slivers = [], win2 = $("mg1-win2");
  for (var i = 0; i < NR; i++) slivers.push({ el: $("mg1-sl-" + i), img: $("mg1-sli-" + i), tint: $("mg1-slt-" + i) });
  var ST = window.MG1Streaks(D.streaks);

  /* ---- brush-wipe matte -> CSS clip-path (exact kit geometry, recorded from FX.brushMatte) */
  function matteRects(rect, p, opt) {
    var out = [];
    var rec = { save: function () {}, restore: function () {}, beginPath: function () {}, rect: function () {}, clip: function () {},
      fillRect: function (x, y, w, h) { out.push([x, y, w, h]); } };
    FX.brushMatte(rec, rect, p, opt);
    return out;
  }
  function r1(v) { return Math.round(v * 10) / 10; }
  function clipIn(rect, p, opt) {
    var rs = matteRects(rect, p, opt);
    if (!rs.length) return "inset(100%)";
    return 'path("' + rs.map(function (r) { return "M" + r1(r[0]) + "," + r1(r[1]) + "h" + r1(r[2]) + "v" + r1(r[3]) + "h" + r1(-r[2]) + "Z"; }).join("") + '")';
  }
  function clipOut(rect, p, opt) { // whole frame minus the revealed rects (rows trimmed to abut exactly)
    var rs = matteRects(rect, p, opt);
    var s = "M-50,-50H" + (D.W + 50) + "V" + (D.H + 50) + "H-50Z";
    // keep what lies outside the card rect visible too (frame minus revealed area)
    s += rs.map(function (r) { return "M" + r1(r[0]) + "," + r1(r[1]) + "h" + r1(r[2]) + "v" + r1(Math.max(0, r[3] - 0.75)) + "h" + r1(-r[2]) + "Z"; }).join("");
    return 'path(evenodd,"' + s + '")';
  }
  function wipeOpt(k) { return { variant: k % 3, seed: k + 1, s: 1 }; }
  function wipeP(f, f0) { return FX.wipeProgress(f, f0, D.wipeDur); }

  function setVis(el, on) { el.style.visibility = on ? "visible" : "hidden"; }

  /* ---- DOM layers */
  function renderDom(f) {
    // whole-frame push into the charge
    var push = usePush ? 1 + D.charge.push * E_IN(cl((f - SP0) / (LAST - SP0))) : 1;
    stage.style.transform = push === 1 ? "none" : "scale(" + push.toFixed(5) + ")";
    // hairline: draws L->R f0-12, holds through Act 1, leaves with the shutter
    var hx = E_OUT(cl(f / D.coldOpen.hairDur)), ho = 1 - E_IN(cl((f - SH0) / 6));
    hair.style.transform = "scaleX(" + hx.toFixed(4) + ")"; hair.style.opacity = ho; setVis(hair, f < SH0 + 6);
    // cold-open label (fades on at f6) - wiped away by R1's brush
    label.style.opacity = (0.7 * E_OUT(cl((f - D.coldOpen.labelF) / 8))).toFixed(3);
    var p1 = wipeP(f, R[0].f_in);
    setVis(card0, p1 < 1);
    card0.style.clipPath = p1 > 0 ? clipOut(CARD, p1, wipeOpt(0)) : "none";
    // roster cards
    for (var k = 0; k < NR; k++) {
      var c = cards[k], r = c.r, nextF = k + 1 < NR ? R[k + 1].f_in : null;
      var pin = wipeP(f, r.f_in), on = f >= r.f_in;
      var pout = nextF != null ? wipeP(f, nextF) : 0;
      var gone = nextF != null ? pout >= 1 : f >= SH0 + 1; // R8 hands its window to the shutter on f223
      setVis(c.el, on && !gone);
      if (!on || gone) continue;
      if (pin < 1) c.el.style.clipPath = clipIn(CARD, pin, wipeOpt(k));
      else if (pout > 0) c.el.style.clipPath = clipOut(CARD, pout, wipeOpt(k + 1));
      else c.el.style.clipPath = "none";
      c.hold.style.opacity = f >= r.f_out ? 1 : 0;
      // outline name: 80 px L->R over its slot, linear (keeps drifting while it is wiped out)
      var dx = D.name.x0 + D.name.slide * (f - r.f_in) / (r.f_out - r.f_in);
      var exitA = 1;
      if (k === NR - 1 && f >= SH0) { var pe = cl((f - SH0) / 4); exitA = 1 - E_IN(pe); dx += 60 * E_IN(pe); }
      c.name.style.transform = "translateX(" + dx.toFixed(2) + "px)";
      c.name.style.opacity = exitA; c.tags.style.opacity = exitA;
    }
    // spectrum shutter f223-236
    var shOn = f >= SH0 && f < CL0;
    setVis(shutter, shOn);
    if (shOn) {
      var sh = WIN1[3] / NR, cy = WIN1[1] + WIN1[3] / 2;
      var pa = E_OUT(cl((f - SH0) / 4));            // gaps open
      var pb = E_IN(cl((f - D.shutter.tighten) / (SH1 - D.shutter.tighten))); // tighten to the centre line
      for (var j = 0; j < NR; j++) {
        var S = slivers[j];
        var h0 = sh - 8 * pa, yc0 = WIN1[1] + sh * (j + 0.5);
        var h = h0 + (D.shutter.lineH - h0) * pb;
        var yc = yc0 + (cy + (j - 3.5) * (D.shutter.lineH + 2) - yc0) * pb;
        S.el.style.transform = "translateY(" + (yc - h / 2).toFixed(2) + "px)";
        S.el.style.height = h.toFixed(2) + "px";
        S.img.style.transform = "translateY(" + (-(sh * j + sh / 2 - h / 2)).toFixed(2) + "px)";
        // strobe: each sliver flashes its hue on the beat, top -> bottom, 1 frame apart
        var fs = f - (SH0 + j * D.shutter.stagger);
        var flash = fs < 0 ? 0 : 1 - E_OUT(cl(fs / 4));
        var tint = Math.max(flash * 0.85, pb);
        S.tint.style.opacity = tint.toFixed(3);
        S.el.style.boxShadow = pb > 0 ? "0 0 " + (40 * pb).toFixed(1) + "px " + (8 * pb).toFixed(1) + "px " + FX.rgba(R[j].hue, 0.6 * pb) : "none";
      }
    }
    // Act 2 window: slams open from the shutter line bundle in 3 f (expo-out)
    var w2on = f >= CL0;
    setVis(win2, w2on);
    if (w2on) {
      var bundle = NR * (D.shutter.lineH + 2);
      var po = E_OUT(cl((f - CL0) / D.clash.slam));
      var ins = (WIN2[3] - bundle) / 2 * (1 - po);
      win2.style.clipPath = "inset(" + ins.toFixed(2) + "px 0px " + ins.toFixed(2) + "px 0px)";
    }
  }

  /* ---- background canvas: dust + roster plume (plume is brush-wiped with the cards) */
  function plumeAt(ctx, f, hex, a) { if (a > 0.001) FX.plume(ctx, f, hex, { opacity: D.plume.opacity * a, seed: 3 }); }
  function renderBg(f) {
    bg.setTransform(1, 0, 0, 1, 0, 0); bg.clearRect(0, 0, bgC.width, bgC.height);
    bg.setTransform(fxScale, 0, 0, fxScale, 0, 0);
    // plume of the current fighter, faded out across the shutter, gone in Act 2 (true colour)
    var fadeOut = 1 - E_IN(cl((f - SH0) / (SH1 - SH0)));
    var k = -1;
    for (var i = 0; i < NR; i++) if (f >= R[i].f_in) k = i;
    if (k >= 0 && f < CL0) {
      var p = wipeP(f, R[k].f_in);
      if (p >= 1) plumeAt(bg, f, R[k].hue, fadeOut);
      else {
        var full = [0, 0, D.W, D.H], o = wipeOpt(k);
        // matte on its own cleared canvas, applied ONCE (kit rule: never draw brushMatte in destination-in mode)
        var mc = tmpM.getContext("2d");
        mc.setTransform(1, 0, 0, 1, 0, 0); mc.globalCompositeOperation = "source-over"; mc.clearRect(0, 0, tmpM.width, tmpM.height);
        mc.setTransform(fxScale, 0, 0, fxScale, 0, 0);
        FX.brushMatte(mc, full, p, o);
        [tmpA, tmpB].forEach(function (t, n) {
          var c = t.getContext("2d");
          c.setTransform(1, 0, 0, 1, 0, 0); c.globalCompositeOperation = "source-over"; c.clearRect(0, 0, t.width, t.height);
          c.setTransform(fxScale, 0, 0, fxScale, 0, 0);
          if (n === 0 && k > 0) plumeAt(c, f, R[k - 1].hue, 1);
          if (n === 1) plumeAt(c, f, R[k].hue, 1);
          c.setTransform(1, 0, 0, 1, 0, 0);
          c.globalCompositeOperation = n === 0 ? "destination-out" : "destination-in";
          c.drawImage(tmpM, 0, 0);
        });
        bg.setTransform(1, 0, 0, 1, 0, 0);
        bg.drawImage(tmpA, 0, 0); bg.drawImage(tmpB, 0, 0);
        bg.setTransform(fxScale, 0, 0, fxScale, 0, 0);
      }
    }
    FX.dust(bg, f, { count: D.dust.count, seed: 5, opacity: D.dust.opacity, inFrom: [0, D.coldOpen.end] });
  }

  /* ---- foreground canvas: brush fringes + light streaks */
  function streakPts(k, f, trail) {
    var pts = [], t0 = Math.max(CL0, f - trail);
    for (var t = t0; t <= f + 1e-6; t += 0.125) pts.push(ST.pos(k, t, E_OUT, useSpirals));
    return pts;
  }
  function renderFg(f) {
    fg.setTransform(1, 0, 0, 1, 0, 0); fg.clearRect(0, 0, fgC.width, fgC.height);
    fg.setTransform(fxScale, 0, 0, fxScale, 0, 0);
    // fringe on the leading edge of each roster wipe (inside the window only)
    for (var k = 0; k < NR; k++) {
      var p = wipeP(f, R[k].f_in);
      if (p > 0 && p < 1) {
        fg.save(); fg.beginPath(); fg.rect(WIN1[0], WIN1[1], WIN1[2], WIN1[3]); fg.clip();
        FX.brushFringe(fg, CARD, p, R[k].hue, wipeOpt(k));
        fg.restore();
      }
    }
    // 8 coloured light streaks: burst from the shutter lines (f237), orbit the window, spiral in (f336-356)
    if (f >= CL0 && (f < SP0 || useSpirals)) {
      var charge = cl((f - SP0) / (LAST - SP0));
      for (var j = 0; j < NR; j++) {
        var pts = streakPts(j, f, D.streakTrail);
        if (pts.length < 2) continue;
        var n = pts.length, thirds = [[0, Math.ceil(n / 3)], [Math.floor(n / 3), Math.ceil(2 * n / 3)], [Math.floor(2 * n / 3), n - 1]];
        var al = [0.22, 0.5, 1], cw = [6, 9, 12 + 2 * charge];
        for (var q = 0; q < 3; q++) {
          var seg = pts.slice(thirds[q][0], thirds[q][1] + 1);
          FX.glowStroke(fg, seg, R[j].hue, { core: cw[q], glow: 48 + 30 * charge, alpha: al[q], whiteCore: q === 2 });
        }
        var hd = pts[n - 1];
        FX.glow(fg, hd[0], hd[1], 70 + 50 * charge, R[j].hue, 0.55);
      }
    }
  }

  function render(f) {
    f = Math.max(0, Math.min(LAST, f));
    renderDom(f); renderBg(f); renderFg(f);
  }
  var clock = { t: 0 };
  var tl = gsap.timeline({ paused: true });
  tl.to(clock, { t: D.duration, duration: D.duration, ease: "none",
    onUpdate: function () { render(Math.round(clock.t * D.fps)); } }, 0);
  render(0);
  window.__mg1Render = render;
  window.__timelines["mg1"] = tl;
})();
