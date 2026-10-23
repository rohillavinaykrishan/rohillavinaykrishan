#!/usr/bin/env node
/* Bakes the kit's PNG assets AND the review demo sheet from kit.js itself
 * (so baked PNGs == live canvas code). Headless Chrome via puppeteer-core.
 *   node bake.js            -> kit/png/** + ../../../../../review/fx_kit_v001.png
 * Env: PUPPETEER_CORE, CHROME (defaults below). */
const fs = require("fs"), path = require("path");
const PC = process.env.PUPPETEER_CORE || "/root/.npm/_npx/702923228c2ce1e6/node_modules/puppeteer-core";
const CHROME = process.env.CHROME || "/root/.cache/hyperframes/chrome/chrome-headless-shell/linux-152.0.7977.30/chrome-headless-shell-linux64/chrome-headless-shell";
const puppeteer = require(PC);
const KIT = __dirname;
const REVIEW = path.resolve(KIT, "../../../../../review");

function save(rel, dataUrl) {
  const p = path.isAbsolute(rel) ? rel : path.join(KIT, "png", rel);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, Buffer.from(dataUrl.split(",")[1], "base64"));
  return p;
}

(async () => {
  const browser = await puppeteer.launch({ executablePath: CHROME, args: ["--no-sandbox", "--disable-gpu"] });
  const page = await browser.newPage();
  await page.setContent("<html><body style='margin:0;background:#000'></body></html>");
  await page.addScriptTag({ path: path.join(KIT, "kit.js") });
  page.on("console", (m) => console.log("[page]", m.text()));

  /* ---------- bake assets ---------- */
  const assets = await page.evaluate(() => {
    const out = {};
    const C = (w, h) => { const c = document.createElement("canvas"); c.width = w; c.height = h; return c; };
    const names = ["dry", "wet", "split"];
    // brush mattes + fringes: Act-1/3 window (2160x904) and tile (482x430); frames 1..5 (frame 0 empty, >=6 full)
    [[2160, 904, "win"], [482, 430, "tile"]].forEach(([w, h, tag]) => {
      for (let v = 0; v < 3; v++) for (let k = 1; k <= 5; k++) {
        const p = FX.ease.out(k / 6);
        let c = C(w, h), x = c.getContext("2d");
        FX.brushMatte(x, [0, 0, w, h], p, { variant: v, seed: 1 });
        out[`wipes/${tag}_${names[v]}_matte_${String(k).padStart(2, "0")}.png`] = c.toDataURL();
        c = C(w, h); x = c.getContext("2d");
        FX.brushFringe(x, [0, 0, w, h], p, "#FFFFFF", { variant: v, seed: 1, composite: "source-over" });
        out[`wipes/${tag}_${names[v]}_fringe_${String(k).padStart(2, "0")}.png`] = c.toDataURL();
      }
    });
    // light point, f357-364 (silence), breathing 1.0 -> 1.15, 256x256 centred, native 4K size
    for (let f = 357; f <= 364; f++) {
      const c = C(256, 256), x = c.getContext("2d");
      FX.lightPoint(x, 128, 128, f, { scale: 1 + 0.15 * (f - 357) / 7 });
      out[`lightpoint/lightpoint_f${f}.png`] = c.toDataURL();
    }
    // soft glows: one per fighter colour + White Hot + Gold (256, additive / screen)
    const glowSet = FX.hues.map((h) => [h.name.replace(/[^A-Za-z]/g, "").toLowerCase(), h.hex])
      .concat([["whitehot", FX.palette.whiteHot], ["gold", FX.palette.gold]]);
    glowSet.forEach(([n, hex]) => {
      const c = C(256, 256), x = c.getContext("2d");
      FX.glow(x, 128, 128, 128, hex, 1, "source-over");
      out[`glows/glow_${n}.png`] = c.toDataURL();
    });
    // sprites (white, tint with CSS mask + background-color)
    let c = C(64, 64); c.getContext("2d").drawImage(FX.dotSprite("#FFFFFF", 64, 0.18), 0, 0);
    out["sprites/dust_mote.png"] = c.toDataURL();
    c = C(160, 32); let x = c.getContext("2d");
    FX.glowStroke(x, [[16, 16], [144, 16]], "#FFFFFF", { core: 6, glow: 26, composite: "source-over", whiteCore: false });
    out["sprites/spark_streak.png"] = c.toDataURL();
    return out;
  });
  let n = 0;
  for (const [rel, d] of Object.entries(assets)) { save(rel, d); n++; }
  console.log("baked", n, "pngs");

  /* ---------- demo sheet ---------- */
  const sheet = await page.evaluate(() => {
    const SW = 2400, SH = 3400;
    const sc = document.createElement("canvas"); sc.width = SW; sc.height = SH;
    const S = sc.getContext("2d");
    const P = FX.palette;
    S.fillStyle = P.ink; S.fillRect(0, 0, SW, SH);
    const label = (t, x, y, size, col) => { S.font = `700 ${size || 30}px monospace`; S.fillStyle = col || P.bone; S.fillText(t, x, y); };
    const C = (w, h) => { const c = document.createElement("canvas"); c.width = w; c.height = h; return c; };
    label("SPECTRUM FX KIT v001  -  shots/sh010/mograph/v001/kit  -  all drawn live by kit.js at 4K, shown scaled", 40, 60, 34, P.whiteHot);

    // A. brush wipes: 3 variants x frames 1..5 (Act-1 window 2160x904 at 4K, cell scale 0.2)
    let y = 110;
    label("A  INK-BRUSH WIPES  FX.brushWipe / brushMatte + brushFringe   (6 f, ease.out, L->R; old = Ryu plate, new = Guile)", 40, y, 28); y += 20;
    const names = ["dry (0)", "wet (1)", "split (2)"];
    const win = C(2160, 904), wx = win.getContext("2d");
    const plate = (ctx, hex, w, h) => {
      const g = ctx.createLinearGradient(0, 0, w, h);
      g.addColorStop(0, P.ink); g.addColorStop(0.5, FX.mixHex(P.ink, hex, 0.8)); g.addColorStop(1, FX.mixHex(hex, P.whiteHot, 0.5));
      ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
      ctx.fillStyle = "rgba(7,6,10,0.5)"; for (let i = 0; i < 6; i++) ctx.fillRect(200 + i * 330, 250, 120, 500);
    };
    for (let v = 0; v < 3; v++) {
      for (let k = 1; k <= 5; k++) {
        wx.globalCompositeOperation = "source-over"; wx.clearRect(0, 0, 2160, 904);
        plate(wx, FX.hue("Ryu"), 2160, 904);
        FX.brushWipe(wx, 100 + k, 100, [0, 0, 2160, 904], FX.hue("Guile"), (t) => plate(t, FX.hue("Guile"), 2160, 904), { variant: v, seed: 1 });
        S.drawImage(win, 40 + (k - 1) * 468, y + 10, 432, 181);
        if (v === 0) label("frame +" + k, 40 + (k - 1) * 468, y + 225, 22);
      }
      label(names[v], 2390 - 160, y + 110, 26);
      y += 200;
    }
    y += 40;
    // A2. 100% crop of the fringe at 4K (crispness check)
    label("A2  100% 4K crop of the leading edge (dry, frame +2)  /  matte over WHITE (alpha check)", 40, y, 26); y += 14;
    wx.clearRect(0, 0, 2160, 904); plate(wx, FX.hue("Ryu"), 2160, 904);
    FX.brushWipe(wx, 102, 100, [0, 0, 2160, 904], FX.hue("Guile"), (t) => plate(t, FX.hue("Guile"), 2160, 904), { variant: 0, seed: 1 });
    S.drawImage(win, 1500, 200, 1100, 360, 40, y, 1100, 360);
    const m = C(2160, 904), mx = m.getContext("2d");
    mx.fillStyle = "#ffffff"; mx.fillRect(0, 0, 2160, 904);
    mx.globalCompositeOperation = "source-over";
    const mm = C(2160, 904); FX.brushMatte(mm.getContext("2d"), [0, 0, 2160, 904], FX.ease.out(1 / 6), { variant: 2, seed: 1, color: P.ink });
    mx.drawImage(mm, 0, 0);
    S.drawImage(m, 1180, y, 1180, 494);
    y += 520;

    // B. plumes, 8 hues (frame 9:16, s = 1/8 -> 270x480)
    label("B  COLOUR PLUMES  FX.plume(ctx, f, hex, {opacity:0.25})  -  8 fighter hues, 4 s seamless loop   + glow sprites (png/glows)", 40, y, 26); y += 16;
    const pc = C(270, 480), px = pc.getContext("2d");
    FX.hues.forEach((h, i) => {
      px.globalCompositeOperation = "source-over"; px.fillStyle = P.ink; px.fillRect(0, 0, 270, 480);
      FX.plume(px, 30 + i * 11, h.hex, { s: 270 / 2160, opacity: 0.25, seed: 3 });
      S.drawImage(pc, 40 + i * 292, y);
      label(h.name, 40 + i * 292, y + 510, 22, h.hex);
      FX.glow(S, 40 + i * 292 + 135, y + 600, 70, h.hex, 1);
    });
    y += 700;

    // C. dust + sparks + light point
    label("C  DUST  FX.dust (cold-open fly-in f6 / drift f200)     D  SPARKS  FX.sparks 220 from 8 ray roots (f365 +2/+6/+12)", 40, y, 26); y += 16;
    const dc = C(540, 960), dx = dc.getContext("2d");
    [[8, [0, 18]], [200, null]].forEach(([f, inF], i) => {
      dx.fillStyle = P.ink; dx.fillRect(0, 0, 540, 960);
      FX.dust(dx, f, { s: 0.25, inFrom: inF, size: [6, 16] });
      S.drawImage(dc, 40 + i * 300, y, 270, 480);
      label("f" + f, 40 + i * 300, y + 510, 22);
    });
    const sp = C(2160, 2160), sx = sp.getContext("2d");
    const cx = 1080, cy = 1080;
    const origins = FX.hues.map((h, k) => { const a = -Math.PI / 2 + (22.5 + 45 * k) * Math.PI / 180; return { x: cx + Math.cos(a) * 60, y: cy + Math.sin(a) * 60, hex: h.hex, dir: a, spread: 0.9 }; });
    [367, 371, 377].forEach((f, i) => {
      sx.fillStyle = P.ink; sx.fillRect(0, 0, 2160, 2160);
      FX.sparks(sx, f, { f0: 365, origins: origins, count: 220, seed: 9 });
      S.drawImage(sp, 640 + i * 500, y, 480, 480);
      label("f" + f, 640 + i * 500, y + 510, 22);
    });
    y += 560;
    label("E  LIGHT POINT  FX.lightPoint (f357-364, 24 px core, 80 px halo, 8-hue fringe 15 deg/f) at 300% / 100%, over ink and WHITE", 40, y, 26); y += 16;
    const lp = C(256, 256), lx = lp.getContext("2d");
    [357, 360, 364].forEach((f, i) => {
      lx.fillStyle = P.ink; lx.fillRect(0, 0, 256, 256);
      FX.lightPoint(lx, 128, 128, f, { scale: 1 + 0.15 * (f - 357) / 7 });
      S.imageSmoothingEnabled = false; S.drawImage(lp, 40 + i * 420, y, 384, 384); S.imageSmoothingEnabled = true;
      label("f" + f + " x3", 40 + i * 420, y + 414, 22);
    });
    lx.clearRect(0, 0, 256, 256); FX.lightPoint(lx, 128, 128, 360, { scale: 1.06 });
    S.fillStyle = "#ffffff"; S.fillRect(1320, y, 256, 256); S.drawImage(lp, 1320, y);
    S.fillStyle = P.ink; S.fillRect(1600, y, 256, 256); S.drawImage(lp, 1600, y);
    label("100% white / ink", 1320, y + 290, 22);
    // glow stroke sample
    FX.glowStroke(S, [[1900, y + 40], [2100, y + 200], [2350, y + 260]], FX.hue("Chun-Li"), { core: 10, glow: 60 });
    label("FX.glowStroke", 1900, y + 330, 22);
    return sc.toDataURL();
  });
  const sp = save(path.join(REVIEW, "fx_kit_v001.png"), sheet);
  console.log("sheet", sp);
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
