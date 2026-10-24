# prep.py - resolve upstream inputs -> assets/ for the GROUND TRUTH mograph composition (sh010 mograph v001)
# run: /opt/vfx-ai/bin/python prep.py [--force]
# Every upstream file is read from its department folder. If a file is not delivered yet, a labelled
# placeholder is built in assets/ph/ (never written outside this folder). assets/manifest.json records which is which.
import json, os, sys, subprocess, hashlib, glob
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
U = os.path.abspath(HERE + '../../') + '/'          # shots/sh010/
A = HERE + 'assets/'; PH = A + 'ph/'; V = A + 'v/'
os.makedirs(V, exist_ok=True); os.makedirs(PH, exist_ok=True)
FORCE = '--force' in sys.argv
INK = (13, 16, 18)  # BGR of #12100D
man = {}

def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode: print(r.stderr[-2000:]); raise SystemExit('cmd failed: ' + cmd[:200])
    return r.stdout

def sig(*paths):
    h = hashlib.md5()
    for p in paths:
        st = os.stat(p); h.update(f'{p}{st.st_size}{st.st_mtime}'.encode())
    return h.hexdigest()

def stale(out, *srcs):
    """True if out must be rebuilt (missing, forced, or sources changed)."""
    s = sig(*srcs); sf = out + '.sig'
    if FORCE or not os.path.exists(out) or not os.path.exists(sf) or open(sf).read() != s:
        return s
    return None

def done(out, s): open(out + '.sig', 'w').write(s)

def nframes(p):
    return int(sh(f'ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "{p}"').strip().split(',')[0])

ENC = '-c:v libx264 -preset medium -crf 13 -g 1 -pix_fmt yuv420p -r 25 -an -movflags +faststart'

# ------------------------------------------------------------------ plate (graded, 0-based s0..s51)
PLD = 'color/v002/plate_graded/' if len(glob.glob(U + 'color/v002/plate_graded/plate.*.png')) == 52 else 'color/v001/plate_graded/'
PL = U + PLD + 'plate.%04d.png'
assert len(glob.glob(U + PLD + 'plate.*.png')) == 52
def plate(s): return cv2.imread(PL % s)

# stills for the TILT (s51) and the registration (s0) image planes: 2160x904 lanczos
for s in (0, 51):
    o = A + f'plate_s{s:02d}.png'
    k = stale(o, PL % s)
    if k:
        cv2.imwrite(o, cv2.resize(plate(s), (2160, 904), interpolation=cv2.INTER_LANCZOS4)); done(o, k)
man['plate'] = PLD + ' (real)'

# TRACK band video (lanczos 1.6875x of the graded plate), 52 frames
o = V + 'track_band.mp4'; k = stale(o, PL % 0, PL % 51)
if k:
    sh(f'ffmpeg -v error -y -framerate 25 -start_number 0 -i "{PL}" -frames:v 52 -vf "scale=2160:904:flags=lanczos" {ENC} "{o}"'); done(o, k)

# ------------------------------------------------------------------ credits underlay (the visible list is native DOM type)
CR2 = U + 'color/v002/credits_graded_v002.mp4'
if os.path.exists(CR2) and nframes(CR2) == 69:
    CR = CR2; lift = ''; man['credits'] = 'color/v002/credits_graded_v002.mp4 (real) -> blurred glow underlay'
else:
    CR = U + 'color/v001/credits_graded.mp4'; man['credits'] = 'color/v001/credits_graded.mp4 (v002 not delivered; lifted here) -> blurred glow underlay'
    lift = "curves=all='0/0 0.08/0.085 0.22/0.40 0.45/0.78 0.70/0.93 1/0.97',"
o = V + 'credits.mp4'; k = stale(o, CR, HERE + 'prep.py')
if k:
    sh(f'ffmpeg -v error -y -i "{CR}" -vf "{lift}scale=2160:3840:flags=lanczos,gblur=sigma=10" {ENC} "{o}"'); done(o, k)
