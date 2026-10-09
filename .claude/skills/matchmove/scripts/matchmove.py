#!/usr/bin/env python3
"""Automatic matchmove: footage in, solved camera + QC out.

    python3 matchmove.py PLATE OUT_DIR [--sensor 36] [--focal 35]
        [--screen blue|green] [--mask-dir DIR] [--first-frame 1001]
        [--cam-height 1.6] [--max-size 1920]

PLATE is a video file, a folder of frames, or the first frame of a sequence.
Pipeline: frames -> optional bluescreen/greenscreen feature mask -> COLMAP
(SIFT, sequential matching, incremental SfM, RADIAL lens) -> level the scene
on the dominant ground plane -> per-frame error + QC overlay video -> Blender
export (FBX, Nuke .nk/.chan, .blend) via mm_export.py.
"""
import argparse, glob, json, os, re, shutil, subprocess, sys
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))


def run(cmd, log):
    with open(log, "w") as fh:
        r = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        sys.exit(f"Failed: {' '.join(cmd[:2])} (see {log})")


def probe_fps(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=r_frame_rate", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    try:
        n, d = out.split("/")
        return float(n) / float(d)
    except ValueError:
        return 24.0


def gather_frames(plate, frames_dir, first_frame):
    """Put the plate in frames_dir as <frame>.png, numbered from first_frame."""
    os.makedirs(frames_dir, exist_ok=True)
    exts = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".exr", ".dpx")
    if os.path.isdir(plate):
        src = sorted(p for p in glob.glob(os.path.join(plate, "*")) if p.lower().endswith(exts))
    elif plate.lower().endswith(exts):
        stem = re.sub(r"\d+(\.\w+)$", "", os.path.basename(plate))
        src = sorted(p for p in glob.glob(os.path.join(os.path.dirname(plate) or ".", stem + "*"))
                     if p.lower().endswith(exts))
    else:
        run(["ffmpeg", "-v", "error", "-y", "-i", plate, "-start_number", str(first_frame),
             "-vsync", "0", os.path.join(frames_dir, "%06d.png")], os.path.join(frames_dir, "..", "ffmpeg.log"))
        return probe_fps(plate)
    if not src:
        sys.exit(f"No frames found for {plate}")
    for i, p in enumerate(src):
        dst = os.path.join(frames_dir, f"{first_frame + i:06d}.png")
        if p.lower().endswith(".png"):
            shutil.copyfile(p, dst)
        else:  # EXR/DPX/TIF: convert to an 8-bit display-referred PNG for feature detection
            run(["ffmpeg", "-v", "error", "-y", "-i", p, dst], os.path.join(frames_dir, "..", "ffmpeg.log"))
    return 24.0


def screen_masks(frames_dir, mask_dir, color):
    """Feature mask for blue/green screen plates: keep the screen and its tracking
    markers, drop talent and other large non-screen objects in front of it."""
    os.makedirs(mask_dir, exist_ok=True)
    hue = {"blue": (95, 135), "green": (40, 85)}[color]
    coverage = []
    for p in sorted(glob.glob(os.path.join(frames_dir, "*.png"))):
        img = cv2.imread(p)
        h, w = img.shape[:2]
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        screen = cv2.inRange(hsv, (hue[0], 70, 40), (hue[1], 255, 255))
        # Non-screen blobs: small ones are tape markers (keep), big ones are
        # talent, props or off-screen areas (drop, with a safety margin).
        n, lab, stats, _ = cv2.connectedComponentsWithStats(255 - screen, connectivity=8)
        big = np.zeros_like(screen)
        limit = 0.0015 * w * h
        for i in range(1, n):
            if stats[i, cv2.CC_STAT_AREA] > limit:
                big[lab == i] = 255
        m = max(3, int(w * 0.01)) | 1
        big = cv2.dilate(big, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (m, m)))
        keep = np.where(big > 0, 0, 255).astype(np.uint8)
        cv2.imwrite(os.path.join(mask_dir, os.path.basename(p) + ".png"), keep)
        coverage.append(keep.mean() / 255)
    return float(np.mean(coverage))


