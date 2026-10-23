#!/usr/bin/env python3
"""Editor B: frame-map plan for C00, B01-B08. Reads cues.json + librarian shots.json only.
Writes edl_B.json (per master frame: source position in trailer frames)."""
import json, math, sys
ROOT = "/home/user/rohillavinaykrishan"
P = ROOT + "/projects/sukanya-v2"
cues = json.load(open(P + "/shots/sh010/director/v001/cues.json"))
lib = json.load(open(ROOT + "/library/streetfighter-trailer/shots.json"))
T = 1001 / 24000.0           # trailer frame duration
MFPS = 25.0
Q = 24                        # minterpolate sub-steps per source frame for retimes
CONTACT_F = cues["events"]["DROP"]["f"]          # 261
shots = {s["id"]: s for s in cues["shots"]}

def libshot(t):
    for x in lib["shots"]:
        if x["in"] <= t < x["out"]:
            return x
    raise SystemExit("no lib shot for %s" % t)

def pos(t):                   # source time -> source frame position (float)
    return t / T

out = {"fps": 25, "size": "2400x900", "source": "source/trailer.mp4",
       "source_fps": "24000/1001", "timing_source": "shots/sh010/director/v001/cues.json",
       "prep": "crop=1280:536:0:92,pad=1280:540:0:4,deblock=filter=strong:block=8,crop=1280:536:0:4 -> [minterpolate mci x24 for C00/B01] -> scale 2400:1005 lanczos -> crop 2400:900:0:Y -> unsharp=5:5:0.4",
       "plates": []}
for sid in ["C00"] + ["B%02d" % i for i in range(1, 9)]:
    s = shots[sid]
    n = s["f_out"] - s["f_in"]
    ls = libshot(s["src_in"])
    lo, hi = ls["in_frame"], ls["out_frame"]
    p_in, p_out = pos(s["src_in"]), pos(s["src_out"])
    rec = {"id": sid, "f_in": s["f_in"], "f_out": s["f_out"], "frames": n,
           "src_in": s["src_in"], "src_out": s["src_out"], "lib_shot": ls["id"],
           "lib_frames": [lo, hi], "crop_cue": s["crop"]}
    if sid == "C00":
        # linear slow-mo; the position at f_out (=f261) is exactly the contact frame
        pc = round(pos(s["src_out"]))                       # 3452
        speed = (s["src_out"] - s["src_in"]) / (n / MFPS)
        p = [pc - (n - k) * speed * (1 / T) / MFPS for k in range(n)]
        rec.update(mode="minterpolate", speed=round(speed, 4), contact_src_frame=pc)
    elif sid == "B01":
        pc = round(pos(s["src_in"]))                         # 3452 = contact on f261
        p_end = pc + math.floor((p_out - pc) * Q) / Q        # last sub-step before src_out
        D = p_end - pc
        v0 = (1 / T) / MFPS                                  # 100% speed in src frames per master frame
        ramp = 11                                            # f261..f272, freeze f272-276
        # geometric speed decay v0*r^k, k=0..ramp-1, summing to D (100% at the contact)
        lo_r, hi_r = 0.0, 0.999
        for _ in range(100):
            r = (lo_r + hi_r) / 2
            if v0 * (1 - r ** ramp) / (1 - r) > D: hi_r = r
            else: lo_r = r
        p = [pc]
        for k in range(1, n):
            kk = min(k, ramp)
            p.append(pc + v0 * (1 - r ** kk) / (1 - r))
        p[ramp:] = [p_end] * (n - ramp)
        rec.update(mode="minterpolate", ramp="speed 100%% decaying x%.3f per frame f261-f271, freeze f272-f276" % r,
                   speeds_pct=[round(100 * r ** k, 1) for k in range(ramp)] + [0] * (n - ramp),
                   contact_src_frame=pc)
    else:
        speed = (s["src_out"] - s["src_in"]) / (n / MFPS)
        p = [p_in + k * speed * (1 / T) / MFPS for k in range(n)]
        rec.update(mode="frame-pick (nearest source frame)", speed=round(speed, 4))
    if rec["mode"] == "minterpolate":
        rec["src_pos"] = [round(round(x * Q) / Q, 4) for x in p]
        rec["src_frames_used"] = [math.floor(min(rec["src_pos"])), math.ceil(max(rec["src_pos"]))]
    else:
        rec["src_pos"] = [int(math.floor(x + 0.5)) for x in p]
        rec["src_frames_used"] = [min(rec["src_pos"]), max(rec["src_pos"])]
    a, b = rec["src_frames_used"]
    assert lo <= a and b <= hi, (sid, a, b, lo, hi)
    assert len(rec["src_pos"]) == n
    rec["inside_one_trailer_shot"] = True
    out["plates"].append(rec)
json.dump(out, open(sys.argv[1], "w"), indent=1)
for r in out["plates"]:
    print(r["id"], r["frames"], r["lib_shot"], r["lib_frames"], r["src_frames_used"], r.get("speed", ""), r["src_pos"][:3], "...", r["src_pos"][-2:])