assert nframes(o) == 69, 'credits must be 69 frames'
RT = json.load(open(U + 'edit/v001/row_track.json'))

# ------------------------------------------------------------------ layout JSONs
LY = U + 'layout/v001/'
def layout_ok():
    try:
        c = json.load(open(LY + 'cams.json'))
        return len(c['frames']) == 52 and all(os.path.exists(LY + n) for n in ('points.json', 'tracks.json', 'solve_stats.json', 'anchor.json'))
    except Exception:
        return False
if layout_ok():
    LD = LY; man['layout'] = 'layout/v001 (real)'
else:
    LD = PH + 'layout/'; man['layout'] = 'PLACEHOLDER assets/ph/layout (director cm3_beach 37-frame solve)'
cams = json.load(open(LD + 'cams.json')); pts = json.load(open(LD + 'points.json'))
trk = json.load(open(LD + 'tracks.json')); st = json.load(open(LD + 'solve_stats.json'))
W, H = cams['width'], cams['height']; f, cx, cy, k1 = cams['f'], cams['cx'], cams['cy'], cams['k1']
CF = sorted(cams['frames'], key=lambda c: c['frame']); TF = {t['frame']: t for t in trk['frames']}
nC = len(CF)
def cam_s(s):  # s index 0..51 -> camera entry (identity when 52 frames)
    return CF[int(round(s * (nC - 1) / 51))]

def project(c, X):
    R = np.array(c['R']); t = np.array(c['t']); Xc = X @ R.T + t
    x, y = Xc[:, 0] / Xc[:, 2], Xc[:, 1] / Xc[:, 2]; r2 = x * x + y * y
    return np.c_[f * x * (1 + k1 * r2) + cx, f * y * (1 + k1 * r2) + cy], Xc[:, 2]

# anchor (real anchor.json, else computed here with the treatment's placement)
if os.path.exists(LD + 'anchor.json'):
    an = json.load(open(LD + 'anchor.json')); man['anchor'] = LD.replace(U, '') + 'anchor.json'
    AX, AY, _ = an['anchor']['location']; AR = an['anchor']['rot_z_deg']; TOPZ = an['monument_bounds_world']['max'][2]
    AF = sorted(an['frames'], key=lambda q: q['frame'])
else:
    AX, AY, AR, TOPZ = 1.5, 12.5, -12.0, 3.99; AF = None; man['anchor'] = 'PLACEHOLDER computed in prep.py (1.5, 12.5, rz -12)'
ca, sa = np.cos(np.radians(AR)), np.sin(np.radians(AR))
def a2w(lx, ly, lz): return np.array([AX + ca * lx - sa * ly, AY + sa * lx + ca * ly, lz])
corners_l = {'front_left': (-3.9, -0.5), 'front_right': (3.9, -0.5), 'back_right': (3.9, 0.5), 'back_left': (-3.9, 0.5)}
anc = []
if AF is None or len(AF) != 52:
    crs = []
    for s in range(52):
        c = cam_s(s); P = {kk: project(c, a2w(x, y, 0)[None])[0][0] for kk, (x, y) in corners_l.items()}
        cen = project(c, a2w(0, 0, TOPZ / 2)[None])[0][0]; crs.append(cen[0] * 1280 / W)
        anc.append(dict(corners={kk: (v * 1280 / W).tolist() for kk, v in P.items()}, centre=(cen * 1280 / W).tolist()))
    crs = np.array(crs); g = np.exp(-0.5 * (np.arange(-12, 13) / 6.0) ** 2); g /= g.sum()
    cs = np.clip(np.convolve(np.r_[np.full(12, crs[0]), crs, np.full(12, crs[-1])], g, 'valid'), 493, 787)
    for s in range(52): anc[s]['crop_cx'] = float(cs[s])
