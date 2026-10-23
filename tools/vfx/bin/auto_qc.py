#!/usr/bin/env python3
"""Automatic delivery QC for a finished master (team lead / delivery department).

usage:
  vfx-python tools/vfx/bin/auto_qc.py <video.mp4> [--expect-frames N] [--fps 25] [--size 2160x3840]
        [--names "VINAY KRISHAN ROHILLA" ...] [--out report.md] [--lufs -14] [--lufs-tol 0.5]
        [--tp-max -1.0] [--rb-tol 0] [--no-words] [--language en] [--no-whisper] [--threads 2]

Checks (one ffprobe pass, one audio pass, one downscaled decode pass, one Whisper pass):
  1. specs     ffprobe: size, r/avg fps = --fps, CFR (every video pts delta = 1/fps), frame count
               (packets; = --expect-frames if given), duration, video+audio start_time 0, A/V duration
               within 1 frame, codec/pix_fmt/BT.709 tags (tags = WARN only).
  2. loudness  ebur128 peak=true: integrated within --lufs +/- --lufs-tol, true peak <= --tp-max.
  3. black     frames where >= 98% of pixels have luma < 0.10 (blackdetect-like)  -> FAIL, spans listed.
     frozen    frames whose mean abs diff to the previous frame < 0.20/255 at 360 px -> WARN, spans listed
               (intentional holds exist; the reviewer decides).
  4. blue cast per-frame mean R >= mean B - --rb-tol (0..255 scale) -> FAIL, worst frames listed.
  5. whisper   faster-whisper small, int8, vad_filter=False, temperature 0, word timestamps; every
               segment with times; known hallucinations ("Thanks for watching!", "Music", ...) flagged.
               INFO by default (sung lyrics can be fine); --no-words makes any real segment a FAIL.
  6. names     --names go into the report as a MANUAL spelling checklist (no OCR here) and are
               cross-checked against the transcript (a spoken name = WARN).
  7. sheet     <report>_sheet.png next to the report: 12 evenly spaced frames, labelled frame + time.

Output: markdown report (default ./<video-stem>_qc.md) + contact sheet. Exit 0 = pass, 1 = fail, 2 = usage.
Never writes next to the video unless --out points there (do not put reports in deliver/).

Tested 2026-10-23 on projects/sukanya-v2/deliver/Sukanya_Dilip_Dhariya_StreetFighter_SrMatchmove_v2_4K.mp4
(2160x3840, 25 fps, 450 frames, 18 s), with other jobs idle:
  vfx-python tools/vfx/bin/auto_qc.py projects/sukanya-v2/deliver/Sukanya_..._v2_4K.mp4 \
      --expect-frames 450 --names "SUKANYA DILIP DHARIYA" --out <scratch>/sukanya_v2_qc.md
  -> see RESULT block in tools/vfx/bin/auto_qc.README.md (written from the real run).
"""
import argparse, json, os, re, subprocess, sys, tempfile, time
import numpy as np

