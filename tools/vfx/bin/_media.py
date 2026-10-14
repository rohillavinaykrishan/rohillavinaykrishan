"""Shared image/video helpers for the VFX Studio scripts."""
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}


def is_video(path):
    return Path(path).suffix.lower() in VIDEO_EXTS


def probe_fps(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=r_frame_rate", "-of", "json", str(path)],
        capture_output=True, text=True, check=True).stdout
    num, den = json.loads(out)["streams"][0]["r_frame_rate"].split("/")
    return float(num) / float(den)


def read_frames(path):
    """Yields RGB uint8 frames from a video or a single image."""
    if not is_video(path):
        img = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if img is None:
            raise SystemExit(f"cannot read {path}")
        yield cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return
    cap = cv2.VideoCapture(str(path))
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        yield cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    cap.release()


def write_image(path, rgb_or_rgba):
    arr = np.asarray(rgb_or_rgba)
    code = cv2.COLOR_RGBA2BGRA if arr.shape[-1] == 4 else cv2.COLOR_RGB2BGR
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), cv2.cvtColor(arr, code))


class VideoWriter:
    """Pipes RGB/RGBA frames into ffmpeg. Codec follows the output extension:
    .mov -> ProRes 4444 with alpha, .webm -> VP9 with alpha, else H.264."""

    def __init__(self, path, fps, audio_from=None):
        self.path, self.fps, self.audio_from = Path(path), fps, audio_from
        self.proc = None

    def write(self, frame):
        frame = np.ascontiguousarray(frame, dtype=np.uint8)
        if self.proc is None:
            h, w, c = frame.shape
            pix_in = "rgba" if c == 4 else "rgb24"
            ext = self.path.suffix.lower()
            if ext == ".mov":
                codec = ["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le"]
            elif ext == ".webm":
                codec = ["-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p" if c == 4 else "yuv420p", "-b:v", "0", "-crf", "30"]
            else:
                codec = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2"]
            cmd = ["ffmpeg", "-y", "-loglevel", "error",
                   "-f", "rawvideo", "-pix_fmt", pix_in, "-s", f"{w}x{h}", "-r", str(self.fps), "-i", "-"]
            if self.audio_from:
                cmd += ["-i", str(self.audio_from), "-map", "0:v", "-map", "1:a?", "-c:a", "aac", "-shortest"]
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.proc = subprocess.Popen(cmd + codec + [str(self.path)], stdin=subprocess.PIPE)
        self.proc.stdin.write(frame.tobytes())

    def close(self):
        if self.proc:
            self.proc.stdin.close()
            self.proc.wait()
