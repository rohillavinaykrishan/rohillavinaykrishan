import numpy as np, cv2, sys
from PIL import Image
src, S = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert('RGB'))
# --- watermark crop
X0, Y0, X1, Y1 = 1000, 4600, 2000, 5120
c = a[Y0:Y1, X0:X1].copy(); Image.fromarray(c).save(f'{S}/wm_in.png')
m = np.zeros(c.shape[:2], np.uint8)
def P(x, y): return (x - X0, y - Y0)
def rect(x1, y1, x2, y2): cv2.rectangle(m, P(x1, y1), P(x2, y2), 255, -1)
T = 34
# D
rect(1140, 4900, 1178, 5048)
cv2.ellipse(m, P(1190, 4975), (42, 52), 0, -115, 115, 255, 46)
# N
rect(1296, 4900, 1330, 5048); rect(1388, 4900, 1422, 5048)
cv2.line(m, P(1312, 4908), P(1405, 5040), 255, T + 6)
# E
rect(1480, 4900, 1516, 5048)
rect(1480, 4900, 1575, 4930); rect(1480, 4958, 1572, 4990); rect(1480, 5016, 1575, 5048)
# G
cv2.ellipse(m, P(1693, 4975), (68, 68), 0, 0, 360, 255, T + 6)
cv2.circle(m, P(1690, 4977), 50, 255, -1)

Image.fromarray(m).save(f'{S}/wm_mask.png')
# --- names crop
X0, Y0, X1, Y1 = 760, 3700, 2160, 4060
c = a[Y0:Y1, X0:X1].copy(); Image.fromarray(c).save(f'{S}/nm_in.png')
f = c.astype(np.float32); mx = f.max(2); mn = f.min(2); sat = (mx - mn) / np.maximum(mx, 1)
txt = ((sat < 0.45) & (mx > 150)).astype(np.uint8) * 255
box = np.zeros_like(txt)
for (x1, y1, x2, y2) in [(890, 3845, 1385, 3915), (1495, 3845, 2020, 3915)]:
    cv2.rectangle(box, (x1 - X0, y1 - Y0), (x2 - X0, y2 - Y0), 255, -1)
box2 = np.zeros_like(txt)
for (x1,y1,x2,y2) in [(885,3842,1352,3918),(1352,3842,1392,3872),(1490,3842,2025,3918)]:
    cv2.rectangle(box2,(x1-X0,y1-Y0),(x2-X0,y2-Y0),255,-1)
txt = box2
txt = cv2.dilate(txt, np.ones((9, 9), np.uint8))
Image.fromarray(txt).save(f'{S}/nm_mask.png')