HALLUCINATIONS = [
    "thanks for watching", "thank you for watching", "thank you so much for watching", "thank you",
    "thanks", "music", "music playing", "upbeat music", "applause", "you", "bye", "subscribe",
    "please subscribe", "like and subscribe", "subtitles by the amara.org community", "amara.org",
    "transcribed by", "i'll see you in the next video", "see you next time", "silence", "foreign",
]


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def norm_text(t):
    t = t.lower().strip()
    t = re.sub(r"[\[\]\(\)♪♫*.!?,'\"-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def is_hallucination(text):
    n = norm_text(text)
    if not n:
        return True
    if n in HALLUCINATIONS:
        return True
    return any(n == h or (n.startswith(h) and len(n) <= len(h) + 4) for h in HALLUCINATIONS if len(h) > 6)


def spans(idx):
    """sorted frame indices -> list of (start, end) inclusive runs"""
    out = []
    for i in idx:
        if out and i == out[-1][1] + 1:
            out[-1][1] = i
        else:
            out.append([i, i])
    return [tuple(s) for s in out]


def fmt_spans(sp, fps, limit=20):
    s = ", ".join(f"f{a}-{b} ({a/fps:.2f}-{(b+1)/fps:.2f} s, {b-a+1} fr)" if b > a else f"f{a} ({a/fps:.2f} s)"
                  for a, b in sp[:limit])
    return s + (f" ... (+{len(sp)-limit} more)" if len(sp) > limit else "")


class Report:
    def __init__(self):
        self.rows, self.body = [], []

    def gate(self, name, status, detail):
        self.rows.append((name, status, detail))

    def add(self, text):
        self.body.append(text)

    @property
    def failed(self):
        return any(s == "FAIL" for _, s, _ in self.rows)


def probe(path, rep, a):
    pj = json.loads(run(["ffprobe", "-v", "error", "-count_packets", "-show_streams", "-show_format",
                         "-of", "json", path]).stdout or "{}")
    vs = [s for s in pj.get("streams", []) if s["codec_type"] == "video"]
    au = [s for s in pj.get("streams", []) if s["codec_type"] == "audio"]
    if not vs:
        rep.gate("specs", "FAIL", "no video stream")
        return None
    v = vs[0]
    W, H = int(v["width"]), int(v["height"])
    fails, warns, lines = [], [], []
    ew, eh = map(int, a.size.lower().split("x"))
    if (W, H) != (ew, eh):
        fails.append(f"size {W}x{H} != {ew}x{eh}")
    rfr, afr = v.get("r_frame_rate"), v.get("avg_frame_rate")
    fr = lambda s: (lambda n, d: n / d if d else 0)(*map(float, s.split("/")))
    if abs(fr(rfr) - a.fps) > 1e-3 or abs(fr(afr) - a.fps) > 1e-3:
        fails.append(f"fps r={rfr} avg={afr} != {a.fps}")
    nfr = int(v.get("nb_read_packets") or v.get("nb_frames") or 0)
    if a.expect_frames and nfr != a.expect_frames:
        fails.append(f"frames {nfr} != {a.expect_frames}")
    # CFR: pts deltas from packets (no decode)
    pts = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time",
               "-of", "csv=p=0", path]).stdout.split()
    pts = np.array(sorted(float(x) for x in pts if x not in ("", "N/A")))
    d = np.diff(pts) if len(pts) > 1 else np.array([1 / a.fps])
    bad = int(np.sum(np.abs(d - 1 / a.fps) > 0.5e-3))
    if bad:
        fails.append(f"VFR: {bad} pts deltas != {1000/a.fps:.1f} ms (min {d.min()*1000:.2f}, max {d.max()*1000:.2f})")
    vstart = float(v.get("start_time", 0) or 0)
    vdur = float(v.get("duration", 0) or 0)
    if abs(vstart) > 1e-3:
        fails.append(f"video start_time {vstart}")
    if a.expect_frames and abs(vdur - a.expect_frames / a.fps) > 0.5 / a.fps:
        fails.append(f"video duration {vdur:.3f} != {a.expect_frames / a.fps:.3f}")
    lines.append(f"| Video | {v.get('codec_name')} {v.get('profile','')}, {v.get('pix_fmt')}, "
                 f"{v.get('color_space','?')}/{v.get('color_transfer','?')}/{v.get('color_primaries','?')} "
                 f"{v.get('color_range','')} |")
    lines.append(f"| Size / fps | {W}x{H}, r {rfr}, avg {afr} |")
    lines.append(f"| Frames (packets) | {nfr}; pts deltas min {d.min()*1000:.2f} ms, max {d.max()*1000:.2f} ms |")
    lines.append(f"| Video start / duration | {vstart:.3f} s / {vdur:.3f} s |")
    if v.get("pix_fmt") != "yuv420p":
        warns.append(f"pix_fmt {v.get('pix_fmt')} (delivery = yuv420p)")
    if v.get("color_space") != "bt709" or v.get("color_primaries") != "bt709" or v.get("color_transfer") != "bt709":
        warns.append("BT.709 tags missing/incomplete")
    if not au:
        fails.append("no audio stream")
    else:
        s = au[0]
        astart, adur = float(s.get("start_time", 0) or 0), float(s.get("duration", 0) or 0)
        lines.append(f"| Audio | {s.get('codec_name')} {s.get('profile','')}, {s.get('sample_rate')} Hz, "
                     f"{s.get('channels')} ch, {int(s.get('bit_rate', 0) or 0)//1000} kb/s, start {astart:.3f} s, "
                     f"duration {adur:.3f} s |")
        if abs(astart) > 1e-3:
            fails.append(f"audio start_time {astart}")
        if abs(adur - vdur) > 1 / a.fps + 0.025:  # 1 frame + one AAC frame
            fails.append(f"A/V duration differ: audio {adur:.3f} vs video {vdur:.3f}")
        if s.get("sample_rate") != "48000":
            warns.append(f"audio {s.get('sample_rate')} Hz (delivery = 48 kHz)")
    lines.append(f"| File | {int(pj['format'].get('size', 0))/1e6:.1f} MB, {float(pj['format'].get('bit_rate', 0))/1e6:.1f} Mb/s |")
    rep.add("## 1. Specs (ffprobe)\n\n| | |\n|---|---|\n" + "\n".join(lines))
    st = "FAIL" if fails else ("WARN" if warns else "PASS")
    rep.gate("specs", st, "; ".join(fails + warns) or f"{W}x{H} {a.fps:g} fps CFR, {nfr} fr, {vdur:.3f} s, starts 0")
    return {"W": W, "H": H, "frames": nfr, "dur": vdur, "has_audio": bool(au)}


