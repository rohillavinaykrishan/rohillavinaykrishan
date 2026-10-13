#!/usr/bin/env python3
"""Fast song analysis for lyric/music videos: tempo, beats, energy curve,
loudness peaks, sections, key tendency and vocal onsets, written as JSON.

Everything is computed per frame (hop 512 at 22.05 kHz), never with
sample-level convolution, so a 4-minute song takes seconds, not minutes.

  python tools/analyze_audio.py song.mp3 -o analysis.json
"""
import argparse
import json
import sys

import librosa
import numpy as np

SR = 22050
HOP = 512
KEYS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


def key_estimate(chroma):
    profile = chroma.mean(axis=1)
    best = max(
        ((np.corrcoef(profile, np.roll(tmpl, i))[0, 1], f"{KEYS[i]} {mode}")
         for mode, tmpl in (("major", MAJOR), ("minor", MINOR)) for i in range(12)),
    )
    return best[1]


def sections(chroma, mfcc, duration, n):
    feats = np.vstack([librosa.util.normalize(chroma, axis=1), librosa.util.normalize(mfcc, axis=1)])
    n = max(2, min(n, int(duration // 15) or 2))
    bounds = librosa.segment.agglomerative(feats, n)
    times = list(librosa.frames_to_time(bounds, sr=SR, hop_length=HOP)) + [duration]
    return [{"start": round(float(a), 2), "end": round(float(b), 2)} for a, b in zip(times, times[1:]) if b - a > 1]


def analyze(path, n_sections):
    y, _ = librosa.load(path, sr=SR, mono=True)
    duration = len(y) / SR

    tempo, beats = librosa.beat.beat_track(y=y, sr=SR, hop_length=HOP)
    beat_times = librosa.frames_to_time(beats, sr=SR, hop_length=HOP)

    rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
    rms_t = librosa.frames_to_time(np.arange(len(rms)), sr=SR, hop_length=HOP)
    # Energy curve resampled to 10 values per second, normalized 0-1.
    grid = np.arange(0, duration, 0.1)
    energy = np.interp(grid, rms_t, rms)
    energy = energy / (energy.max() or 1)
    peaks = librosa.util.peak_pick(energy, pre_max=20, post_max=20, pre_avg=30, post_avg=30, delta=0.15, wait=30)

    # Vocal-ish onsets: onset strength on the harmonic part, mid frequencies.
    harm = librosa.effects.harmonic(y, margin=3)
    onset_env = librosa.onset.onset_strength(y=harm, sr=SR, hop_length=HOP, fmin=200, fmax=4000)
    onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=SR, hop_length=HOP, units="time", backtrack=True)

    chroma = librosa.feature.chroma_cqt(y=harm, sr=SR, hop_length=HOP)
    mfcc = librosa.feature.mfcc(y=y, sr=SR, hop_length=HOP, n_mfcc=13)

    r = lambda xs: [round(float(x), 3) for x in xs]
    return {
        "file": path,
        "duration": round(duration, 3),
        "tempo_bpm": round(float(np.atleast_1d(tempo)[0]), 1),
        "beats": r(beat_times),
        "downbeats": r(beat_times[::4]),
        "energy_10hz": r(energy),
        "loudness_peaks": r(grid[peaks]),
        "sections": sections(chroma, mfcc, duration, n_sections),
        "key": key_estimate(chroma),
        "vocal_onsets": r(onsets),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("audio")
    p.add_argument("-o", "--output", help="JSON path (default: stdout)")
    p.add_argument("--sections", type=int, default=8, help="max number of sections")
    args = p.parse_args()
    result = analyze(args.audio, args.sections)
    text = json.dumps(result, ensure_ascii=False)
    if args.output:
        open(args.output, "w").write(text)
        print(f"{args.output}: {result['duration']}s, {result['tempo_bpm']} BPM, {result['key']}, "
              f"{len(result['sections'])} sections, {len(result['vocal_onsets'])} onsets", file=sys.stderr)
    else:
        print(text)


if __name__ == "__main__":
    main()
