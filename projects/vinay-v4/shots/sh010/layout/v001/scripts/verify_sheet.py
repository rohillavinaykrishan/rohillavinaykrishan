# verify_sheet.py : review/solve_v001.png  (points + ground grid + monument box + FINAL window on s0/s25/s51)
import json, numpy as np, cv2, sys
L = '/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/layout/v001/'
FR = [int(x) for x in (sys.argv[1].split(',') if len(sys.argv) > 1 else '0,25,51'.split(','))]
OUT = sys.argv[2] if len(sys.argv) > 2 else L+'review/solve_v001.png'
cj = json.load(open(L+'cams.json')); W, H, f, cx, cy, k1 = cj['width'], cj['height'], cj['f'], cj['cx'], cj['cy'], cj['k1']
pj = json.load(open(L+'points.json')); P = np.array([p['xyz'] for p in pj['points']]); G = np.array([p['ground'] for p in pj['points']])
ids = {p['id']: k for k, p in enumerate(pj['points'])}
aj = json.load(open(L+'anchor.json')); tj = json.load(open(L+'tracks.json'))
st = json.load(open(L+'solve_stats.json'))
AX, AY, _ = aj['anchor']['location']; AR = np.radians(aj['anchor']['rot_z_deg']); TOP = aj['monument_bounds_world']['max'][2]
c_, s_ = np.cos(AR), np.sin(AR)
def loc(x, y, z): return np.array([AX + c_*x - s_*y, AY + s_*x + c_*y, z])
SC = 1  # draw scale
def project(c, X):
    R = np.array(c['R']); t = np.array(c['t']); Xc = X @ R.T + t
    x, y = Xc[:, 0]/Xc[:, 2], Xc[:, 1]/Xc[:, 2]; r2 = x*x+y*y
    z = np.where(r2 < 1.0, Xc[:, 2], -1.0)   # outside r=1 the SIMPLE_RADIAL polynomial folds back: treat as invalid
    return np.c_[f*x*(1+k1*r2)+cx, f*y*(1+k1*r2)+cy]*SC, z
def line3(im, c, a, b, col, th=1, n=120):
    X = np.linspace(a, b, n); uv, z = project(c, X); ok = z > 0.2
    # draw only contiguous valid runs
    idx = np.where(ok)[0]
    if len(idx) < 2: return
    for run in np.split(idx, np.where(np.diff(idx) > 1)[0]+1):
        if len(run) > 1: cv2.polylines(im, [np.round(uv[run]*4).astype(np.int32)], False, col, th, cv2.LINE_AA, shift=2)
tiles = []
for fr in FR:
    c = cj['frames'][fr]; im = cv2.imread(L+'plate/plate.%04d.png' % (fr+1))
    im = (im*0.75).astype(np.uint8)
    # ground grid 1 m, x -10..10, y 2..30
    for gx in range(-10, 11): line3(im, c, np.array([gx, 2, 0]), np.array([gx, 30, 0]), (150, 230, 170))
    for gy in range(2, 31): line3(im, c, np.array([-10, gy, 0]), np.array([10, gy, 0]), (150, 230, 170))
    # tracks: observed (cyan dot) and reprojected 3D (pink cross) + residual
    tf = tj['frames'][fr]['pts']; obs = np.array([[p[0], p[1]] for p in tf]); pid = [ids[p[2]] for p in tf]
    rp, _ = project(c, P[pid]); res = np.linalg.norm(rp-obs, axis=1)
    for (u, v), (ru, rv), g in zip(obs, rp, G[pid]):
        cv2.circle(im, (int(u), int(v)), 2, (255, 255, 0) if not g else (0, 200, 255), -1, cv2.LINE_AA)
        cv2.drawMarker(im, (int(round(ru)), int(round(rv))), (200, 80, 255), cv2.MARKER_CROSS, 5, 1)
    # monument: plinth box + full-height box
    for z0, z1, col in [(0, 0.24, (60, 60, 255)), (0, TOP, (255, 120, 255))]:
        cs = [(-3.9, -0.5), (3.9, -0.5), (3.9, 0.5), (-3.9, 0.5)]
        for k in range(4):
            a, b = cs[k], cs[(k+1) % 4]
            line3(im, c, loc(*a, z0), loc(*b, z0), col, 2); line3(im, c, loc(*a, z1), loc(*b, z1), col, 2)
            line3(im, c, loc(*a, z0), loc(*a, z1), col, 2)
    fa = aj['frames'][fr]
    cv2.drawMarker(im, tuple(int(v) for v in fa['corners']['front_left']), (0, 0, 255), cv2.MARKER_TILTED_CROSS, 14, 2)
    # FINAL window and 6% top line
    CX, HW = fa['crop_cx'], aj['window_half_width_px']
    for xx in (CX-HW, CX+HW): cv2.line(im, (int(xx), 0), (int(xx), H), (0, 255, 255), 1)
    cv2.line(im, (0, int(0.06*H)), (W, int(0.06*H)), (0, 160, 255), 1)
    txt = 's%d  tracks %d  reproj mean %.2f px  window %s  top %.1f%%' % (fr, len(tf), res.mean(), 'OK' if fa['inside_final_window'] else 'OUT', fa['top_margin_pct'])
    cv2.rectangle(im, (0, H-30), (W, H), (0, 0, 0), -1); cv2.putText(im, txt, (10, H-9), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    tiles.append(im)
hdr = np.zeros((44, W, 3), np.uint8)
cv2.putText(hdr, 'sh010 layout v001  cams %d/52  pts %d  mean reproj %.3f px  f %.1f px (%.2f mm)  k1 %.4f  anchor (%.1f, %.1f, rz %.0f)' % (
    st['cameras_registered'], st['points'], st['mean_reproj_px'], st['f_px'], st['lens_mm_36'], st['k1'], AX, AY, np.degrees(AR)),
    (10, 29), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
cv2.imwrite(OUT, np.vstack([hdr] + tiles)); print('wrote', OUT)