else:
    sc = 1280 / W
    for q in AF:
        anc.append(dict(corners={kk: [v[0] * sc, v[1] * sc] for kk, v in q['corners'].items()}, centre=[q['centre'][0] * sc, q['centre'][1] * sc],
                        crop_cx=q['crop_cx'] * sc))

# ------------------------------------------------------------------ monument wireframe (Unbounded 900 glyph outlines, anchor-local metres)
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
FONT = A + 'fonts/Unbounded-900.ttf'
ft = TTFont(FONT); gs = ft.getGlyphSet(); cmap = ft.getBestCmap(); upm = ft['head'].unitsPerEm
capH = ft['OS/2'].sCapHeight
def glyph_contours(ch):
    gn = cmap[ord(ch)]; pen = RecordingPen(); gs[gn].draw(pen); cs, cur = [], []
    for op, args in pen.value:
        if op == 'moveTo': cur = [args[0]]
        elif op == 'lineTo': cur.append(args[0])
        elif op in ('qCurveTo', 'curveTo'):
            p0 = np.array(cur[-1], float); ctrl = [np.array(a, float) for a in args]
            if op == 'qCurveTo' and len(ctrl) == 1:
                cur.append(tuple(ctrl[0]))
            elif op == 'qCurveTo':
                # TrueType implied on-curve points
                segs = []; pts_ = ctrl
                for i in range(len(pts_) - 1):
                    c1 = pts_[i]; e = pts_[i + 1] if i == len(pts_) - 2 else (pts_[i] + pts_[i + 1]) / 2
                    segs.append((c1, e))
                for c1, e in segs:
                    for u in np.linspace(0, 1, 7)[1:]:
                        cur.append(tuple((1 - u) ** 2 * p0 + 2 * (1 - u) * u * c1 + u * u * e))
                    p0 = e
            else:
                c1, c2, e = ctrl
                for u in np.linspace(0, 1, 9)[1:]:
                    cur.append(tuple((1 - u) ** 3 * p0 + 3 * (1 - u) ** 2 * u * c1 + 3 * (1 - u) * u * u * c2 + u ** 3 * e))
        elif op in ('closePath', 'endPath'):
            if len(cur) > 2: cs.append(np.array(cur, float))
            cur = []
    return cs, ft['hmtx'][gn][0]
lines = ['VINAY', 'KRISHAN', 'ROHILLA']; L = []
for ln in lines:
    x = 0; cs_all = []
    for ch in ln:
        cs, adv = glyph_contours(ch)
        for c in cs: cs_all.append(c + [x, 0])
        x += adv
    L.append((cs_all, x))
wmax = max(w for _, w in L); sc = 7.2 / wmax                      # 7.2 m wide (widest line)
textH = TOPZ - 0.24; pitch = (textH / sc - capH) / 2                 # fit the stacked height to the real bounds
mono = []
for i, (cs, w) in enumerate(L):
    base = (2 - i) * pitch
    for c in cs:
        q = np.c_[(c[:, 0] - w / 2) * sc, (c[:, 1] + base) * sc + 0.24]
        mono.append(np.round(q, 4).tolist())
man['monument_wire'] = f'Unbounded 900 outlines, width 7.2 m, top z {TOPZ:.3f} m, line pitch {pitch*sc:.3f} m'

# ------------------------------------------------------------------ comp bands (real .mov -> intra mp4; else placeholder)
def newest(dept, name):
    # newest version folder of a department that holds this file
    c = sorted(glob.glob(U + dept + '/v*/' + name))
    return c[-1] if c else None
