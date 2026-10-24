#!/usr/bin/env python3
"""qc_rgb.py - per-frame warm-balance QC for SUPER ART (treatment section 5).

Rule: every frame's mean R >= mean B (no blue cast). Also reported per frame:
  - black floor: % of pixels darker than Aubergine Ink #14080F (luma < its luma; info, not a fail)
  - pure white: % of pixels at (255,255,255) (fail only if > --white-max %, flash frames excepted)

Decodes with ffmpeg as full-range RGB using the Rec.709 matrix (the file's own tags if present).

Usage:
  python3 qc_rgb.py plates/B01.mp4 [more.mp4 | frame.png ...]
  python3 qc_rgb.py --margin 2 --json out.json --flash 261,262 plates/*.mp4
Options:
  --margin M     require mean R >= mean B + M (8-bit units, default 0)
  --white-max P  max % of pure-255 white pixels per frame (default 0.5)
  --flash a,b    frame indices exempt from the white check
  --json PATH    write the per-frame table
Exit code 0 = all pass, 1 = any frame fails, 2 = decode error.
"""
import argparse, json, subprocess, sys
import numpy as np

AUB_LUMA = 0.2126 * 0x14 + 0.7152 * 0x08 + 0.0722 * 0x0F   # ~10.0 in 8-bit


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                          'stream=width,height,color_space,color_range', '-of', 'json', path],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)['streams'][0]


def frames(path):
    st = probe(path)
    w, h = int(st['width']), int(st['height'])
    rng = 'pc' if st.get('color_range') == 'pc' else 'tv'
    is_img = path.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff'))
    vf = 'format=rgb24' if is_img else f'scale=in_color_matrix=bt709:in_range={rng}:out_range=pc,format=rgb24'
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-i', path, '-vf', vf,
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    n = w * h * 3
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        yield np.frombuffer(buf, np.uint8).reshape(h, w, 3)
    if p.wait() != 0:
        raise RuntimeError(f'ffmpeg failed on {path}')


def check(path, margin=0.0, white_max=0.5, flash=()):
    rows, fails = [], 0
    for i, f in enumerate(frames(path)):
        m = f.reshape(-1, 3).mean(0)
        y = f.astype(np.float32) @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        below = float((y < AUB_LUMA - 0.5).mean() * 100)
        white = float((f.min(axis=2) == 255).mean() * 100)
        ok_rb = m[0] >= m[2] + margin
        ok_w = white <= white_max or i in flash
        ok = bool(ok_rb and ok_w)
        fails += not ok
        rows.append(dict(f=i, R=round(float(m[0]), 2), G=round(float(m[1]), 2), B=round(float(m[2]), 2),
                         RminusB=round(float(m[0] - m[2]), 2), below_aub_pct=round(below, 3),
                         white_pct=round(white, 3), ok=ok))
    return rows, fails


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+')
    ap.add_argument('--margin', type=float, default=0.0)
    ap.add_argument('--white-max', type=float, default=0.5)
    ap.add_argument('--flash', default='')
    ap.add_argument('--json')
    a = ap.parse_args()
    flash = {int(x) for x in a.flash.split(',') if x.strip()}
    report, total_fail = {}, 0
    for path in a.files:
        try:
            rows, fails = check(path, a.margin, a.white_max, flash)
        except Exception as e:  # noqa
            print(f'ERROR {path}: {e}'); sys.exit(2)
        total_fail += fails
        rb = [r['RminusB'] for r in rows]
        worst = min(rows, key=lambda r: r['RminusB']) if rows else None
        print(f"{'PASS' if fails == 0 else 'FAIL'}  {path}  frames={len(rows)}  "
              f"R-B min={min(rb):.1f} mean={np.mean(rb):.1f} (worst f{worst['f']})  "
              f"below-Aubergine max={max(r['below_aub_pct'] for r in rows):.2f}%  "
              f"white max={max(r['white_pct'] for r in rows):.2f}%")
        for r in rows:
            if not r['ok']:
                print(f"   fail f{r['f']}: R={r['R']} G={r['G']} B={r['B']} white={r['white_pct']}%")
        report[path] = rows
    if a.json:
        json.dump(report, open(a.json, 'w'), indent=1)
    sys.exit(1 if total_fail else 0)


if __name__ == '__main__':
    main()