def loudness(path, rep, a):
    err = run(["ffmpeg", "-hide_banner", "-nostats", "-threads", str(a.threads), "-i", path, "-vn",
               "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
    summ = err[err.rfind("Summary:"):]
    g = lambda k: (lambda m: float(m.group(1)) if m else None)(re.search(k + r":\s+(-?[\d.]+|-inf)", summ))
    I, LRA, TP = g(r"\bI"), g("LRA"), g("Peak")
    if I is None:
        rep.gate("loudness", "FAIL", "ebur128 gave no summary (no audio?)")
        return
    ok = abs(I - a.lufs) <= a.lufs_tol and TP is not None and TP <= a.tp_max
    rep.add(f"## 2. Loudness (ebur128, true peak)\n\nIntegrated **{I:.1f} LUFS** (target {a.lufs:g} +/- {a.lufs_tol:g}), "
            f"LRA {LRA:.1f} LU, true peak **{TP:.1f} dBTP** (max {a.tp_max:g}).")
    rep.gate("loudness", "PASS" if ok else "FAIL", f"I {I:.1f} LUFS, TP {TP:.1f} dBTP, LRA {LRA:.1f} LU")


def frames_pass(path, info, rep, a, sheet_path):
    W, H = info["W"], info["H"]
    long_side = 640
    if H >= W:
        h = long_side; w = int(round(W * h / H / 2)) * 2
    else:
        w = long_side; h = int(round(H * w / W / 2)) * 2
    n_exp = info["frames"]
    picks = set(np.linspace(0, max(n_exp - 1, 0), 12).round().astype(int).tolist())
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-threads", str(a.threads), "-i", path, "-map", "0:v:0",
                          "-vf", f"scale={w}:{h}:flags=area,format=rgb24", "-f", "rawvideo", "-"],
                         stdout=subprocess.PIPE)
    fsz = w * h * 3
    means, black, mad, tiles = [], [], [], {}
    prev = None
    i = 0
    while True:
        buf = p.stdout.read(fsz)
        if len(buf) < fsz:
            break
        f = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        ff = f.astype(np.float32)
        means.append(ff.reshape(-1, 3).mean(0))
        luma = ff[..., 0] * 0.2126 + ff[..., 1] * 0.7152 + ff[..., 2] * 0.0722
        black.append(float((luma < a.black_pix * 255).mean()))
        mad.append(float(np.abs(ff - prev).mean()) if prev is not None else 999.0)
        prev = ff
        if i in picks:
            tiles[i] = f.copy()
        i += 1
    p.wait()
    n = i
    means = np.array(means) if means else np.zeros((0, 3))
    fps = a.fps
    # black
    bidx = [k for k, b in enumerate(black) if b >= 0.98]
    bsp = spans(bidx)
    sec3 = ("## 3. Black / frozen frames\n\n"
            f"Decoded {n} frames at {w}x{h}. Darkest frame: f{int(np.argmin(means.mean(1))) if n else 0} "
            f"(mean {means.mean(1).min() if n else 0:.1f}/255).\n\n"
            f"- Black (>=98% of pixels with luma < {a.black_pix:g}, like blackdetect pix_th): {fmt_spans(bsp, fps) if bsp else 'none'}")
    rep.gate("black frames", "FAIL" if bsp else "PASS", fmt_spans(bsp, fps, 5) if bsp else "none")
    def holds(th):
        sp = spans([k for k, m in enumerate(mad) if m < th])
        merged = []  # merge runs split by <= 2 frames; a repeat run from k means frames k-1..end hold
        for s0, e0 in sp:
            if merged and s0 - merged[-1][1] <= 3:
                merged[-1][1] = e0
            else:
                merged.append([s0 - 1, e0])
        return [tuple(x) for x in merged]
    fsp_hold = holds(a.freeze_th)
    still = [sp for sp in holds(a.still_th) if not any(f0 <= sp[0] and sp[1] <= f1 for f0, f1 in fsp_hold)]
    md = np.array(mad[1:]) if n > 1 else np.array([0.0])
    sec3 += (f"\n- Frozen (frame ~= previous, mean abs diff < {a.freeze_th}/255 at {w}x{h}): "
             f"{fmt_spans(fsp_hold, fps) if fsp_hold else 'none'}\n"
             f"- Near-still (diff < {a.still_th}/255; slow end cards, embers, grain): "
             f"{fmt_spans(still, fps) if still else 'none'}\n"
             f"- Smallest consecutive-frame change: {md.min():.3f}/255 at f{int(np.argmin(md))+1}; "
             f"median {np.median(md):.2f}/255.")
    rep.add(sec3)
    rep.gate("frozen frames", "WARN" if fsp_hold else "PASS",
             (fmt_spans(fsp_hold, fps, 5) + " (check they are intended holds)") if fsp_hold else "none")
    if still:
        rep.gate("near-still spans", "INFO", fmt_spans(still, fps, 4))
    if a.expect_frames and n != a.expect_frames:
        rep.gate("decoded frames", "FAIL", f"decoded {n} != {a.expect_frames}")
    # blue cast
    if n:
        rb = means[:, 0] - means[:, 2]
        bad = np.where(rb < -a.rb_tol)[0]
        worst = np.argsort(rb)[:5]
        wl = ", ".join(f"f{k} R-B {rb[k]:+.1f} (R {means[k,0]:.0f} G {means[k,1]:.0f} B {means[k,2]:.0f})" for k in worst)
        rep.add(f"## 4. Blue cast (per-frame mean R >= B - {a.rb_tol:g})\n\n"
                f"Whole clip mean R {means[:,0].mean():.1f}, G {means[:,1].mean():.1f}, B {means[:,2].mean():.1f}. "
                f"Frames with B > R: **{len(bad)}** of {n}"
                + (f" ({fmt_spans(spans(bad.tolist()), fps, 10)})" if len(bad) else "")
                + f".\n\nWorst 5 frames: {wl}.")
        rep.gate("R >= B (no blue cast)", "FAIL" if len(bad) else "PASS",
                 f"{len(bad)} frames with B > R; worst f{worst[0]} R-B {rb[worst[0]]:+.1f}")
    # sheet
    try:
        from PIL import Image, ImageDraw, ImageFont
        ks = sorted(tiles)
        cols = 6 if H >= W else 4
        rows = (len(ks) + cols - 1) // cols
        lab = 28
        sheet = Image.new("RGB", (cols * w, rows * (h + lab)), (24, 24, 24))
        dr = ImageDraw.Draw(sheet)
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 18)
        except OSError:
            font = ImageFont.load_default()
        for j, k in enumerate(ks):
            x, y = (j % cols) * w, (j // cols) * (h + lab)
            sheet.paste(Image.fromarray(tiles[k]), (x, y + lab))
            dr.text((x + 6, y + 4), f"f{k}  {k / fps:.2f}s", fill=(255, 220, 120), font=font)
        sheet.save(sheet_path)
        rep.add(f"## 7. Contact sheet\n\n`{sheet_path}` ({len(ks)} frames at {w}x{h}).")
        rep.gate("contact sheet", "INFO", os.path.basename(sheet_path))
    except Exception as e:  # sheet is a convenience, never a gate
        rep.gate("contact sheet", "WARN", f"failed: {e}")


def whisper(path, rep, a):
    t0 = time.time()
    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, "a.wav")
        run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vn", "-ac", "1", "-ar", "16000", wav])
        if not os.path.exists(wav):
            rep.gate("whisper", "WARN", "no audio extracted")
            return
        from faster_whisper import WhisperModel
        m = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=a.threads)
        segs, info = m.transcribe(wav, vad_filter=False, word_timestamps=True, beam_size=5, temperature=0.0,
                                  condition_on_previous_text=False, no_speech_threshold=0.6,
                                  language=a.language)
        segs = list(segs)
    real, lines = [], []
    for s in segs:
        hall = is_hallucination(s.text)
        if not hall:
            real.append(s)
        lines.append(f"| {s.start:6.2f} | {s.end:6.2f} | {s.text.strip()} | {s.no_speech_prob:.2f} | "
                     f"{s.avg_logprob:.2f} | {'hallucination (known phrase)' if hall else '**words**'} |")
    rep.add(f"## 5. Whisper (faster-whisper small, vad_filter=False)\n\nLanguage {info.language} "
            f"(p {info.language_probability:.2f}); {len(segs)} segments, {len(real)} not on the hallucination list; "
            f"{time.time()-t0:.0f} s.\n\n| start | end | text | no_speech | avg_logprob | flag |\n|---|---|---|---|---|---|\n"
            + ("\n".join(lines) if lines else "| | | (no segments) | | | |"))
    if not real:
        rep.gate("whisper (VAD off)", "PASS", f"{len(segs)} segments, all known hallucinations" if segs else "no words")
    else:
        txt = "; ".join(f"{s.start:.1f}-{s.end:.1f} \"{s.text.strip()[:40]}\"" for s in real[:4])
        rep.gate("whisper (VAD off)", "FAIL" if a.no_words else "INFO",
                 f"{len(real)} word segments: {txt}" + ("" if a.no_words else " (lyrics? listen; --no-words to gate)"))
    return " ".join(norm_text(s.text) for s in segs)