def klt_features(frames_dir, mask_dir, feat_dir, match_list, overlap=12):
    """Track corners frame to frame with pyramidal Lucas-Kanade (forward-backward
    checked) and export them to COLMAP as features + raw matches. Unlike SIFT
    matching, this copes with identical-looking markers and low-texture screens."""
    os.makedirs(feat_dir, exist_ok=True)
    names = sorted(n for n in os.listdir(frames_dir) if n.endswith(".png"))
    first = cv2.imread(os.path.join(frames_dir, names[0]), cv2.IMREAD_GRAYSCALE)
    h, w = first.shape
    min_dist = max(6, w // 140)
    lk = dict(winSize=(21, 21), maxLevel=4,
              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 40, 0.01))

    def load(i):
        g = cv2.imread(os.path.join(frames_dir, names[i]), cv2.IMREAD_GRAYSCALE)
        m = None
        if mask_dir:
            mp = os.path.join(mask_dir, names[i] + ".png")
            if os.path.exists(mp):
                m = cv2.imread(mp, cv2.IMREAD_GRAYSCALE)
        return g, m

    def detect(g, m, existing):
        mm = np.full_like(g, 255) if m is None else m.copy()
        for x, y in existing:
            cv2.circle(mm, (int(x), int(y)), min_dist, 0, -1)
        c = cv2.goodFeaturesToTrack(g, maxCorners=1500, qualityLevel=0.02, minDistance=min_dist,
                                    mask=mm, blockSize=7)
        if c is None:
            return np.zeros((0, 2), np.float32)
        return cv2.cornerSubPix(g, c, (5, 5), (-1, -1),
                                (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01)).reshape(-1, 2)

    obs = [dict() for _ in names]  # frame -> {track_id: (x, y)}
    g0, m0 = load(0)
    pts = detect(g0, m0, [])
    ids = list(range(len(pts)))
    next_id = len(pts)
    for j, (x, y) in zip(ids, pts):
        obs[0][j] = (float(x), float(y))
    prev = g0
    for i in range(1, len(names)):
        g, m = load(i)
        if len(pts):
            p1, st, _ = cv2.calcOpticalFlowPyrLK(prev, g, pts.reshape(-1, 1, 2), None, **lk)
            p0r, st2, _ = cv2.calcOpticalFlowPyrLK(g, prev, p1, None, **lk)
            fb = np.linalg.norm(pts.reshape(-1, 2) - p0r.reshape(-1, 2), axis=1)
            p1 = p1.reshape(-1, 2)
            good = (st.ravel() == 1) & (st2.ravel() == 1) & (fb < 0.5) \
                & (p1[:, 0] >= 2) & (p1[:, 1] >= 2) & (p1[:, 0] < w - 2) & (p1[:, 1] < h - 2)
            if m is not None:
                xi = np.clip(p1[:, 0].astype(int), 0, w - 1); yi = np.clip(p1[:, 1].astype(int), 0, h - 1)
                good &= m[yi, xi] > 0
            pts = p1[good]
            ids = [t for t, k in zip(ids, good) if k]
        new = detect(g, m, pts)
        if len(new):
            pts = np.vstack([pts, new]) if len(pts) else new
            ids += list(range(next_id, next_id + len(new)))
            next_id += len(new)
        for j, (x, y) in zip(ids, pts):
            obs[i][j] = (float(x), float(y))
        prev = g

    # Keep tracks seen in at least 6 frames (short ones are mostly grain/noise).
    life = {}
    for o in obs:
        for t in o:
            life[t] = life.get(t, 0) + 1
    index = []
    for i, o in enumerate(obs):
        keep = [(t, xy) for t, xy in o.items() if life[t] >= 6]
        index.append({t: k for k, (t, _) in enumerate(keep)})
        with open(os.path.join(feat_dir, names[i] + ".txt"), "w") as fh:
            fh.write(f"{len(keep)} 128\n")
            zeros = " ".join(["0"] * 128)
            for _, (x, y) in keep:
                fh.write(f"{x:.4f} {y:.4f} 1 0 {zeros}\n")
    steps = sorted({1, 2, 3, 4, 6, 8, 12, 16, 24, 32} & set(range(1, overlap * 3)))
    with open(match_list, "w") as fh:
        for i in range(len(names)):
            for s in steps:
                j = i + s
                if j >= len(names):
                    break
                common = set(index[i]) & set(index[j])
                if len(common) < 8:
                    continue
                fh.write(f"{names[i]} {names[j]}\n")
                for t in common:
                    fh.write(f"{index[i][t]} {index[j][t]}\n")
                fh.write("\n")
    lens = [l for l in life.values() if l >= 6]
    return len(lens), float(np.median(lens)) if lens else 0.0


