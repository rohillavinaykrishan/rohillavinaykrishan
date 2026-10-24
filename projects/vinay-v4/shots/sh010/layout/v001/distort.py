#!/usr/bin/env python3
"""distort.py : apply the solved SIMPLE_RADIAL lens to pinhole CG renders (or remove it from the plate).

Model (COLMAP SIMPLE_RADIAL, normalised coords, from cams.json at plate 1280x536):
    x = X/Z, y = Y/Z, r2 = x*x + y*y,  u = f*x*(1 + k1*r2) + cx,  v = f*y*(1 + k1*r2) + cy
f, cx, cy scale linearly with output width (k1 is resolution independent).

DISTORT (default): input = pinhole render with OVERSCAN (render res = round(OS*W) x round(OS*H), Blender:
  same lens, sensor_width = 36*OS, so the px focal is unchanged) -> output W x H, lens-distorted, aligned to the plate.
  With k1 = -0.20 (barrel) the frame corners need ~15% overscan; 6% is NOT enough (see --check).
UNDISTORT (--undistort): input = plate-like image W x H -> output pinhole of round(OS*W) x round(OS*H).

RGBA is premultiplied before resampling and un-premultiplied after (no dark/bright fringes). 8/16-bit PNG and EXR.

Usage:
  vfx-python distort.py in.png out.png --width 2808 [--overscan 1.16]
  vfx-python distort.py 'cg/cg.%04d.exr' 'cg_d/cg.%04d.png' --width 2808 --frames 0-51
  vfx-python distort.py --check            # print the overscan needed for the solved lens
"""
import os, sys, json, argparse
os.environ.setdefault('OPENCV_IO_ENABLE_OPENEXR', '1')
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))

def load_lens(path):
    c = json.load(open(path)); return c['width'], c['height'], c['f'], c['cx'], c['cy'], c['k1']

def undist_r(rd, k1, it=12):
    """solve ru*(1+k1*ru^2) = rd (Newton)."""
    ru = rd.copy()
    for _ in range(it):
        g = ru*(1+k1*ru*ru) - rd; dg = 1+3*k1*ru*ru; ru = ru - g/dg
    return ru

def required_overscan(PW, PH, f, cx, cy, k1):
    """overscan factor needed so the pinhole render covers every distorted plate pixel (per axis, max)."""
    u = np.array([0, PW, 0, PW, 0, PW, PW/2, PW/2]); v = np.array([0, 0, PH, PH, PH/2, PH/2, 0, PH])
    xd, yd = (u-cx)/f, (v-cy)/f; rd = np.hypot(xd, yd); ru = undist_r(rd, k1); s = np.where(rd > 0, ru/np.maximum(rd, 1e-12), 1)
    xu, yu = xd*s, yd*s
    return max(np.abs(xu).max()*f/(PW/2), np.abs(yu).max()*f/(PH/2))

def maps(W, H, OS, PW, f, cx, cy, k1, undistort=False):
    sc = W/PW; fo, cxo, cyo = f*sc, cx*sc, cy*sc*1.0
    Hs = H
    RW, RH = int(round(OS*W)), int(round(OS*H))
    if not undistort:
        # output pixel (distorted) -> source pixel in pinhole overscan render
        j, i = np.meshgrid(np.arange(W, dtype=np.float64), np.arange(H, dtype=np.float64))
        xd, yd = (j+0.5-cxo)/fo, (i+0.5-cyo)/fo; rd = np.hypot(xd, yd)
        ru = undist_r(rd, k1); s = np.where(rd > 0, ru/np.maximum(rd, 1e-12), 1.0)
        mx = fo*xd*s + RW/2 - 0.5; my = fo*yd*s + RH/2 - 0.5
        return mx.astype(np.float32), my.astype(np.float32), (W, H), (RW, RH)
    # undistort: output pixel (pinhole overscan) -> source (distorted) pixel in W x H
    j, i = np.meshgrid(np.arange(RW, dtype=np.float64), np.arange(RH, dtype=np.float64))
    xu, yu = (j+0.5-RW/2)/fo, (i+0.5-RH/2)/fo; d = 1+k1*(xu*xu+yu*yu)
    mx = fo*xu*d + cxo - 0.5; my = fo*yu*d + cyo - 0.5
    return mx.astype(np.float32), my.astype(np.float32), (RW, RH), (W, H)

def remap(img, mx, my, interp=cv2.INTER_CUBIC):
    dt = img.dtype; a = img.astype(np.float32)
    if a.ndim == 3 and a.shape[2] == 4:
        mx_ = 65535.0 if dt == np.uint16 else (255.0 if dt == np.uint8 else 1.0)
        al = a[..., 3:4]/mx_; a[..., :3] *= al
        o = cv2.remap(a, mx, my, interp, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        al2 = np.clip(o[..., 3:4]/mx_, 0, 1); o[..., :3] = np.where(al2 > 1e-6, o[..., :3]/np.maximum(al2, 1e-6), 0)
    else:
        o = cv2.remap(a, mx, my, interp, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    if dt == np.uint8: o = np.clip(np.round(o), 0, 255).astype(np.uint8)
    elif dt == np.uint16: o = np.clip(np.round(o), 0, 65535).astype(np.uint16)
    else: o = o.astype(dt)
    return o

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inp', nargs='?'); ap.add_argument('out', nargs='?')
    ap.add_argument('--cams', default=os.path.join(HERE, 'cams.json'))
    ap.add_argument('--width', type=int, default=None, help='output (distort) / input (undistort) width; height keeps the plate aspect')
    ap.add_argument('--overscan', type=float, default=1.16)
    ap.add_argument('--frames', default=None, help='a-b for %%04d patterns')
    ap.add_argument('--undistort', action='store_true'); ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    PW, PH, f, cx, cy, k1 = load_lens(a.cams)
    need = required_overscan(PW, PH, f, cx, cy, k1)
    if a.check or not a.inp:
        print('lens f=%.2f px @%d, k1=%.4f -> required overscan %.4f (use >= %.2f)' % (f, PW, k1, need, np.ceil(need*100)/100)); return
    if a.overscan + 1e-6 < need and not a.undistort:
        print('WARNING: overscan %.3f < required %.3f: frame corners will be transparent' % (a.overscan, need), file=sys.stderr)
    frames = [None]
    if a.frames: s, e = map(int, a.frames.split('-')); frames = range(s, e+1)
    cache = {}
    for fr in frames:
        ip = a.inp % fr if fr is not None else a.inp; op = a.out % fr if fr is not None else a.out
        img = cv2.imread(ip, cv2.IMREAD_UNCHANGED)
        if img is None: sys.exit('cannot read ' + ip)
        if a.undistort: W = a.width or img.shape[1]
        else: W = a.width or int(round(img.shape[1]/a.overscan))
        H = int(round(W*PH/PW))
        key = (W, img.shape[1], img.shape[0])
        if key not in cache:
            mx, my, osz, isz = maps(W, H, a.overscan, PW, f, cx, cy, k1, a.undistort)
            if (img.shape[1], img.shape[0]) != isz:
                sys.exit('input %s is %dx%d, expected %dx%d (overscan %.3f of %dx%d)' % (ip, img.shape[1], img.shape[0], isz[0], isz[1], a.overscan, W, H))
            cache[key] = (mx, my)
        mx, my = cache[key]
        os.makedirs(os.path.dirname(os.path.abspath(op)), exist_ok=True)
        cv2.imwrite(op, remap(img, mx, my))
    print('done', len(list(frames)), 'frame(s)')

if __name__ == '__main__':
    main()
