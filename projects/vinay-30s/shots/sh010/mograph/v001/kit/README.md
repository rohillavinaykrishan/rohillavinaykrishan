# SPECTRUM FX kit v001 (shared by MG1 / MG2 / MG3)

Everything is drawn by `kit.js`: seeded, a pure function of the master frame, no `Math.random`,
`Date` or `requestAnimationFrame`. It is crisp at any size because it is drawn at the canvas's native
resolution. Units are **master frames (25 fps)** and **4K pixels (2160x3840)**. When you draw at proxy size, pass
`s = canvas.width / 2160` (540 wide gives `s: 0.25`). Demo sheet: `review/fx_kit_v001.png`.

| File | What |
|---|---|
| `kit.js` | the kit (UMD: `<script src>` gives `window.FX`; in node, `require('./kit.js')`). **Generated**, do not edit |
| `kit_src.js` + `make_kit.py` | source + builder; it inlines `director/v001/cues.json` because HyperFrames forbids fetch. **Re-run `python3 make_kit.py` whenever cues.json changes** |
| `bake.js` | bakes `png/**` and the demo sheet from kit.js (headless Chrome), `node bake.js` |
| `png/wipes/{win,tile}_{dry,wet,split}_{matte,fringe}_01..05.png` | brush wipe frames +1..+5 (frame +0 = nothing, >= +6 = full). `win` = 2160x904, `tile` = 482x430. White on alpha |
| `png/glows/glow_<fighter>.png` | 256 px soft radial glow per fighter hue + `whitehot`, `gold` (blend: screen/add) |
| `png/lightpoint/lightpoint_f357..f364.png` | the silence point, 256x256, 4K-native size, breathing 1.0 to 1.15, fringe rotating 15 deg/f, centre at (128,128) |
| `png/sprites/dust_mote.png`, `spark_streak.png` | white sprites, tint them with a CSS mask + background-color |

## Load in a HyperFrames comp
Copy or symlink the kit into your project's `assets/kit/` (asset paths must be root-relative):
```bash
ln -s ../../kit assets/kit     # or: cp -r ../kit assets/kit
```
```html
<script src="assets/kit/kit.js"></script>
<canvas id="fx" width="2160" height="3840" style="position:absolute;inset:0;width:100%;height:100%"></canvas>
<script>
  // startFrame = master frame at this composition's t = 0 -> draw() always receives master frames
  FX.mount(document.getElementById("fx"), function (ctx, f, t, s) {
    FX.plume(ctx, f, FX.hue("Ryu"), { s: s, opacity: 0.25 });
    FX.dust(ctx, f, { s: s, inFrom: [0, 18] });
  }, { startFrame: 0 });
</script>
```
`FX.mount` hooks `hf-seek` and redraws from scratch every frame. For a 540 proxy, use `width=540 height=960`;
`s` is then 0.25 automatically.

## Eases and beats
```js
FX.ease.out(x)              // cubic-bezier(0.16,1,0.3,1): entrances
FX.ease.in(x)               // cubic-bezier(0.7,0,0.84,0): exits
FX.ease.linear(x)           // ambient drift only
FX.ease.outOver(x, 0.04)    // ease.out + overshoot peaking at 1+amt: name strike 0.04, logo slam 0.03
FX.prog(f, f0, dur, FX.ease.out)  // eased 0..1 progress of an animation starting at f0
FX.beat("S3", 0)            // 365  (sections S1..S4, 0-based; -1 = last; fractional ok)
FX.beats("S1")              // [6,19,33,...]
FX.beatLength("S2")         // 17.4
FX.beatAt(370)              // {f:365, section:"S3", n:0, next:376, since:5, phase:0.45}
FX.event("HIT").f           // 365; FX.event("TITLE_STINGER").f = 686
FX.shot("R3"), FX.shot("T5")  // cue rows (f_in/f_out/hue..., tiles: rect_4k, arrive_f)
FX.layout.act1_window       // [0,1048,2160,904] (all of layout_4k)
FX.palette.whiteHot / .bone / .gold / .goldDeep / .ink / .inkRaised / .smoke
FX.hues                     // [{i,name,hex,rgb}] x8 in wheel order (Ryu..E. Honda)
FX.hue("Ken") | FX.hue(1) | FX.hue("R2") | FX.hue("T2")  // "#FF5E1A"
FX.rng(seed)                // mulberry32 -> () => 0..1   ;  FX.noise1(x, seed)
```

