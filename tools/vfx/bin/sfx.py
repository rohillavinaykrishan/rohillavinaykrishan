"""Sound-design department: synthesize transition sound effects (no library or
credits needed) and place them on a timeline under the song.

  vfx-python sfx.py make whoosh whoosh.wav --dur 0.8
  vfx-python sfx.py make all sfx_kit/                      # every effect, 48 kHz stereo WAV
  vfx-python sfx.py place song.wav cues.json out.wav        # mix effects at given times

cues.json: [{"t": 12.0, "sfx": "riser", "dur": 2.0, "gain": -6, "end_at_t": true}, ...]
"end_at_t" makes the effect END at t (risers, reverse swells that land on a cut).
Effects: whoosh, riser, downlifter, impact, boom, reverse, glitch, shimmer, tape-stop, swipe
"""
import argparse
import json
import wave
from pathlib import Path

import numpy as np

SR = 48000
RNG = np.random.default_rng(7)


def _t(d):
    return np.arange(int(SR * d)) / SR


def _env(n, attack, release):
    e = np.ones(n)
    a, r = int(attack * SR), int(release * SR)
    if a:
        e[:a] = np.linspace(0, 1, a) ** 2
    if r:
        e[-r:] *= np.linspace(1, 0, r) ** 2
    return e


def _bandpass_sweep(noise, f0, f1, q=2.5):
    """Resonant band-pass (Chamberlin state-variable filter) whose centre glides from
    f0 to f1 - the audible "swoosh" of whooshes and risers."""
    out = np.empty_like(noise)
    low = band = 0.0
    damp = 1.0 / q
    for i, (x, fc) in enumerate(zip(noise, np.geomspace(f0, min(f1, 8000), len(noise)))):
        f = 2 * np.sin(np.pi * fc / SR)
        low += f * band
        high = x - low - damp * band
        band += f * high
        out[i] = band
    return out


def whoosh(d=0.8):
    n = int(SR * d)
    x = _bandpass_sweep(RNG.standard_normal(n), 250, 5000)
    x = x + _bandpass_sweep(RNG.standard_normal(n), 400, 4000, q=1.2)[::-1] * 0.25
    return x * np.sin(np.linspace(0, np.pi, n)) ** 1.5


def riser(d=2.0):
    t = _t(d)
    noise = _bandpass_sweep(RNG.standard_normal(len(t)), 200, 9000)
    tone = np.sin(2 * np.pi * np.cumsum(np.geomspace(110, 880, len(t))) / SR)
    return (noise * 0.8 + tone * 0.25) * np.linspace(0, 1, len(t)) ** 2.5


def downlifter(d=1.5):
    return riser(d)[::-1]


def impact(d=1.2):
    t = _t(d)
    body = np.sin(2 * np.pi * (45 + 80 * np.exp(-t * 18)) * t) * np.exp(-t * 4)
    crack = RNG.standard_normal(len(t)) * np.exp(-t * 35)
    return body * 1.0 + crack * 0.5


def boom(d=2.0):
    t = _t(d)
    return np.sin(2 * np.pi * (32 + 60 * np.exp(-t * 10)) * t) * np.exp(-t * 2.2)


def reverse(d=1.2):
    t = _t(d)
    cym = _bandpass_sweep(RNG.standard_normal(len(t)), 7000, 4000, q=0.8) * np.exp(-t * 3)
    return cym[::-1]


def glitch(d=0.5):
    n = int(SR * d)
    x = np.zeros(n)
    i = 0
    while i < n:
        seg = int(RNG.integers(200, 2400))
        kind = RNG.integers(0, 3)
        tt = np.arange(min(seg, n - i)) / SR
        if kind == 0:
            x[i:i + len(tt)] = np.sign(np.sin(2 * np.pi * RNG.integers(80, 2000) * tt))
        elif kind == 1:
            x[i:i + len(tt)] = RNG.standard_normal(len(tt)) * 0.6
        i += seg
    return np.round(x * 6) / 6 * _env(n, 0.002, 0.05)


def shimmer(d=1.5):
    t = _t(d)
    x = sum(np.sin(2 * np.pi * f * t + RNG.random() * 6) for f in (1760, 2217, 2637, 3520, 4435))
    return x / 5 * np.exp(-t * 2.5) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t))


def tape_stop(d=0.7):
    t = _t(d)
    f = 220 * (1 - t / d) ** 2
    return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 * (1 - t / d)


def swipe(d=0.35):
    n = int(SR * d)
    return _bandpass_sweep(RNG.standard_normal(n), 2000, 12000) * np.sin(np.linspace(0, np.pi, n))


EFFECTS = {"whoosh": whoosh, "riser": riser, "downlifter": downlifter, "impact": impact, "boom": boom,
           "reverse": reverse, "glitch": glitch, "shimmer": shimmer, "tape-stop": tape_stop, "swipe": swipe}


def make(name, dur=None):
    x = EFFECTS[name](dur) if dur else EFFECTS[name]()
    x = x / (np.abs(x).max() + 1e-9) * 0.89
    # gentle stereo width: tiny delay on the right channel
    right = np.concatenate([np.zeros(int(SR * 0.004)), x])[:len(x)]
    return np.stack([x, right * 0.97 + x * 0.03], axis=1)


def write_wav(path, stereo):
    pcm = (np.clip(stereo, -1, 1) * 32767).astype(np.int16)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def read_wav_any(path):
    import subprocess
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make")
    m.add_argument("name", choices=list(EFFECTS) + ["all"])
    m.add_argument("out")
    m.add_argument("--dur", type=float)
    p = sub.add_parser("place")
    p.add_argument("song")
    p.add_argument("cues")
    p.add_argument("out")
    args = ap.parse_args()

    if args.cmd == "make":
        names = list(EFFECTS) if args.name == "all" else [args.name]
        for n in names:
            dst = Path(args.out) / f"{n}.wav" if args.name == "all" else Path(args.out)
            write_wav(dst, make(n, args.dur))
            print(f"wrote {dst}")
        return

    song = read_wav_any(args.song)
    mix = song.copy()
    for c in json.loads(Path(args.cues).read_text()):
        fx = make(c["sfx"], c.get("dur")) * 10 ** (c.get("gain", -8) / 20)
        start = int((c["t"] - (len(fx) / SR if c.get("end_at_t") else 0)) * SR)
        a, b = max(start, 0), min(start + len(fx), len(mix))
        if b > a:
            mix[a:b] += fx[a - start:b - start]
    peak = np.abs(mix).max()
    if peak > 0.98:
        mix *= 0.98 / peak
    write_wav(args.out, mix)
    print(f"wrote {args.out} ({len(json.loads(Path(args.cues).read_text()))} cues)")


if __name__ == "__main__":
    main()
