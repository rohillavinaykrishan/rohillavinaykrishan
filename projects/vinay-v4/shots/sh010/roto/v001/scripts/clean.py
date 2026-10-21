"""Combine + clean holdout mattes.
person = max( temporal_median3(rembg u2net_human_seg), SAM2 people/heli union )
then erode 1 px (3x3), gaussian blur sigma 1.5 px. Blade matte: SAM2 blade, same erode/blur.
usage: vfx-python clean.py  (run from the version folder)"""
import cv2, numpy as np, os, sys
N = 52
def load(pat, i):
    m = cv2.imread(pat % i, 0)
    return np.zeros((536, 1280), np.uint8) if m is None else m
rem = np.stack([load('raw/human/m.%04d.png', i) for i in range(N)]).astype(np.float32)
pad = np.concatenate([rem[:1], rem, rem[-1:]])
med = np.median(np.stack([pad[:-2], pad[1:-1], pad[2:]]), axis=0)
sam_objs = [d for d in sorted(os.listdir('raw/sam')) if os.path.isdir('raw/sam/' + d)] if os.path.isdir('raw/sam') else []
sam = np.zeros_like(rem)
for d in sam_objs:
    s = np.stack([load(f'raw/sam/{d}/m.%04d.png', i) for i in range(N)]).astype(np.float32)
    # SAM masks are binary: median3 them too (kills 1-frame pops), they are tracked so this is safe
    sp = np.concatenate([s[:1], s, s[-1:]])
    s = np.median(np.stack([sp[:-2], sp[1:-1], sp[2:]]), axis=0)
    sam = np.maximum(sam, s)
k = np.ones((3, 3), np.uint8)
def finish(m):
    m = cv2.erode(m.astype(np.uint8), k, iterations=1)
    return cv2.GaussianBlur(m, (0, 0), 1.5)
os.makedirs('matte', exist_ok=True)
for i in range(N):
    cv2.imwrite('matte/matte.%04d.png' % i, finish(np.maximum(med[i], sam[i])))
if os.path.isdir('raw/blade'):
    os.makedirs('matte_blade', exist_ok=True)
    b = np.stack([load('raw/blade/m.%04d.png', i) for i in range(N)]).astype(np.float32)
    bp = np.concatenate([b[:1], b, b[-1:]])
    b = np.median(np.stack([bp[:-2], bp[1:-1], bp[2:]]), axis=0)
    for i in range(N):
        cv2.imwrite('matte_blade/blade.%04d.png' % i, finish(b[i]))
print('sam objs:', sam_objs)
