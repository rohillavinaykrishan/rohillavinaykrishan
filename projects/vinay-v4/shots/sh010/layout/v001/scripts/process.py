# process.py : COLMAP model -> Z-up metric world, ground plane, cams/points/tracks/solve_stats JSON
# run: vfx-python process.py [model_dir]
import numpy as np, json, sys, os, glob, re
L = '/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/layout/v001/'
M = sys.argv[1] if len(sys.argv) > 1 else L + 'colmap/sparse/0/'
REF = 26          # world origin under this plate frame's camera (= director cm3 image 0019 = lookdev frame)
CAM_H = float(os.environ.get('CAM_H', '1.0'))   # assumed mean camera height (m), treatment 9.1

def qR(q):
    w, x, y, z = q
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])

cam = [l.split() for l in open(M+'cameras.txt') if not l.startswith('#') and l.strip()][0]
model = cam[1]; W, H = int(cam[2]), int(cam[3]); f, cx, cy, k1 = map(float, cam[4:8])
Ls = [l for l in open(M+'images.txt') if not l.startswith('#')]
imgs = {}
for i in range(0, len(Ls), 2):
    a = Ls[i].split()
    if not a: continue
    p = np.array(Ls[i+1].split(), float).reshape(-1, 3) if Ls[i+1].strip() else np.zeros((0, 3))
    imgs[int(re.findall(r'\d+', a[9])[-1])] = dict(q=np.array(a[1:5], float), t=np.array(a[5:8], float), name=a[9], obs=p)
