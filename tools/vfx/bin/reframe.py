"""Shorts/Reels reframe: turn a 16:9 video into 9:16 (or any aspect) with a
crop window that follows the main subject instead of the fixed centre.

The subject is found with rembg on every Nth frame, its centre is smoothed so
the virtual camera glides instead of jittering, then ffmpeg crops and scales.

  vfx-python reframe.py music_video.mp4 short.mp4 --start 62.5 --duration 45
  vfx-python reframe.py in.mp4 out.mp4 --size 2160x3840 --model u2net_human_seg
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np
from rembg import new_session, remove


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                          "-show_entries", "stream=width,height,r_frame_rate", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return s["width"], s["height"], float(num) / float(den)


def subject_track(path, start, duration, step_s, model):
    """Returns [(t, x_centre_px)] sampled every step_s seconds (None = no subject)."""
    session = new_session(model)
    cap = cv2.VideoCapture(str(path))
    track, t = [], 0.0
    while t <= duration:
        cap.set(cv2.CAP_PROP_POS_MSEC, (start + t) * 1000)
        ok, frame = cap.read()
        if not ok:
            break
        small = cv2.resize(frame, (480, int(480 * frame.shape[0] / frame.shape[1])))
        mask = np.asarray(remove(cv2.cvtColor(small, cv2.COLOR_BGR2RGB), session=session, only_mask=True), np.float32)
        weight = mask.sum()
        x = (mask.sum(axis=0) * np.arange(mask.shape[1])).sum() / weight * frame.shape[1] / 480 if weight > 500 else None
        track.append((t, x))
        t += step_s
    cap.release()
    return track


def smooth(track, width, crop_w, strength):
    xs = np.array([x if x is not None else np.nan for _, x in track], dtype=float)
    if np.all(np.isnan(xs)):
        xs[:] = width / 2
    idx = np.arange(len(xs))
    xs = np.interp(idx, idx[~np.isnan(xs)], xs[~np.isnan(xs)])  # fill gaps
    k = max(1, strength)
    xs = np.convolve(np.pad(xs, k, mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), mode="valid")
    return np.clip(xs - crop_w / 2, 0, width - crop_w)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--start", type=float, default=0.0, help="seconds")
    ap.add_argument("--duration", type=float, default=None, help="seconds (default: to the end)")
    ap.add_argument("--size", default="2160x3840", help="output WxH (default 4K vertical)")
    ap.add_argument("--model", default="u2net_human_seg", help="rembg model; isnet-general-use for objects")
    ap.add_argument("--step", type=float, default=0.25, help="seconds between subject samples")
    ap.add_argument("--smooth", type=int, default=6, help="smoothing radius in samples (higher = calmer camera)")
    args = ap.parse_args()

    w, h, fps = probe(args.input)
    if args.duration is None:
        total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                      args.input], capture_output=True, text=True, check=True).stdout)
        args.duration = total - args.start
    ow, oh = map(int, args.size.split("x"))
    crop_w = min(w, int(round(h * ow / oh / 2)) * 2)
    crop_h = h if crop_w < w else int(round(w * oh / ow / 2)) * 2

    track = subject_track(args.input, args.start, args.duration, args.step, args.model)
    lefts = smooth(track, w, crop_w, args.smooth)
    times = [t for t, _ in track]
    found = sum(x is not None for _, x in track)

    # Interpolate the crop position for every frame so the move is smooth, and
    # feed it to ffmpeg's crop filter with sendcmd.
    frame_t = np.arange(0, args.duration, 1 / fps)
    frame_x = np.interp(frame_t, times, lefts)
    with tempfile.TemporaryDirectory() as tmp:
        cmds = Path(tmp) / "crop.cmd"
        cmds.write_text("".join(f"{t:.4f} crop x {int(round(x))};\n" for t, x in zip(frame_t, frame_x)))
        vf = (f"sendcmd=f='{cmds}',crop=w={crop_w}:h={crop_h}:x={int(lefts[0])}:y={(h - crop_h) // 2},"
              f"scale={ow}:{oh}:flags=lanczos,unsharp=5:5:0.35,format=yuv420p")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(args.start), "-t", str(args.duration),
                        "-i", args.input, "-vf", vf, "-c:v", "libx264", "-crf", "16", "-preset", "slow",
                        "-profile:v", "high", "-level", "5.2", "-movflags", "+faststart",
                        "-c:a", "aac", "-b:a", "320k", args.output], check=True)
    print(f"wrote {args.output} ({ow}x{oh}, {args.duration:.1f}s, subject found in {found}/{len(track)} samples)")


if __name__ == "__main__":
    main()
