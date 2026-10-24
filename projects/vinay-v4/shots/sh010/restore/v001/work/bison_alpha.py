"""Union the 300 px top fade with a soft matte of M. Bison (colour key: bright orange/yellow sky vs his dark
uniform; holes filled so the face/cap stay solid). Box limited to Bison so the sky elsewhere still fades."""
import cv2, numpy as np, sys
src, out = sys.argv[1], sys.argv[2]
im = cv2.imread(src, cv2.IMREAD_UNCHANGED); a = im[..., 3].astype(np.float32) / 255
bgr = cv2.imread('work/lineup_faces_selected.png')[470:1760]
bgr = cv2.resize(bgr, (2160, 968), interpolation=cv2.INTER_AREA)
x0, y0, x1, y1 = 900, 0, 1290, 330          # Bison box (fade zone ends at y 300)
hsv = cv2.cvtColor(bgr[y0:y1, x0:x1], cv2.COLOR_BGR2HSV).astype(int)
dark = (hsv[..., 2] < 100).astype(np.uint8)  # cap, coat, glove (sky is bright)
dark = cv2.morphologyEx(dark, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
cv2.ellipse(dark, (1088 - x0, 158 - y0), (40, 50), 0, 0, 360, 1, -1)  # the face (skin is sky-coloured)
dark = cv2.morphologyEx(dark, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
n, lab, st, _ = cv2.connectedComponentsWithStats(dark)
k = lab[300 - y0, 1100 - x0]                 # seed on Bison's coat
m = (lab == k).astype(np.uint8) * 255
cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cv2.drawContours(m, cnts, -1, 255, -1)       # fill holes (face, cap badge)
m = cv2.erode(m, np.ones((3, 3), np.uint8))
m = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 2.0)
full = np.zeros_like(a); full[y0:y1, x0:x1] = m
# fade the matte's own edge at the box border so there is no seam
a2 = np.maximum(a, full)
im[..., 3] = (a2 * 255).round().astype(np.uint8)
cv2.imwrite(out, im)
cv2.imwrite(out.replace('.png', '_bisonmatte_dbg.png'), (full * 255).astype(np.uint8))
print('matte px', int((full > .5).sum()), 'face alpha', a2[110:190, 1060:1140].mean())