def read_model(txt):
    cam = [l.split() for l in open(os.path.join(txt, "cameras.txt")) if not l.startswith("#")][0]
    W, H = int(cam[2]), int(cam[3])
    f, cx, cy, k1, k2 = map(float, cam[4:9])
    pts = {}
    for l in open(os.path.join(txt, "points3D.txt")):
        if l.startswith("#"):
            continue
        v = l.split()
        pts[int(v[0])] = (np.array(list(map(float, v[1:4]))), float(v[7]))
    imgs = {}
    lines = [l for l in open(os.path.join(txt, "images.txt")) if not l.startswith("#")]
    for a, b in zip(lines[0::2], lines[1::2]):
        v = a.split()
        w, x, y, z = map(float, v[1:5])
        R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                      [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                      [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
        t = np.array(list(map(float, v[5:8])))
        frame = int(re.findall(r"(\d+)", v[9])[-1])
        obs = b.split()
        o = [(float(obs[i]), float(obs[i + 1]), int(obs[i + 2])) for i in range(0, len(obs), 3)
             if int(obs[i + 2]) >= 0]
        imgs[frame] = {"R": R, "t": t, "name": v[9], "obs": o}
    return (W, H, f, cx, cy, k1, k2), pts, imgs


def project(Xw, R, t, intr):
    W, H, f, cx, cy, k1, k2 = intr
    Xc = (R @ Xw.T).T + t
    z = np.where(np.abs(Xc[:, 2]) < 1e-9, 1e-9, Xc[:, 2])
    x, y = Xc[:, 0] / z, Xc[:, 1] / z
    r2 = x * x + y * y
    d = 1 + k1 * r2 + k2 * r2 * r2
    # In front of the camera and inside the field of view the lens model is valid for.
    rmax2 = ((W / 2) ** 2 + (H / 2) ** 2) / f ** 2 * 1.2
    ok = (Xc[:, 2] > 1e-6) & (r2 < rmax2)
    return np.stack([f * x * d + cx, f * y * d + cy], 1), ok


def ground_plane(P):
    """RANSAC the dominant plane (usually floor/ground). Returns (normal, point)."""
    rng = np.random.default_rng(0)
    best, best_n, best_p = 0, None, None
    scale = np.median(np.linalg.norm(P - np.median(P, 0), axis=1))
    for _ in range(600):
        a, b, c = P[rng.choice(len(P), 3, replace=False)]
        n = np.cross(b - a, c - a)
        if np.linalg.norm(n) < 1e-9:
            continue
        n /= np.linalg.norm(n)
        inl = np.abs((P - a) @ n) < 0.01 * scale
        if inl.sum() > best:
            best, best_n, best_p = inl.sum(), n, P[inl].mean(0)
    return best_n, best_p, best / len(P)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plate"); ap.add_argument("out")
    ap.add_argument("--sensor", type=float, default=36.0, help="sensor/film back width in mm")
    ap.add_argument("--focal", type=float, default=None, help="focal length in mm, if known")
    ap.add_argument("--screen", choices=["blue", "green"], default=None)
    ap.add_argument("--mask-dir", default=None, help="your own masks: <frame>.png.png, white = trackable")
    ap.add_argument("--first-frame", type=int, default=1001)
    ap.add_argument("--cam-height", type=float, default=None, help="real camera height (m) for scale")
    ap.add_argument("--max-size", type=int, default=1920, help="max image side for SIFT")
    ap.add_argument("--tracker", choices=["auto", "sift", "klt"], default="auto",
                    help="auto: KLT for screen plates, SIFT otherwise, retry the other if frames are missing")
    a = ap.parse_args()

    out = os.path.abspath(a.out)
    work = os.path.join(out, "work")
    frames = os.path.join(work, "frames")
    if os.path.exists(work):
        shutil.rmtree(work)
    os.makedirs(work)
    fps = gather_frames(os.path.abspath(a.plate), frames, a.first_frame)
    names = sorted(os.listdir(frames))
    h0, w0 = cv2.imread(os.path.join(frames, names[0])).shape[:2]
    print(f"{len(names)} frames {w0}x{h0} @ {fps:.3f} fps")

    mask_dir = a.mask_dir
    if a.screen and not mask_dir:
        mask_dir = os.path.join(work, "masks")
        cov = screen_masks(frames, mask_dir, a.screen)
        print(f"{a.screen}screen mask covers {cov:.0%} of the frame")
        if cov < 0.08:
            print("Screen too small for a useful mask; tracking the whole frame instead.")
            mask_dir = None

    reader = ["--ImageReader.single_camera", "1", "--ImageReader.camera_model", "RADIAL"]
    if a.focal:
        fpx = a.focal * w0 / a.sensor
        reader += ["--ImageReader.camera_params", f"{fpx},{w0 / 2},{h0 / 2},0,0"]

    def solve_with(tracker):
        d = os.path.join(work, tracker)
        os.makedirs(d)
        db = os.path.join(d, "db.db")
        if tracker == "sift":
            fe = ["colmap", "feature_extractor", "--database_path", db, "--image_path", frames, *reader,
                  "--SiftExtraction.use_gpu", "0", "--SiftExtraction.max_num_features", "4096",
                  "--SiftExtraction.max_image_size", str(a.max_size)]
            if mask_dir:
                fe += ["--ImageReader.mask_path", mask_dir]
            run(fe, os.path.join(d, "features.log"))
            run(["colmap", "sequential_matcher", "--database_path", db, "--SiftMatching.use_gpu", "0",
                 "--SequentialMatching.overlap", "12", "--SequentialMatching.quadratic_overlap", "1",
                 "--SequentialMatching.loop_detection", "0"], os.path.join(d, "matching.log"))
        else:
            feats, ml = os.path.join(d, "features"), os.path.join(d, "matches.txt")
            n_tracks, med_len = klt_features(frames, mask_dir, feats, ml)
            print(f"KLT: {n_tracks} tracks, median length {med_len:.0f} frames")
            run(["colmap", "feature_importer", "--database_path", db, "--image_path", frames,
                 "--import_path", feats, *reader], os.path.join(d, "features.log"))
            run(["colmap", "matches_importer", "--database_path", db, "--match_list_path", ml,
                 "--match_type", "raw", "--SiftMatching.use_gpu", "0"], os.path.join(d, "matching.log"))
        sparse = os.path.join(d, "sparse")
        os.makedirs(sparse)
        # KLT gives fewer, longer tracks: let the mapper start from fewer inliers.
        relaxed = ["--Mapper.init_min_num_inliers", "50", "--Mapper.abs_pose_min_num_inliers", "15"] \
            if tracker == "klt" else []
        run(["colmap", "mapper", "--database_path", db, "--image_path", frames, "--output_path", sparse,
             *relaxed, "--Mapper.ba_global_function_tolerance", "1e-6",
             "--Mapper.ba_global_images_ratio", "1.3", "--Mapper.ba_global_points_ratio", "1.3"],
            os.path.join(d, "mapper.log"))
        best, best_n = None, 0
        for m in (x for x in glob.glob(os.path.join(sparse, "*")) if os.path.isdir(x)):
            t = m + "_txt"
            os.makedirs(t, exist_ok=True)
            run(["colmap", "model_converter", "--input_path", m, "--output_path", t, "--output_type", "TXT"],
                os.path.join(d, "convert.log"))
            n = sum(1 for l in open(os.path.join(t, "images.txt")) if not l.startswith("#")) // 2
            if n > best_n:
                best, best_n = t, n
        print(f"{tracker}: solved {best_n}/{len(names)} frames")
        return best, best_n

    tracker = a.tracker if a.tracker != "auto" else ("klt" if a.screen else "sift")
    best, best_n = solve_with(tracker)
    if a.tracker == "auto" and best_n < 0.95 * len(names):
        other = "klt" if tracker == "sift" else "sift"
        print(f"{tracker} left frames unsolved; trying {other}")
        b2, n2 = solve_with(other)
        if n2 > best_n:
            best, best_n, tracker = b2, n2, other
    if not best:
        sys.exit("Could not solve this shot (no parallax? nodal pan? too little texture?). "
                 "See SKILL.md: Shots that fail.")
    intr, pts, imgs = read_model(best)
    W, H, f, cx, cy, k1, k2 = intr
    all_frames = [int(n[:-4]) for n in names]
    missing = [fr for fr in all_frames if fr not in imgs]

    # Per-frame reprojection error.
    pid = sorted(pts)
    P = np.array([pts[i][0] for i in pid])
    index = {p: i for i, p in enumerate(pid)}
    per_frame = {}
    for fr, im in imgs.items():
        if not im["obs"]:
            continue
        uv = np.array([(o[0], o[1]) for o in im["obs"]])
        X = P[[index[o[2]] for o in im["obs"]]]
        proj, _ = project(X, im["R"], im["t"], intr)
        per_frame[fr] = float(np.linalg.norm(proj - uv, axis=1).mean())

    # Level the scene: ground plane -> z=0, up -> +Z, scale from camera height.
    centers = {fr: -im["R"].T @ im["t"] for fr, im in imgs.items()}
    C = np.array(list(centers.values()))
    n, p0, frac = ground_plane(P)
    if (C.mean(0) - p0) @ n < 0:
        n = -n
    z = n
    xr = np.array([1.0, 0, 0]) if abs(z[0]) < 0.9 else np.array([0, 1.0, 0])
    x = np.cross(xr, z); x /= np.linalg.norm(x)
    y = np.cross(z, x)
    Rl = np.stack([x, y, z])  # rows: new axes in old coords
    height = float(np.median((C - p0) @ z))
    s = (a.cam_height / height) if a.cam_height else (1.6 / height if height > 1e-6 else 1.0)
    def lv(X):
        return s * ((X - p0) @ Rl.T)
    blender_flip = np.diag([1.0, -1.0, -1.0])  # COLMAP camera (+Z fwd, +Y down) -> Blender camera
    cam_world = {}
    for fr, im in sorted(imgs.items()):
        M = np.eye(4)
        M[:3, :3] = Rl @ im["R"].T @ blender_flip
        M[:3, 3] = lv(centers[fr])
        cam_world[fr] = M.tolist()
    PL = lv(P)
    ply = os.path.join(out, "points.ply")
    with open(ply, "w") as fh:
        fh.write(f"ply\nformat ascii 1.0\nelement vertex {len(PL)}\nproperty float x\nproperty float y\n"
                 f"property float z\nend_header\n")
        for q in PL:
            fh.write(f"{q[0]:.6f} {q[1]:.6f} {q[2]:.6f}\n")

    # QC overlay: tracked points (green, error-coloured) + a 1 m ground grid (cyan).
    qc_dir = os.path.join(work, "qc")
    os.makedirs(qc_dir)
    g = np.arange(-10, 10.01, 1.0)
    grid = []
    for v in g:
        grid.append((np.array([v, -10, 0]), np.array([v, 10, 0])))
        grid.append((np.array([-10, v, 0]), np.array([10, v, 0])))
    inv = lambda X: (X / s) @ Rl + p0  # leveled -> COLMAP world
    for name in names:
        fr = int(name[:-4])
        img = cv2.imread(os.path.join(frames, name))
        if fr in imgs:
            im = imgs[fr]
            for a3, b3 in grid:
                seg = inv(np.linspace(a3, b3, 80))
                uv, ok = project(seg, im["R"], im["t"], intr)
                for i in range(len(uv) - 1):
                    if ok[i] and ok[i + 1]:
                        cv2.line(img, tuple(np.int32(uv[i])), tuple(np.int32(uv[i + 1])), (255, 200, 0), 1, cv2.LINE_AA)
            if im["obs"]:
                X = P[[index[o[2]] for o in im["obs"]]]
                proj, _ = project(X, im["R"], im["t"], intr)
                for (u, v, _), q in zip(im["obs"], proj):
                    e = np.hypot(q[0] - u, q[1] - v)
                    col = (0, 255, 0) if e < 1 else (0, 200, 255) if e < 2 else (0, 0, 255)
                    cv2.circle(img, (int(q[0]), int(q[1])), 3, col, 1, cv2.LINE_AA)
            label = f"{fr}  err {per_frame.get(fr, 0):.2f}px"
        else:
            label = f"{fr}  NOT SOLVED"
        cv2.putText(img, label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(img, label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imwrite(os.path.join(qc_dir, name), img)
    run(["ffmpeg", "-v", "error", "-y", "-framerate", f"{fps:.3f}", "-start_number", str(all_frames[0]),
         "-i", os.path.join(qc_dir, "%06d.png"), "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
         "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", os.path.join(out, "qc_overlay.mp4")],
        os.path.join(work, "qc.log"))

    errs = np.array(list(per_frame.values()))
    solve = {
        "resolution": [W, H], "fps": fps, "sensor_mm": a.sensor,
        "focal_mm": round(f * a.sensor / W, 4), "focal_px": f, "k1": k1, "k2": k2,
        "focal_given": a.focal, "frames_total": len(all_frames), "frames_solved": len(imgs),
        "frames_missing": missing, "points": len(P),
        "reprojection_error_px": round(float(errs.mean()), 3),
        "worst_frames": sorted(((round(e, 3), fr) for fr, e in per_frame.items()), reverse=True)[:5],
        "ground_plane_inliers": round(frac, 3),
        "scale": "camera height %.2f m (%s)" % (a.cam_height or 1.6, "given" if a.cam_height else "ASSUMED"),
        "tracker": tracker,
        "screen_mask": a.screen if mask_dir else None,
        "points_ply": ply,
        "plate_first_frame": os.path.join(frames, names[0]),
        "camera_world": cam_world,
    }
    json.dump(solve, open(os.path.join(out, "solve.json"), "w"), indent=1)
    run(["blender", "-b", "--factory-startup", "--python", os.path.join(HERE, "mm_export.py"), "--",
         os.path.join(out, "solve.json"), out], os.path.join(work, "export.log"))
    summary = {k: v for k, v in solve.items() if k not in ("camera_world",)}
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