CP = U + 'comp/v001/'
def ph_band(name, w, h, kind):
    """placeholder band video: graded plate (+ a bone box where the monument goes), labelled."""
    o = PH + name + '.mp4'; k = stale(o, PL % 0, HERE + 'prep.py', *( [LD + 'anchor.json'] if os.path.exists(LD + 'anchor.json') else []))
    if not k: return o
    tmp = PH + 'tmp_' + name; os.makedirs(tmp, exist_ok=True)
    for s in range(52):
        if kind == 'cg': im = np.full((h, w, 3), (0x5C, 0x66, 0x6E), np.uint8)
        else: im = cv2.resize(plate(s), (w, h), interpolation=cv2.INTER_LANCZOS4)
        if kind in ('cg', 'final'):
            fall = 5 * (1 - (s / 4) ** 2) if s <= 4 else 0
            c = cam_s(s); box = np.array([a2w(x, y, z + fall) for x in (-3.9, 3.9) for y in (-0.5, 0.5) for z in (0, TOPZ)])
            uv, _ = project(c, box); uv = uv * (w / W)
            x0, y0 = uv.min(0).astype(int); x1, y1 = uv.max(0).astype(int)
            ov = im.copy(); cv2.rectangle(ov, (x0, y0), (x1, y1), (211, 225, 233), -1); im = cv2.addWeighted(ov, 0.75, im, 0.25, 0)
        cv2.putText(im, f'PLACEHOLDER {name} s{s:02d}', (int(30 * w / 2160), int(80 * w / 2160)), cv2.FONT_HERSHEY_SIMPLEX, 1.6 * w / 2160, (40, 40, 200), 3)
        cv2.imwrite(f'{tmp}/f.{s:04d}.png', im)
    sh(f'ffmpeg -v error -y -framerate 25 -start_number 0 -i "{tmp}/f.%04d.png" {ENC} "{o}"'); done(o, k)
    return o
for name, w, h, kind in (('final_band_2808x1176', 2808, 1176, 'final'), ('plate_band_2160x904', 2160, 904, 'plate'),
                         ('cg_band_2160x904', 2160, 904, 'cg'), ('final_band_2160x904', 2160, 904, 'final')):
    SEQ = {'final_band_2808x1176': 'final_2808/final', 'final_band_2160x904': 'final_2160/final', 'plate_band_2160x904': 'plate_2160/plate', 'cg_band_2160x904': 'cg_2160/cg'}
    seqd = sorted(glob.glob(U + 'comp/v*/' + SEQ[name].split('/')[0]))
    if seqd and len(glob.glob(seqd[-1] + '/*.png')) == 52:
        sq = seqd[-1] + '/' + SEQ[name].split('/')[1] + '.%04d.png'; o = V + name + '.mp4'
        k = stale(o, sq % 0, sq % 51)
        if k:   # lossless PNG sequence from the compositor (already flattened over its ground)
            sh(f'ffmpeg -v error -y -framerate 25 -start_number 0 -i "{sq}" -frames:v 52 -vf "scale={w}:{h}:flags=lanczos" {ENC} "{o}"'); done(o, k)
        man[name] = sq.replace(U, '') + ' (real, PNG sequence)'
        assert nframes(o) == 52, name
        continue
    src = newest('comp', name + '.mov') or (CP + name + '.mov'); o = V + name + '.mp4'
    real = os.path.exists(src) and nframes(src) == 52
    if real:
        k = stale(o, src)
        if k:
            bg = '0x6E665C' if kind == 'cg' else '0x12100D'   # flatten any alpha over the right ground
            sh(f'ffmpeg -v error -y -f lavfi -i "color=c={bg}:s={w}x{h}:r=25" -i "{src}" -filter_complex '
               f'"[1:v]scale={w}:{h}:flags=lanczos,format=rgba[f];[0:v][f]overlay=shortest=1" -frames:v 52 {ENC} "{o}"'); done(o, k)
        man[name] = src.replace(U, '') + ' (real)'
    else:
        p = ph_band(name, w, h, kind); sh(f'cp "{p}" "{o}"'); man[name] = 'PLACEHOLDER (comp not delivered)'
    assert nframes(o) == 52, name

