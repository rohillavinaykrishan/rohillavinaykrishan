# measure the row "VAMSI KRISHNA EADALA | VINAY KRISHAN ROHILLA" per frame in credits_src (69 fr)
import cv2, numpy as np, json, sys
FR = 'work/cr/c.%04d.png'; N = 69; REF = 40
ref = cv2.imread(FR % REF, 0).astype(np.float32)
T0 = (372, 620, 560, 640)              # x0,y0,x1,y1 template (right column, his name) on ref
tpl = ref[T0[1]:T0[3], T0[0]:T0[2]]
CY_REF = 629.5                          # cap-height centre on ref (rows 625..634 measured)
def sub(c, i):
    if 0 < i < len(c) - 1:
        a, b, d = c[i-1], c[i], c[i+1]; den = a - 2*b + d
        return i + (0.5*(a - d)/den if den != 0 else 0)
    return float(i)
out = []
for f in range(N):
    g = cv2.imread(FR % f, 0).astype(np.float32)
    res = cv2.matchTemplate(g[:, 340:600], tpl, cv2.TM_CCOEFF_NORMED)
    _, mx, _, loc = cv2.minMaxLoc(res)
    x, y = loc
    ys = sub(res[:, x], y); xs = sub(res[y, :], x)
    dy = ys - (T0[1]); cy = CY_REF + dy
    xoff = (340 + xs) - T0[0]
    yi = int(round(cy))
    band = g[yi-8:yi+9]
    # x extents of bright text in this band (right col = his name, left col = partner)
    thr = max(110.0, float(np.percentile(band, 99)) * 0.6)
    def ext(x0, x1):
        cols = np.nonzero((band[:, x0:x1] > thr).any(0))[0]
        return (int(x0 + cols.min()), int(x0 + cols.max())) if len(cols) else (None, None)
    rx = ext(362, 700); lx = ext(20, 358)
    peak = float(np.percentile(band[:, 377:554], 99))
    out.append({"f": f, "t_src": round(67.40 + f/25, 2), "y": round(float(cy), 2), "y_top": round(float(cy) - 4.5, 2), "y_bot": round(float(cy) + 4.5, 2),
                "x_dx": round(float(xoff), 2), "name_x0": rx[0], "name_x1": rx[1], "partner_x0": lx[0], "partner_x1": lx[1],
                "score": round(float(mx), 3), "text_peak": round(peak, 1)})
json.dump(out, open('work/_rt.json', 'w'))
for o in out: print(o['f'], o['y'], o['x_dx'], o['name_x0'], o['name_x1'], o['partner_x0'], o['partner_x1'], o['score'], o['text_peak'])
