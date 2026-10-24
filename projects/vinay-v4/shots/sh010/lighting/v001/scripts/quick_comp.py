# quick integration check: distort CG + shadow, comp over plate. usage: quick_comp.py CGDIR WIDTH OUT.png frames...
import sys, subprocess, numpy as np, cv2, os
CG, W, OUT = sys.argv[1], int(sys.argv[2]), sys.argv[3]; frames = [int(x) for x in sys.argv[4:]]
LAY = '/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/layout/v001/'
H = round(W * 536 / 1280); rows = []
for f in frames:
    for kind in ('cg', 'shadow'):
        subprocess.run(['/opt/vfx-ai/bin/python', LAY + 'distort.py', f'{CG}/{kind}/{kind}.{f:04d}.png', f'/tmp/qc_{kind}.png', '--width', str(W), '--overscan', '1.16'], check=True, capture_output=True)
    pl = cv2.imread(LAY + f'plate/plate.{f+1:04d}.png').astype(np.float32) / 255
    pl = cv2.resize(pl, (W, H), interpolation=cv2.INTER_LANCZOS4)
    lin = np.clip(pl, 0, 1) ** 2.2
    sh = cv2.imread('/tmp/qc_shadow.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 65535
    if sh.ndim == 3: sh = sh[..., 0]
    shm = cv2.imread('/tmp/qc_shadow.png', cv2.IMREAD_UNCHANGED)
    lin = lin * (1 - 0.65 * (1 - sh))[..., None]
    cg = cv2.imread('/tmp/qc_cg.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 65535
    a = cg[..., 3:4]; c = np.clip(cg[..., :3], 0, 1) ** 2.2
    out = c * a + lin * (1 - a)
    rows.append((np.clip(out, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8))
cv2.imwrite(OUT, np.vstack(rows)); print('wrote', OUT)