def names_check(rep, a, transcript):
    if not a.names:
        return
    lines = []
    for nm in a.names:
        toks = [t for t in norm_text(nm).split() if len(t) > 2]
        heard = [t for t in toks if transcript and re.search(r"\b" + re.escape(t) + r"\b", transcript)]
        lines.append(f"- [ ] `{nm}`: read it at 100% on the 4K frames (spelling, every occurrence)."
                     + (f" Whisper heard: {', '.join(heard)} (spoken name?)" if heard else ""))
        if heard:
            rep.gate(f"name in audio: {nm}", "WARN", f"transcript contains {', '.join(heard)}")
    rep.add("## 6. Names (MANUAL spelling check; no OCR in this toolset)\n\n" + "\n".join(lines))
    rep.gate("names", "MANUAL", f"{len(a.names)} name(s) to read at 100%")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--expect-frames", type=int)
    ap.add_argument("--fps", type=float, default=25)
    ap.add_argument("--size", default="2160x3840")
    ap.add_argument("--names", nargs="*", default=[])
    ap.add_argument("--out")
    ap.add_argument("--lufs", type=float, default=-14.0)
    ap.add_argument("--lufs-tol", type=float, default=0.5)
    ap.add_argument("--tp-max", type=float, default=-1.0)
    ap.add_argument("--rb-tol", type=float, default=0.0, help="allowed B-R excess per frame (0..255)")
    ap.add_argument("--freeze-th", type=float, default=0.05, help="mean abs diff /255 (360 px) under which a frame = previous (WARN)")
    ap.add_argument("--black-pix", type=float, default=0.05, help="pixel luma threshold 0..1 for black (blackdetect pix_th)")
    ap.add_argument("--still-th", type=float, default=0.20, help="near-still threshold /255 (INFO only)")
    ap.add_argument("--no-words", action="store_true", help="any non-hallucination Whisper segment = FAIL")
    ap.add_argument("--language", default=None, help="force Whisper language (default auto)")
    ap.add_argument("--no-whisper", action="store_true")
    ap.add_argument("--threads", type=int, default=2, help="decoder/whisper threads (shared machine: keep 2)")
    a = ap.parse_args()
    if not os.path.isfile(a.video):
        ap.error(f"no such file: {a.video}")
    stem = os.path.splitext(os.path.basename(a.video))[0]
    out = os.path.abspath(a.out or f"{stem}_qc.md")
    if os.path.abspath(out) == os.path.abspath(a.video):
        ap.error("--out would overwrite the video")
    sheet = os.path.splitext(out)[0] + "_sheet.png"
    t0 = time.time()
    rep = Report()
    info = probe(a.video, rep, a)
    if info:
        loudness(a.video, rep, a) if info["has_audio"] else rep.gate("loudness", "FAIL", "no audio")
        frames_pass(a.video, info, rep, a, sheet)
        transcript = None
        if not a.no_whisper and info["has_audio"]:
            transcript = whisper(a.video, rep, a)
        names_check(rep, a, transcript)
    verdict = "FAIL" if rep.failed else "PASS"
    order = {"FAIL": 0, "WARN": 1, "MANUAL": 2, "INFO": 3, "PASS": 4}
    head = (f"# Auto QC: {os.path.basename(a.video)}\n\nFile: `{os.path.abspath(a.video)}`  \n"
            f"Run: {time.strftime('%Y-%m-%d %H:%M', time.localtime())} (container time), {time.time()-t0:.0f} s, "
            f"`auto_qc.py` (expect {a.size} @ {a.fps:g} fps"
            + (f", {a.expect_frames} frames" if a.expect_frames else "") + ")\n\n"
            f"# VERDICT: {verdict}\n\n| Gate | Result | Detail |\n|---|---|---|\n"
            + "\n".join(f"| {g} | {'**'+s+'**' if s in ('FAIL','WARN') else s} | {d} |"
                        for g, s, d in sorted(rep.rows, key=lambda r: order.get(r[1], 9))))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as fh:
        fh.write(head + "\n\n" + "\n\n".join(sorted(rep.body, key=lambda b: b[:6])) + "\n")
    print(head.split("\n\n", 2)[2])
    print(f"\nreport: {out}\nsheet:  {sheet}")
    sys.exit(1 if rep.failed else 0)


if __name__ == "__main__":
    main()
