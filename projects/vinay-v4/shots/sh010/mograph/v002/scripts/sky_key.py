# sky_key.py in out : pull the line-up's saturated orange-red sky (top 520 px) to Ink; faces/costumes keep their colour
import sys, cv2, numpy as np
im = cv2.imread(sys.argv[1], cv2.IMREAD_UNCHANGED).astype(np.float32)
bgr = im[..., :3]; hsv = cv2.cvtColor(bgr.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
h, s, v = hsv[..., 0] * 2, hsv[..., 1] / 255, hsv[..., 2] / 255
key = np.clip((s - 0.50) / 0.20, 0, 1) * np.clip((v - 0.25) / 0.15, 0, 1) * ((h < 42) | (h > 345)).astype(np.float32)
H = im.shape[0]; yw = np.clip((560 - np.arange(H)) / 140.0, 0, 1)[:, None]          # only the top band (fades out 420-560)
m = cv2.GaussianBlur(key * yw, (0, 0), 5); m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
ink = np.array([13, 16, 18], np.float32)
im[..., :3] = bgr * (1 - 0.9 * m[..., None]) + ink * 0.9 * m[..., None]
cv2.imwrite(sys.argv[2], np.clip(im, 0, 255).astype(np.uint8))
