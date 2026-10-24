#!/usr/bin/env python3
"""Grade editor plates as they land (or get replaced). Polls every 60 s; a plate is taken once it is >45 s old.
watch_plates.py [--minutes 120] [--once]"""
import argparse, json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "../../../.."))
SRC = os.path.join(PROJ, "shots/sh010/edit/v001/plates"); DST = os.path.join(HERE, "plates")
cues = json.load(open(os.path.join(HERE, "../../director/v001/cues.json")))
IDS = {s["id"]: s["frames"] for s in cues["shots"]} | {t["id"]: t["clip_frames"] for t in cues["tiles"]}
def outs(i): return [os.path.join(DST, i + s + ".mp4") for s in (["_duo", "_true"] if i.startswith("T") else [""])]
def log(m):
    m = time.strftime("%H:%M:%S ") + m; print(m, flush=True); open(os.path.join(HERE, "watch_log.txt"), "a").write(m + "\n")
ap = argparse.ArgumentParser(); ap.add_argument("--minutes", type=float, default=120); ap.add_argument("--once", action="store_true")
a = ap.parse_args(); end = time.time() + a.minutes * 60
while True:
    for i in IDS:
        src = os.path.join(SRC, i + ".mp4")
        if not os.path.exists(src): continue
        st = os.stat(src)
        if st.st_size < 10000 or time.time() - st.st_mtime < 45: continue
        o = outs(i)
        if all(os.path.exists(x) and os.path.getmtime(x) > st.st_mtime for x in o): continue
        log(f"grading {i} (src mtime {time.strftime('%H:%M:%S', time.localtime(st.st_mtime))}, expect {IDS[i]} f)")
        r = subprocess.run([sys.executable, os.path.join(HERE, "grade_plate.py"), i], capture_output=True, text=True)
        log((r.stdout + r.stderr).strip())
        if os.stat(src).st_mtime != st.st_mtime:
            log(f"{i} source changed during grading; will regrade"); [os.utime(x, (0, 0)) for x in o if os.path.exists(x)]; continue
        q = subprocess.run([sys.executable, os.path.join(HERE, "qc_rgb.py")] + o, capture_output=True, text=True)
        log(q.stdout.strip()); open(os.path.join(HERE, "qc_log.txt"), "a").write(q.stdout)
    done = sum(all(os.path.exists(x) for x in outs(i)) for i in IDS)
    if a.once or time.time() > end: log(f"stop: {done}/{len(IDS)} graded"); break
    time.sleep(60)
