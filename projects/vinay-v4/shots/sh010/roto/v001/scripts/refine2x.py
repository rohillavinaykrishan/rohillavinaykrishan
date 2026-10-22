"""2x holdout matte (director note 20) for sh010.
per frame: base = max(rembg u2net_human_seg soft matte, SAM2 people union) at 1280x536
 -> upscale to 2560x1072 (cubic) -> guided filter (guide = plate upscaled 2x, r=4, eps=1e-3)
 -> temporal median over 3 frames -> erode 1 px (3x3) -> feather (gaussian sigma 2 px)
writes matte/matte.%04d.png (8-bit gray, white = person/holdout)."""
import cv2, numpy as np, os
N, W, H = 52, 2560, 1072
gf = cv2.ximgproc.guidedFilter
def rd(p):
    m = cv2.imread(p, 0)
    return np.zeros((536, 1280), np.uint8) if m is None else m
objs = sorted(d for d in os.listdir('raw/sam') if os.path.isdir('raw/sam/' + d)) if os.path.isdir('raw/sam') else []
ref = []
for i in range(N):
    base = rd('raw/human/m.%04d.png' % i)
    for d in objs:
        base = np.maximum(base, rd(f'raw/sam/{d}/m.%04d.png' % i))
    up = cv2.resize(base, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255
    guide = cv2.resize(cv2.imread('plate/plate.%04d.png' % i), (W, H), interpolation=cv2.INTER_CUBIC)
    r = gf(guide.astype(np.float32) / 255, up, 4, 1e-3)
    ref.append(np.clip(r, 0, 1))
ref = np.stack(ref)
pad = np.concatenate([ref[:1], ref, ref[-1:]])
med = np.median(np.stack([pad[:-2], pad[1:-1], pad[2:]]), axis=0)
k = np.ones((3, 3), np.uint8)
os.makedirs('matte', exist_ok=True)
for i in range(N):
    m = cv2.erode((med[i] * 255).round().astype(np.uint8), k, iterations=1)
    m = cv2.GaussianBlur(m, (0, 0), 2.0)
    cv2.imwrite('matte/matte.%04d.png' % i, m)
print('sam objs', objs, 'wrote', N)