# breakdown stack: 52 frames + 2-frame hold of s51 for the fold (f273-274) = 54 frames
for name, src in (('bd_plate', 'plate_band_2160x904'), ('bd_track', 'plate_band_2160x904'), ('bd_cg', 'cg_band_2160x904'), ('bd_final', 'final_band_2160x904')):
    i = V + src + '.mp4'; o = V + name + '.mp4'; k = stale(o, i)
    if k: sh(f'ffmpeg -v error -y -i "{i}" -vf "tpad=stop_mode=clone:stop=2" {ENC} "{o}"'); done(o, k)
    assert nframes(o) == 54, name

# ------------------------------------------------------------------ ambient bleed: 540x960, timeline-mapped, 375 frames
o = V + 'bleed.mp4'; k = stale(o, PL % 0, PL % 51, HERE + 'prep.py')
if k:
    tmp = PH + 'tmp_bleed'; os.makedirs(tmp, exist_ok=True)
    cache = {}
    def bl(s, desat=0.0):
        key = (s, desat)
        if key not in cache:
            im = plate(s); hh = 960; ww = int(round(im.shape[1] * hh / im.shape[0]))
            im = cv2.resize(im, (ww, hh), interpolation=cv2.INTER_AREA); x0 = (ww - 540) // 2; im = im[:, x0:x0 + 540]
            im = cv2.GaussianBlur(im, (0, 0), 10)
            hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(np.float32); hsv[..., 1] = np.clip(hsv[..., 1] * 1.1, 0, 255)
            im = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
            if desat:
                g = cv2.cvtColor(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR); im = cv2.addWeighted(im, 1 - desat, g, desat, 0)
            cache[key] = im
        return cache[key]
    blank = np.zeros((960, 540, 3), np.uint8); blank[:] = INK
    for F in range(375):
        if 69 <= F <= 120: im = bl(F - 69)
        elif 121 <= F <= 136: im = bl(51, 0.3)
        elif 169 <= F <= 272: im = bl((F - 169) % 52 if F <= 220 else F - 221)
        else: im = blank
        cv2.imwrite(f'{tmp}/f.{F:04d}.png', im)
    sh(f'ffmpeg -v error -y -framerate 25 -start_number 0 -i "{tmp}/f.%04d.png" {ENC} "{o}"'); done(o, k)

# ------------------------------------------------------------------ title stills + logo
LT = U + 'lighting/v001/'
for nm in ('title_bg', 'title_fg'):
    src = newest('lighting', nm + '.png') or (LT + nm + '.png'); o = A + nm + '.png'
    if os.path.exists(src):
        k = stale(o, src)
        if k: sh(f'cp "{src}" "{o}"'); done(o, k)
        man[nm] = src.replace(U, '') + (' (real)' if '/v001/' not in src else ' (OLD design: waiting for the re-lit v002 still)')
    else:
        # placeholder: the newest lighting proxy pair (pNN_bg / pNN_fg), upscaled and labelled
        prox = sorted(glob.glob(LT + 'title/p*_' + nm.split('_')[1] + '.png'))
        if prox:
            im = cv2.imread(prox[-1], cv2.IMREAD_UNCHANGED); im = cv2.resize(im, (2160, 3840), interpolation=cv2.INTER_LANCZOS4)
            if nm == 'title_bg': cv2.putText(im, 'PLACEHOLDER ' + os.path.basename(prox[-1]), (180, 240), cv2.FONT_HERSHEY_SIMPLEX, 2.2, (40, 40, 200), 5)
            cv2.imwrite(o, im)
        else:
            cv2.imwrite(o, np.zeros((3840, 2160, 4), np.uint8))
        man[nm] = 'PLACEHOLDER'
LG = U + 'color/v001/sf_logo_bone.png'; o = A + 'sf_logo_bone.png'; k = stale(o, LG)
if k: sh(f'cp "{LG}" "{o}"'); done(o, k)
man['logo'] = 'color/v001/sf_logo_bone.png (real)'

