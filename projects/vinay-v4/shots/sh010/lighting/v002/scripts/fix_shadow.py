# The render uses a per-frame border (monument + its shadow + motion-blur margin). Outside the border Cycles writes 0
# into the Shadow Catcher pass; set it to 1 (= no shadow) there. usage: fix_shadow.py OUTDIR
import sys, json, os, numpy as np, cv2
D = sys.argv[1]; B = {}
for l in open(os.path.join(D, 'borders.jsonl')):
    r = json.loads(l); B[r['frame']] = r
for f, r in sorted(B.items()):
    p = os.path.join(D, 'shadow', 'shadow.%04d.png' % f)
    if not os.path.exists(p): continue
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED); H, W = im.shape[:2]
    x0, x1, y0, y1 = r['border']
    c0, c1 = int(np.floor(x0 * W)), int(np.ceil(x1 * W)); r0, r1 = int(np.floor((1 - y1) * H)), int(np.ceil((1 - y0) * H))
    m = np.ones((H, W), bool); m[r0 + 3:r1 - 3, c0 + 3:c1 - 3] = False
    # the 1-px rim of the border can be partially written: treat it as outside too if it is darker than its inner neighbour
    im[m] = 65535
    cv2.imwrite(p, im)
print('fixed', len(B), 'frames')