## Ink-brush wipe (6 f, L to R, 40 px fringe in the arriving hue)
Canvas route (simplest: draw the new layer through the matte):
```js
// f0 = the cut frame, e.g. FX.shot("R2").f_in; rect = FX.layout.act1_window (scale by s at proxy)
FX.brushWipe(ctx, f, f0, rect, FX.hue("Ken"), function (t) { /* draw the NEW content into t */ },
             { variant: 0, seed: 2, s: s });     // variant 0 dry | 1 wet | 2 split
```
Low-level: `FX.wipeProgress(f, f0, 6)` gives `p`, then `FX.brushMatte(mctx, rect, p, opt)` (draw source-over onto its
**own cleared canvas**, then apply that canvas once with `destination-in`; never draw brushMatte straight in
`destination-in` mode, because every bristle row would erase the rest), then `FX.brushFringe(ctx, rect, p, hex, opt)` (additive).
For a different look per fighter, vary `seed`; matte and fringe line up when they get the same `opt`.

HTML/video route (no canvas): mask the new plate's wrapper with the baked frames:
```js
// frames +1..+5 use the PNG; at +6 drop the mask. Fringe: a div with background:<hue>, same mask on fringe_XX, mix-blend-mode:screen
for (let k = 1; k <= 5; k++) tl.set(wrap, { maskImage: `url(assets/kit/png/wipes/win_dry_matte_0${k}.png)`, webkitMaskImage: `url(assets/kit/png/wipes/win_dry_matte_0${k}.png)` }, (f0 + k - start) / 25);
tl.set(wrap, { maskImage: "none", webkitMaskImage: "none" }, (f0 + 6 - start) / 25);
```
(`mask-size: 100% 100%`; the `tile_*` set is for 482x430 tiles.)

## Colour plumes and glows
```js
FX.plume(ctx, f, FX.hue("Guile"), { s, opacity: 0.25, seed: 3 })  // breathes from the frame edges, loops every 100 f (4 s)
FX.glow(ctx, x, y, r, hex, alpha)                                  // soft additive radial glow
```
To crossfade hues across an Act-1 wipe, draw the old plume at `1-p` and the new one at `p` (`opacity: 0.25*p`).

## Dust
```js
FX.dust(ctx, f, { s, inFrom: [0, 18] })          // cold open: 8-colour motes fly in from the edges
FX.dust(ctx, f, { s, count: 60, opacity: 0.4 })  // ambient hold (f687-749); hues: [FX.palette.gold] to restrict
```

## Sparks (strike, section 6)
```js
const C = [1080, 1550], origins = FX.hues.map((h, k) => {
  const a = -Math.PI / 2 + (22.5 + 45 * k) * Math.PI / 180;     // ray k direction
  return { x: C[0] * s + Math.cos(a) * 60 * s, y: C[1] * s + Math.sin(a) * 60 * s, hex: h.hex, dir: a, spread: 0.9 };
});
FX.sparks(ctx, f, { f0: 365, origins, count: 220, seed: 9, s,
                    life: [8, 20], gravity: 1800, drag: 0.08 })   // analytic: any frame, any order
```
(Scale `x`/`y` by `s` yourself; speeds/gravity/widths are scaled by `s` internally.)

## Light point (silence f357-364)
```js
FX.lightPoint(ctx, 1080 * s, 1550 * s, f, { s, scale: 1 + 0.15 * FX.prog(f, 357, 7) })
```
Or `<img src="assets/kit/png/lightpoint/lightpoint_f360.png">`, 256 px centred on (1080,1550) at 4K
(left 952, top 1422), blend screen. The core is drawn source-over in exact White Hot `#FFF8EC`.

## Glow strokes (rays, orbit streaks, spirals)
```js
FX.glowStroke(ctx, [[x0,y0],[x1,y1],...], hex, { s, core: 18, glow: 120, alpha: a })  // additive, White Hot core
```

## Blend modes for the comp
Everything that is light (fringe, plume, glow, dust, sparks, point, strokes) is additive: canvas `lighter`,
CSS `mix-blend-mode: screen` (or `plus-lighter`) over ink. Mattes are alpha masks, not visible layers.
