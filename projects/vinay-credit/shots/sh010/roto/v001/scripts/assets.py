import numpy as np, cv2, sys
from PIL import Image
src, S, O = sys.argv[1:4]
a = np.asarray(Image.open(src).convert('RGB')).copy()
# paste LaMa patches
a[4600:5120, 1000:2000] = np.asarray(Image.open(f'{S}/wm_out.png').convert('RGB'))
a[3700:4060, 760:2160] = np.asarray(Image.open(f'{S}/nm_out2.png').convert('RGB'))
Image.fromarray(a).save(f'{S}/clean_full.png')
# ---- lineup
TOP, FEND = 3360, 3840
crop = a[TOP:].astype(np.float32)
h = crop.shape[0]
t = np.clip((np.arange(h) - 0) / (FEND - TOP), 0, 1)
al = (t * t * (3 - 2 * t))[:, None] * np.ones((1, crop.shape[1]))
rgba = np.dstack([crop, al * 255]).round().astype(np.uint8)
Image.fromarray(rgba, 'RGBA').save(f'{O}/lineup.png', optimize=True)
print('lineup', rgba.shape)
# ---- red base
F0, F1 = 1120, 2860
L = F1 - F0
f = a[F0:F1].astype(np.float32)
# flatten low-frequency gradient to a uniform mean so it can be stacked/tiled
low = cv2.GaussianBlur(f, (0, 0), 180)
mean = f.reshape(-1, 3).mean(0)
flat = np.clip(f / np.maximum(low, 1) * mean, 0, 255)
H = 5120
# vertical: stack mirrored copies, then crossfade seams to hide the mirror axis
st = np.vstack([flat[::-1], flat, flat[::-1]])            # 6000
st = st[(st.shape[0] - H) // 2:(st.shape[0] - H) // 2 + H]
# blend in a shifted copy around the mirror axes to break symmetry
off = np.vstack([flat, flat[::-1], flat, flat[::-1]])[L // 2 - 200:][:H]
off = off[:, ::-1]
yy = np.arange(H)
n3 = 3 * L
axes = [L - (n3 - H) // 2, 2 * L - (n3 - H) // 2]  # seam rows in output coords
w = np.zeros(H)
for s in axes:
    w = np.maximum(w, np.clip(1 - np.abs(yy - s) / 320, 0, 1))
w = (w * w * (3 - 2 * w))[:, None, None]
base = st * (1 - w) + off * w
# horizontal tileability: crossfade left/right edges
W = base.shape[1]; band = 240
wx = np.clip(np.arange(W) / band, 0, 1); wx = np.minimum(wx, wx[::-1])
rolled = np.roll(base, W // 2, axis=1)
base = base * wx[None, :, None] + rolled * (1 - wx[None, :, None])
Image.fromarray(np.clip(base + 0.5, 0, 255).astype(np.uint8)).save(f'{O}/red_base.png', optimize=True)
print('seams', axes, 'mean', mean)