def rgba_glow(g):
    """additive glow -> straight-alpha RGBA (alpha = peak channel), so it composites correctly in any group"""
    g = np.clip(g, 0, 255); al = g.max(2, keepdims=True); c = np.where(al > 0, g * 255.0 / np.maximum(al, 1), 0)
    return np.dstack([np.clip(c, 0, 255), al]).astype(np.uint8)
# logo rim glow (screen copy, blur 18 px at display size ~0.55x -> 32 px at native)
o = A + 'sf_logo_glow.png'; k = stale(o, LG)
if k:
    im = cv2.imread(LG, cv2.IMREAD_UNCHANGED).astype(np.float32); a_ = im[..., 3:4] / 255.0
    g = cv2.GaussianBlur(im[..., :3] * a_, (0, 0), 32); cv2.imwrite(o, rgba_glow(g)); done(o, k)
# line-up (restored by the colorist) for the bottom of the credits act only
LU = U + 'restore/v001/lineup_restored_2160_r470.png' if os.path.exists(U + 'restore/v001/lineup_restored_2160_r470.png') else U + 'restore/v001/lineup_restored_2160.png'
LU2 = sorted(glob.glob(U + 'color/v00*/lineup_restored_2160.png'))
src_lu = LU if os.path.exists(LU) else (LU2[-1] if LU2 else None)
o = A + 'lineup.png'
if src_lu:
    k = stale(o, src_lu, HERE + 'scripts/sky_key.py')
    if k:
        im = cv2.imread(src_lu, cv2.IMREAD_UNCHANGED)
        if im.shape[2] == 3: im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
        if im.shape[1] != 2160: im = cv2.resize(im, (2160, int(round(im.shape[0] * 2160 / im.shape[1]))), interpolation=cv2.INTER_AREA)
        cv2.imwrite(o, im); sh(f'/opt/vfx-ai/bin/python "{HERE}scripts/sky_key.py" "{o}" "{o}"'); done(o, k)
    man['lineup'] = src_lu.replace(U, '') + ' (real, sky keyed to Ink by scripts/sky_key.py)'
else:
    k = stale(o, ROOT_LU := os.path.abspath(U + '../../assets_prev/lineup.png'), HERE + 'prep.py')
    if k:
        im = cv2.imread(ROOT_LU, cv2.IMREAD_UNCHANGED)
        im = cv2.resize(im, (2160, 1320), interpolation=cv2.INTER_AREA)[420:1320].copy()     # src rows 560-1760, 0.75x
        ramp_ = np.clip(np.arange(900) / 300.0, 0, 1) ** 1.6
        im[..., 3] = (im[..., 3].astype(np.float32) * ramp_[:, None]).astype(np.uint8)
        cv2.putText(im, 'PLACEHOLDER lineup (not restored)', (60, 880), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (40, 40, 200), 3)
        cv2.imwrite(o, im); done(o, k)
    man['lineup'] = 'PLACEHOLDER assets_prev/lineup.png (restore not delivered)'
o2 = A + 'lineup_glow.png'; k = stale(o2, o)
if k:
    im = cv2.imread(o, cv2.IMREAD_UNCHANGED).astype(np.float32); a_ = im[..., 3:4] / 255.0
    cv2.imwrite(o2, rgba_glow(cv2.GaussianBlur(im[..., :3] * a_, (0, 0), 30))); done(o2, k)
LUH = cv2.imread(o, cv2.IMREAD_UNCHANGED).shape[0]

