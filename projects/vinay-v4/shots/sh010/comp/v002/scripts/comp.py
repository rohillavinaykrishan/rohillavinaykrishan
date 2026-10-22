#!/usr/bin/env python3
"""sh010 FINAL comp v002 (treatment 9.5 + director note 18), at 2808x1176.

Inputs (all relative to shots/sh010):
  comp/v002/work/plate_up/plate.%04d.png   graded plate v002, lanczos 2.19x + cas 0.55 (comp.sh step 1)
  comp/v002/work/{cg,shadow,mist}_d/        lighting v002 passes, lens-distorted by layout distort.py (step 2)
  comp/v002/work/grain/grain.%04d.png      colorist grain (noise c0s=5:c0f=t) on 50% grey, same upscale (step 3)
  roto/v001/matte/matte.%04d.png           person holdout (white = person), 2560x1072
Frame numbering everywhere: 0000-0051 = s0-s51.

Per frame:
  CG  -> [optional grade LUT] -> premult gblur sigma 0.7 + chroma blur -> black lift to Ink -> 3% mist haze
      -> holdout a *= (1 - matte)
  shadow: d = 1 - luma(shadow); d' = min(d * GAIN, DMAX); Umber-tinted multiplier, linear light, held out by the matte
  over, light wrap (blurred plate on the CG's inner edge), rim bloom (top 8% CG luma, blur 12, screen 35%),
  luma-only grain on the CG.
Writes work/final/final.%04d.png (8-bit RGB 2808x1176), work/cgband/cg.%04d.png (CG + shadow over #6E665C).
"""
import os, sys, argparse
import numpy as np, cv2

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))  # shots/sh010
W, H = 2808, 1176
INK = np.array([0x12, 0x10, 0x0D], np.float32) / 255.0          # RGB
GREY = np.array([0x6E, 0x66, 0x5C], np.float32) / 255.0
UMBER_W = np.array([1.19, 0.96, 0.77], np.float32)               # sqrt of Umber #3A2E24 chroma ratio (linear)

ap = argparse.ArgumentParser()
ap.add_argument('--frames', default='0-51')
ap.add_argument('--out', default=os.path.join(ROOT, 'comp/v002/work'))
ap.add_argument('--matte', default=os.path.join(ROOT, 'roto/v001/matte/matte.%04d.png'))
ap.add_argument('--lut', default=os.path.join(ROOT, 'color/v002/sunbleach_v002.cube'))
ap.add_argument('--grade-cg', type=float, default=0.4, help='mix of the plate grade LUT on the CG (0 = off)')
ap.add_argument('--blur', type=float, default=0.7)
ap.add_argument('--chroma-blur', type=float, default=1.4)
ap.add_argument('--haze', type=float, default=0.03, help='mean haze mix on the monument')
ap.add_argument('--shadow-gain', type=float, default=1.17)
ap.add_argument('--shadow-max', type=float, default=0.78)
ap.add_argument('--wrap', type=float, default=0.04, help='light wrap amount (mean luminance gain on the monument)')
ap.add_argument('--wrap-sigma', type=float, default=3.0)
ap.add_argument('--wrap-edge', type=float, default=0.3, help='edge opacity of the wrap screen')
ap.add_argument('--bloom-thr', type=float, default=None, help='CG luma threshold; default = top 8%% (fixed, measured)')
ap.add_argument('--bloom-blur', type=float, default=12)
ap.add_argument('--bloom-mix', type=float, default=0.35)
ap.add_argument('--grain', type=float, default=1.0)
ap.add_argument('--tag', default='')
ap.add_argument('--solid-frames', default='1-4', help='fall frames whose motion-blurred alpha is shaped to read solid')
ap.add_argument('--solid-target', type=float, default=0.95, help='median alpha on the monument after shaping')
ap.add_argument('--dump-layer', default='4,25,38,48', help='frames for which the held-out CG layer (RGBA) is written for QC')
a = ap.parse_args()

def srgb2lin(x): return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)
def lin2srgb(x):
    x = np.clip(x, 0, None); return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)
def luma(rgb): return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
def rd(p, flag=cv2.IMREAD_UNCHANGED):
    im = cv2.imread(p, flag)
    if im is None: sys.exit('cannot read ' + p)
    return im
def to_f(im):
    m = 65535.0 if im.dtype == np.uint16 else 255.0
    return im.astype(np.float32) / m
def screen(x, y): return 1 - (1 - x) * (1 - y)

