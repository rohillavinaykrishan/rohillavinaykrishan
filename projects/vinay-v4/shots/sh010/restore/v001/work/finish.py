"""restored RGB (2880x1760) + lineup.png alpha -> warm-matched 2160x900 RGBA.
Crop src rows 560-1760 (director note 4), shadows toward Umber #2A211A with
saturated costume colours protected, 0.75x INTER_AREA, 300 px top gradient alpha."""
import sys, cv2, numpy as np
rgb_path, alpha_src, out = sys.argv[1:4]
STRENGTH = float(sys.argv[4]) if len(sys.argv) > 4 else 0.7
Y0 = int(sys.argv[5]) if len(sys.argv) > 5 else 560
rgb = cv2.cvtColor(cv2.imread(rgb_path, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
a0 = cv2.imread(alpha_src, cv2.IMREAD_UNCHANGED)[..., 3].astype(np.float32) / 255
rgb, a0 = rgb[Y0:1760], a0[Y0:1760]
umber = np.array([0x2A, 0x21, 0x1A], np.float32) / 255
L = rgb @ np.array([0.2126, 0.7152, 0.0722], np.float32)
mx, mn = rgb.max(-1), rgb.min(-1)
sat = (mx - mn) / np.maximum(mx, 1e-4)
def ss(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)
shadow = 1 - ss(0.04, 0.32, L)                      # only dark tones
protect = 1 - ss(0.45, 0.80, sat) * ss(0.06, 0.20, mx)  # leave saturated costume colour alone
w = (shadow * protect * STRENGTH)[..., None]
# lift-style: black maps to Umber, the tint fades out as tones rise
lifted = umber + rgb * (1 - umber)
out_rgb = rgb * (1 - w) + lifted * w
H, W = out_rgb.shape[:2]
nw, nh = 2160, round(H * 2160 / W)
small = cv2.resize(out_rgb, (nw, nh), interpolation=cv2.INTER_AREA)
a = cv2.resize(a0, (nw, nh), interpolation=cv2.INTER_AREA)
g = ss(0, 300, np.arange(nh, dtype=np.float32))[:, None]
a = a * g
rgba = np.dstack([small, a]).clip(0, 1)
cv2.imwrite(out, cv2.cvtColor((rgba * 255).round().astype(np.uint8), cv2.COLOR_RGBA2BGRA))
print(out, nw, nh, 'mean w', float(w.mean()), 'protected frac', float((protect < 0.5).mean()))