# the verbatim list: 3 rows visible above credits.txt's first line at f0 (read from source/movie.mp4 67.40 s), then credits.txt
PRE = [['SHASHIKANTH B TUPSUNDAR', 'SURAJ PANKAJ MISTRY'], ['SHATADRU BOSE', 'SURESH KOTHARI'], ['SHEELVANT SINGH', 'SURYA K']]
rows = PRE[:]
for ln in open(os.path.abspath(U + '../../source/credits.txt')).read().split('\n'):
    if '|' in ln: l_, r_ = [q.strip() for q in ln.split('|', 1)]; rows.append([l_, r_])
    elif ln.strip() == '': rows.append(['', ''])
while rows and rows[-1] == ['', '']: rows.pop()
HIS = [i for i, r in enumerate(rows) if r[1] == 'VINAY KRISHAN ROHILLA'][0]
assert rows[HIS][0] == 'VAMSI KRISHNA EADALA'

# FINAL window centre: monument centre x (plate px), Gaussian sigma 6 (clamped per frame in the page for the current scale)
cxr = np.array([q['centre'][0] for q in anc]); g_ = np.exp(-0.5 * (np.arange(-12, 13) / 6.0) ** 2); g_ /= g_.sum()
FCX = np.convolve(np.r_[np.full(12, cxr[0]), cxr, np.full(12, cxr[-1])], g_, 'valid').round(2).tolist()

# grain tile (seeded)
o = A + 'grain.png'
if not os.path.exists(o):
    rng = np.random.default_rng(7); g = np.clip(128 + rng.normal(0, 46, (512, 512)), 0, 255).astype(np.uint8)
    cv2.imwrite(o, cv2.cvtColor(g, cv2.COLOR_GRAY2BGR))

# ------------------------------------------------------------------ data.js
P = np.array([p['xyz'] for p in pts['points']], float); RGB = np.array([p['rgb'] for p in pts['points']], int)
G = np.array([p.get('ground', False) for p in pts['points']], bool)
ids = np.array([p['id'] for p in pts['points']])
camsJS = []
for s in range(52):
    c = cam_s(s); camsJS.append(dict(R=np.round(np.array(c['R']), 7).flatten().tolist(), t=np.round(c['t'], 5).tolist(),
                                       C=np.round(c['C'], 5).tolist(), src=c.get('src_frame', 2982 + s), n=c.get('n_tracks', 0)))
trJS = []
for s in range(52):
    c = cam_s(s); t = TF[c['frame']]; a = np.array(t['pts'], float).reshape(-1, 3)
    a[:, :2] *= 1280 / W
    trJS.append(np.round(a, 1).flatten().tolist())
# per-frame observation order for the registration (point id -> index in pts list)
idx = {int(i): n for n, i in enumerate(ids)}
D = dict(manifest=man, W=1280, H=536, f=f * 1280 / W, cx=cx * 1280 / W, cy=cy * 1280 / W, k1=k1,
         cams=camsJS, pts=np.round(np.c_[P, RGB, G], 4).flatten().tolist(), pid=ids.tolist(), tracks=trJS,
         stats={kk: st[kk] for kk in ('cameras_registered', 'cameras_total', 'points', 'ground_points', 'observations', 'mean_reproj_px',
                                      'median_reproj_px', 'camera_model', 'f_px', 'lens_mm_36', 'hfov_deg', 'k1', 'camera_travel_m',
                                      'rotation_span_deg') if kk in st},
         anchor=dict(loc=[AX, AY], rot=AR, top=TOPZ, frames=anc), mono=mono,
         cred=dict(rows=rows, his=HIS), lineupH=LUH, fcx=FCX,
         row=[dict(y=q['y'], x0=q['name_x0'], x1=q['name_x1']) for q in sorted(RT['frames'], key=lambda q: q['f'])])
open(A + 'data.js', 'w').write('window.D=' + json.dumps(D, separators=(',', ':')) + ';')
json.dump(man, open(A + 'manifest.json', 'w'), indent=1)
print(json.dumps(man, indent=1)); print('stats', D['stats'])
print('data.js', os.path.getsize(A + 'data.js') // 1024, 'KB; points', len(P), '; mono contours', len(mono))
