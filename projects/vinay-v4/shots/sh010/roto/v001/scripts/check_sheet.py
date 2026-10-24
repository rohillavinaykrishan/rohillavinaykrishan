"""review/matte_check_v001.png: top = matte (pink) over plate on s0,s12,s25,s38,s51 with monument bbox;
below = 100% (2x) crops around the monument bbox on s4,s25,s48: plate*matte over black | over white."""
import cv2, json, numpy as np
A = {f['frame']: f for f in json.load(open('../../layout/v001/anchor.json'))['frames']}
def lab(img, t):
    cv2.putText(img, t, (8, 30), 0, 0.9, (0, 0, 0), 4); cv2.putText(img, t, (8, 30), 0, 0.9, (0, 255, 255), 2); return img
top = []
for i in (0, 12, 25, 38, 51):
    p = cv2.imread('plate/plate.%04d.png' % i); m = cv2.resize(cv2.imread('matte/matte.%04d.png' % i, 0), (1280, 536), interpolation=cv2.INTER_AREA)[..., None] / 255.
    o = (p * (1 - .6 * m) + np.array([180, 0, 255]) * .6 * m).astype(np.uint8)
    x0, y0, x1, y1 = map(int, A[i]['bbox']); cv2.rectangle(o, (x0, y0), (x1, y1), (0, 255, 255), 2)
    top.append(lab(cv2.resize(o, (640, 268)), 's%d' % i))
top = np.hstack(top)  # 3200 wide
rows = []
for i in (4, 25, 48):
    p = cv2.resize(cv2.imread('plate/plate.%04d.png' % i), (2560, 1072), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    m = cv2.imread('matte/matte.%04d.png' % i, 0)[..., None] / 255.
    x0, y0, x1, y1 = [int(v * 2) for v in A[i]['bbox']]
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    cw, ch = 1600, 700
    a = max(0, min(2560 - cw, cx - cw // 2)); b = max(0, min(1072 - ch, cy - ch // 2))
    blk = (p * m)[b:b+ch, a:a+cw].astype(np.uint8)
    wht = (p * m + 255 * (1 - m))[b:b+ch, a:a+cw].astype(np.uint8)
    rows.append(np.hstack([lab(blk, 's%d 100%% (2x) over black' % i), lab(wht, 's%d over white' % i)]))
sheet = np.vstack([top] + rows)
cv2.imwrite('review/matte_check_v001.png', sheet)
print(sheet.shape)