def load_cube(p):
    n, rows = None, []
    for ln in open(p):
        t = ln.strip().split()
        if not t or t[0].startswith('#'): continue
        if t[0] == 'LUT_3D_SIZE': n = int(t[1]); continue
        if t[0][0].isalpha(): continue
        rows.append([float(v) for v in t[:3]])
    return n, np.array(rows, np.float32).reshape(n, n, n, 3)  # [b][g][r] (red fastest)

def apply_lut(rgb, n, lut):
    x = np.clip(rgb, 0, 1) * (n - 1); i0 = np.floor(x).astype(np.int32); i0 = np.minimum(i0, n - 2); f = x - i0
    r0, g0, b0 = i0[:, 0], i0[:, 1], i0[:, 2]; fr, fg, fb = f[:, 0:1], f[:, 1:2], f[:, 2:3]
    out = 0
    for db in (0, 1):
        for dg in (0, 1):
            for dr in (0, 1):
                w = (fr if dr else 1 - fr) * (fg if dg else 1 - fg) * (fb if db else 1 - fb)
                out = out + w * lut[b0 + db, g0 + dg, r0 + dr]
    return out

N_LUT, LUT = load_cube(a.lut)
S, E = map(int, a.frames.split('-'))
os.makedirs(os.path.join(a.out, 'final'), exist_ok=True); os.makedirs(os.path.join(a.out, 'cgband'), exist_ok=True)
wk = os.path.join(ROOT, 'comp/v002/work')

# fixed bloom threshold = 92nd percentile of the CG luma on the landed monument (s5-s51), measured once
thr = a.bloom_thr
if thr is None:
    vals = []
    for i in range(5, 52, 6):
        c = to_f(rd(f'{wk}/cg_d/cg.{i:04d}.png')); al = c[..., 3]; px = c[..., 2::-1][al > 0.9]
        if a.grade_cg > 0: px = px * (1 - a.grade_cg) + apply_lut(px, N_LUT, LUT) * a.grade_cg
        vals.append(luma(INK + px * (1 - INK)))
    thr = float(np.percentile(np.concatenate(vals), 92))
print('bloom threshold (display luma, graded) %.3f' % thr, flush=True)

# haze colour = the plate's bright sky (s25 top rows), measured once
sky = to_f(rd(f'{wk}/plate_up/plate.0025.png'))[:120, 1600:2600, ::-1].reshape(-1, 3)
HAZE = np.median(sky, axis=0).astype(np.float32)