P3 = {}
for l in open(M+'points3D.txt'):
    if l.startswith('#'): continue
    a = l.split(); P3[int(a[0])] = dict(X=np.array(a[1:4], float), rgb=[int(v) for v in a[4:7]], err=float(a[7]), n=(len(a)-8)//2)
ids = np.array(sorted(P3)); X = np.array([P3[i]['X'] for i in ids])
frames = sorted(imgs)
print('model', model, W, H, 'f', f, 'k1', k1, 'registered', len(frames), 'points', len(ids))

def proj(fr, Xs):
    Rc, tc = qR(imgs[fr]['q']), imgs[fr]['t']
    Xc = Xs @ Rc.T + tc; x = Xc[:, 0]/Xc[:, 2]; y = Xc[:, 1]/Xc[:, 2]; d = 1 + k1*(x*x+y*y)
    return np.c_[f*x*d+cx, f*y*d+cy], Xc[:, 2]

C = {fr: -qR(imgs[fr]['q']).T @ imgs[fr]['t'] for fr in frames}
# ---- ground plane: RANSAC on points projecting below 62% of frame height in REF (treatment 9.2.3)
uv, z = proj(REF, X); sel = (uv[:, 1] > 0.62*H) & (z > 0) & (uv[:, 0] >= 0) & (uv[:, 0] < W)
G = X[sel]; rng = np.random.default_rng(0)
# threshold 0.15 units was defined at the director's scale (mean cam height 2.874 units); keep it scale-relative
Cs = np.array([C[fr] for fr in frames])
def fit(thr):
    best = None
    for _ in range(4000):
        s3 = G[rng.choice(len(G), 3, replace=False)]; nr = np.cross(s3[1]-s3[0], s3[2]-s3[0])
        if np.linalg.norm(nr) < 1e-12: continue
        nr /= np.linalg.norm(nr); d = -nr @ s3[0]; inl = np.abs(G @ nr + d) < thr
        if best is None or inl.sum() > best[0]: best = (inl.sum(), nr, d, inl)
    cnt, nr, d, inl = best
    # least-squares refine on inliers
    Gi = G[inl]; c0 = Gi.mean(0); u, s_, vt = np.linalg.svd(Gi-c0); nr2 = vt[2]
    if nr2 @ nr < 0: nr2 = -nr2
    return nr2, -nr2 @ c0
nr, d = fit(1.0)  # rough pass to get scale
if (Cs @ nr + d).mean() < 0: nr, d = -nr, -d
hmean = (Cs @ nr + d).mean()
thr = 0.15 * hmean / 2.874
nr, d = fit(thr)
if (Cs @ nr + d).mean() < 0: nr, d = -nr, -d
hcam = Cs @ nr + d; s = CAM_H / hcam.mean()
gres = X @ nr + d; ground_all = np.abs(gres) < thr
ground_inl = ground_all.copy()
print('ground candidates', len(G), 'thr(units)', round(thr, 4), 'inliers among candidates', int((np.abs(G@nr+d) < thr).sum()),
      'all pts within thr', int(ground_all.sum()), 'scale m/unit', round(s, 4))
# ---- world axes
Rr = qR(imgs[REF]['q']); fwd = Rr.T @ np.array([0, 0, 1.]); fwd = fwd - (fwd@nr)*nr; fwd /= np.linalg.norm(fwd)
right = np.cross(fwd, nr); Mrot = np.vstack([right, fwd, nr]); O = C[REF] - (C[REF]@nr + d)*nr
def to_w(Xs): return (Xs - O) @ Mrot.T * s
Xw = to_w(X)
cams = []
for fr in frames:
    Rc, tc = qR(imgs[fr]['q']), imgs[fr]['t']
    Rn = Rc @ Mrot.T; tn = s*(Rc @ O + tc); Cw = -Rn.T @ tn
    Rb = Rn.T @ np.diag([1, -1, -1])
    mw = np.eye(4); mw[:3, :3] = Rb; mw[:3, 3] = Cw
    nobs = int((imgs[fr]['obs'][:, 2] >= 0).sum()) if len(imgs[fr]['obs']) else 0
    cams.append(dict(frame=fr, plate_file='plate.%04d.png' % (fr+1), src_frame=2982+fr, image=imgs[fr]['name'], R=Rn.tolist(), t=tn.tolist(), C=Cw.tolist(),
                     blender_matrix_world=mw.tolist(), n_tracks=nobs))
lens = f/W*36
out_cams = dict(convention=("World Z-up metres, ground z=0, origin on the ground under camera s%d, +Y = s%d forward projected on ground. "
                            "R,t are world->camera (OpenCV: x right, y down, z forward): x_cam = R@X + t. "
                            "Pixel (plate 1280x536): x=xc/zc, y=yc/zc, r2=x*x+y*y, u=f*x*(1+k1*r2)+cx, v=f*y*(1+k1*r2)+cy. "
                            "C = camera centre. blender_matrix_world = camera object matrix_world (Blender -Z forward, +Y up). "
                            "Blender: sensor_fit HORIZONTAL, sensor_width 36, lens_mm. frame = s index 0-51 = Blender scene frame; plate_file = edit/v001/plate numbering (s+1). "
                            "Projection is only valid for r2 < 1.0 (frame corner r2 = 0.64): beyond r = 1/sqrt(-3*k1) = 1.30 the polynomial folds back, so clip 3D lines/points with r2 >= 1 (or behind the camera) before projecting. Pixel coords: (0,0) = top-left CORNER of the image, first pixel centre = (0.5,0.5) (COLMAP = canvas convention).") % (REF, REF),
                width=W, height=H, model=model, f=f, cx=cx, cy=cy, k1=k1,
                K=[[f, 0, cx], [0, f, cy], [0, 0, 1]], lens_mm=lens, hfov_deg=float(np.degrees(2*np.arctan(W/2/f))),
                fps=24000/1001, src_frames=[2982, 3033], frames=cams)
assert len(cams) == 52 or os.environ.get('ALLOW_PARTIAL')
json.dump(out_cams, open(L+'cams.json', 'w'), indent=1)
pts = [dict(id=int(i), xyz=[round(v, 4) for v in Xw[k]], rgb=P3[i]['rgb'], err=round(P3[i]['err'], 3),
            track_len=P3[i]['n'], ground=bool(ground_inl[k])) for k, i in enumerate(ids)]
json.dump(dict(convention='xyz in the cams.json world (metres, Z up). ground = within RANSAC threshold of the fitted sand plane.',
               count=len(pts), ground_count=int(ground_inl.sum()), points=pts), open(L+'points.json', 'w'))
tr = []
for fr in frames:
    o = imgs[fr]['obs']; o = o[o[:, 2] >= 0] if len(o) else o
    tr.append(dict(frame=fr, plate_file='plate.%04d.png' % (fr+1), n=len(o), pts=[[round(a, 2), round(b, 2), int(c)] for a, b, c in o]))
json.dump(dict(convention='per plate frame: [u, v, point3D id] observations (plate px 1280x536, distorted = as seen in the plate) that belong to a triangulated 3D point. (0,0)=top-left corner of the image (canvas convention). frame = s index 0-51.',
               frames=tr), open(L+'tracks.json', 'w'))
# ---- reprojection check (own computation)
errs = []
for fr in frames:
    o = imgs[fr]['obs']; o = o[o[:, 2] >= 0]
    Xs = np.array([P3[int(i)]['X'] for i in o[:, 2]]); uv, _ = proj(fr, Xs); errs.append(np.linalg.norm(uv - o[:, :2], axis=1))
alle = np.concatenate(errs)
an = open(L+'colmap/analyzer.txt').read() if os.path.exists(L+'colmap/analyzer.txt') else ''
Cw_all = np.array([c['C'] for c in cams])
fw = np.array([np.array(c['blender_matrix_world'])[:3, :3] @ [0, 0, -1] for c in cams])
pairmax = max(np.degrees(np.arccos(np.clip(a @ b, -1, 1))) for a in fw for b in fw)
stats = dict(cameras_registered=len(frames), cameras_total=52, points=len(ids), ground_points=int(ground_inl.sum()),
             observations=int(len(alle)), mean_track_length=round(float(np.mean([P3[i]['n'] for i in ids])), 2),
             mean_reproj_px=round(float(np.mean([P3[i]['err'] for i in ids])), 3), mean_reproj_definition='COLMAP model_analyzer: mean over 3D points of their mean track reprojection error',
             mean_reproj_per_observation_px=round(float(alle.mean()), 3), median_reproj_px=round(float(np.median(alle)), 3),
             p95_reproj_px=round(float(np.percentile(alle, 95)), 3),
             camera_model=model, width=W, height=H, f_px=round(f, 2), f_px_960=round(f*960/W, 2), lens_mm_36=round(lens, 2),
             hfov_deg=round(float(np.degrees(2*np.arctan(W/2/f))), 2), k1=round(k1, 4), cx=cx, cy=cy,
             cam_height_assumed_m=CAM_H, scale_m_per_unit=round(float(s), 5),
             cam_height_min_max_m=[round(float(hcam.min()*s), 3), round(float(hcam.max()*s), 3)],
             camera_travel_m=round(float(np.linalg.norm(Cw_all[-1]-Cw_all[0])), 3),
             camera_path_m=round(float(np.linalg.norm(np.diff(Cw_all, axis=0), axis=1).sum()), 3),
             rotation_span_deg=round(float(pairmax), 2), rotation_s0_s51_deg=round(float(np.degrees(np.arccos(np.clip(fw[0]@fw[-1], -1, 1)))), 2),
             ground_plane_colmap=dict(normal=nr.tolist(), d=float(d)), world_origin_frame=REF,
             per_frame=[dict(frame=c['frame'], tracks=c['n_tracks'], reproj_px=round(float(e.mean()), 3)) for c, e in zip(cams, errs)],
             scale_check=dict(note='measured with CAM_H=1.0: woman in red on s15 (upright, one leg) 4.27 m, man centre s25 (crouched) 3.37 m (about 3.9 m standing) -> for 1.75-1.8 m people the true camera height is about 0.42-0.46 m (true metres = world units x 0.45). World kept at the treatment 9.1 convention (mean camera height 1.0 m); rerun process.py with CAM_H=0.45 for true metres.', true_cam_height_est_m=0.45),
             init_pair=[10, 25], solve_note='relaxed mapper options (treatment 9.2) + lens prior f 999.16 px / k1 -0.1966 (director 960 px solve scaled) + forced init pair s10/s25; f and k1 refined freely by BA',
             tracks_per_frame_min_mean_max=[int(min(c['n_tracks'] for c in cams)), round(float(np.mean([c['n_tracks'] for c in cams])), 1), int(max(c['n_tracks'] for c in cams))],
             colmap_model_analyzer=[l for l in an.splitlines() if any(k in l for k in ('Registered', 'Points', 'reprojection', 'Observations'))])
json.dump(stats, open(L+'solve_stats.json', 'w'), indent=1)
json.dump(dict(normal=nr.tolist(), d=float(d), scale_m_per_unit=float(s), focal_px_1280=f, k1=k1, world_origin_frame=REF,
               world_from_colmap=dict(R=(Mrot*s).tolist(), O=O.tolist(), note='X_world = R @ (X_colmap - O)')),
          open(L+'ground_plane.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in stats.items() if k not in ('colmap_model_analyzer',)}, indent=0))