for i in range(S, E + 1):
    plate = to_f(rd(f'{wk}/plate_up/plate.{i:04d}.png'))[..., ::-1].copy()          # RGB 0-1
    cg = to_f(rd(f'{wk}/cg_d/cg.{i:04d}.png')); al = cg[..., 3].copy(); rgb = cg[..., 2::-1].copy()
    sh = to_f(rd(f'{wk}/shadow_d/shadow.{i:04d}.png'))[..., 2::-1]
    mist = to_f(rd(f'{wk}/mist_d/mist.{i:04d}.png', cv2.IMREAD_ANYDEPTH))
    gr = rd(f'{wk}/grain/grain.{i:04d}.png', cv2.IMREAD_ANYDEPTH).astype(np.float32) / 257.0 - 128.0
    gr = (gr - gr.mean()) / 255.0
    mt = to_f(rd(a.matte % i, cv2.IMREAD_GRAYSCALE))
    if mt.shape != (H, W): mt = cv2.resize(mt, (W, H), interpolation=cv2.INTER_LINEAR)
    mt = np.clip(mt, 0, 1)

    # ---- fall frames (s1-s4): the render's vertical motion blur leaves the letters ~55-75% opaque (ghosted).
    #      a' = 1-(1-a)^k, k from the frame's median alpha, so the body reads solid and the smear keeps its length.
    s0, s1 = map(int, a.solid_frames.split('-'))
    if s0 <= i <= s1:
        p50 = float(np.median(al[al > 0.02]))
        if p50 < a.solid_target:
            k = float(np.clip(np.log(1 - a.solid_target) / np.log(max(1e-3, 1 - p50)), 1, 4))
            al = 1 - (1 - al) ** k
            print('  solid s%d: median alpha %.2f -> k %.2f' % (i, p50, k), flush=True)

    # ---- CG degrade (straight colour where alpha > 0) ----
    m = al > 1e-4
    if a.grade_cg > 0 and m.any():
        g = apply_lut(rgb[m], N_LUT, LUT)
        rgb[m] = rgb[m] * (1 - a.grade_cg) + g * a.grade_cg
    pm = np.dstack([rgb * al[..., None], al])
    pm = cv2.GaussianBlur(pm, (0, 0), a.blur)
    al = np.clip(pm[..., 3], 0, 1)
    rgb = np.where(al[..., None] > 1e-4, pm[..., :3] / np.maximum(al[..., None], 1e-4), 0)
    ycc = cv2.cvtColor(np.clip(rgb, 0, 1).astype(np.float32), cv2.COLOR_RGB2YCrCb)
    for ch in (1, 2):   # chroma blur, weighted by alpha so the edge does not pull in black
        num = cv2.GaussianBlur(ycc[..., ch] * al, (0, 0), a.chroma_blur); den = cv2.GaussianBlur(al, (0, 0), a.chroma_blur)
        ycc[..., ch] = np.where(den > 1e-3, num / np.maximum(den, 1e-3), ycc[..., ch])
    rgb = cv2.cvtColor(ycc, cv2.COLOR_YCrCb2RGB)
    rgb = INK + rgb * (1 - INK)                                              # black lift to Ink
    hz = np.clip(mist * (a.haze / 0.53), 0, 2 * a.haze)[..., None]          # mist ~0.53 on the monument -> 3%
    rgb = rgb * (1 - hz) + HAZE * hz

    # ---- holdout: fighters always in front ----
    alh = al * (1 - mt)

    # ---- shadow: Umber-tinted, density gain, linear light, held out ----
    d = 1 - luma(sh)
    d2 = np.clip(d * a.shadow_gain, 0, a.shadow_max)
    t = (1 - 0.25 * UMBER_W) / 0.75
    mul = np.clip(1 - d2[..., None] * t, 0, 1)
    mul = 1 - (1 - mul) * (1 - mt[..., None])
    bg = lin2srgb(srgb2lin(plate) * mul)

    # ---- over ----
    out = bg * (1 - alh[..., None]) + rgb * alh[..., None]

    # ---- light wrap: blurred background screened onto the monument's inner edge ----
    bgb = cv2.GaussianBlur(bg, (0, 0), 10)
    edge = np.clip(al * (1 - cv2.GaussianBlur(al, (0, 0), a.wrap_sigma)) * 2.0, 0, 1)
    wrap_op = np.clip(a.wrap + a.wrap_edge * edge, 0, 1) * (1 - mt)
    wrapped = screen(out, bgb)
    out = out + (wrapped - out) * (wrap_op * al)[..., None]

    # ---- rim bloom: top 8% CG luma, blur 12, screen 35% (held out) ----
    lm = luma(rgb)
    hi = np.clip((lm - thr) / max(1e-3, 1 - thr), 0, 1) ** 0.75 * alh
    bl = cv2.GaussianBlur(rgb * hi[..., None], (0, 0), a.bloom_blur)
    out = screen(out, np.clip(bl * a.bloom_mix, 0, 1))

    # ---- luma-only grain on the CG (the plate already carries the colorist's grain) ----
    out = out + (gr * a.grain * alh)[..., None]
    out = np.clip(out, 0, 1)
    if str(i) in a.dump_layer.split(','):
        os.makedirs(f'{a.out}/cglayer', exist_ok=True)
        lay = np.dstack([np.clip(rgb + (gr * a.grain)[..., None], 0, 1), alh])
        cv2.imwrite(f'{a.out}/cglayer/cg.{i:04d}.png', (lay[..., [2, 1, 0, 3]] * 65535 + 0.5).astype(np.uint16))
    cv2.imwrite(f'{a.out}/final/final{a.tag}.{i:04d}.png', (out[..., ::-1] * 255 + 0.5).astype(np.uint8))

    # ---- CG band: monument + its shadow over warm 18% grey (no holdout, no plate) ----
    gmul = np.clip(1 - d2[..., None] * t, 0, 1)
    gbg = lin2srgb(srgb2lin(np.broadcast_to(GREY, out.shape)) * gmul)
    cgb = gbg * (1 - al[..., None]) + rgb * al[..., None]
    cgb = screen(cgb, np.clip(cv2.GaussianBlur(rgb * (np.clip((lm - thr) / max(1e-3, 1 - thr), 0, 1) ** 0.75 * al)[..., None], (0, 0), a.bloom_blur) * a.bloom_mix, 0, 1))
    cgb = np.clip(cgb + (gr * a.grain * al)[..., None], 0, 1)
    cv2.imwrite(f'{a.out}/cgband/cg{a.tag}.{i:04d}.png', (cgb[..., ::-1] * 255 + 0.5).astype(np.uint8))
    print('frame', i, 'shadow dmax %.3f' % d2.max(), flush=True)
