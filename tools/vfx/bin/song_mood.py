"""Audio department: measure how a song FEELS, to drive the look and the grade.

Outputs tempo, beats, key + major/minor, energy and brightness per section, and
a starting suggestion for the colour-grade family. The director and colorist
combine it with the lyrics' meaning (which they read themselves) before deciding.

  vfx-python song_mood.py song.wav mood.json
"""
import argparse
import json

import librosa
import numpy as np

KEYS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
# Krumhansl-Schmuckler key profiles
MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


def detect_key(chroma):
    prof = chroma.mean(axis=1)
    best = max(((np.corrcoef(np.roll(p, k), prof)[0, 1], KEYS[k], mode)
                for p, mode in ((MAJOR, "major"), (MINOR, "minor")) for k in range(12)))
    return best[1], best[2], round(float(best[0]), 2)


def sections(y, sr, n=6):
    """Rough structure: split at the biggest novelty points of a beat-synced feature matrix."""
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    bounds = librosa.segment.agglomerative(mfcc, n)
    times = librosa.frames_to_time(bounds, sr=sr).tolist() + [len(y) / sr]
    rms = librosa.feature.rms(y=y)[0]
    rt = librosa.frames_to_time(np.arange(len(rms)), sr=sr)
    out = []
    for a, b in zip(times[:-1], times[1:]):
        m = (rt >= a) & (rt < b)
        out.append({"start": round(a, 2), "end": round(b, 2), "energy": float(rms[m].mean()) if m.any() else 0.0})
    peak = max(s["energy"] for s in out) or 1
    for s in out:
        s["energy"] = round(s["energy"] / peak, 2)
        s["label_hint"] = "high (chorus/drop?)" if s["energy"] > 0.8 else "mid (verse?)" if s["energy"] > 0.5 else "low (intro/bridge/outro?)"
    return out


def suggest(bpm, mode, energy, brightness):
    """Grade family from the music alone - a starting point, not the decision."""
    fast, bright, loud = bpm >= 110, brightness > 2600, energy > 0.12
    if mode == "major" and fast and loud:
        return ["punjabi-gold", "blockbuster", "bollywood"], "upbeat, celebratory: warm saturated skin, punchy contrast"
    if mode == "major" and not fast:
        return ["punjabi-romance", "romantic", "golden-hour"], "warm and tender: soft golden light, lifted blacks"
    if mode == "minor" and fast and loud:
        return ["punjabi-night", "punjabi-dark", "night-neon"], "intense, swagger: deep teal shadows, hot highlights, crushed blacks"
    if mode == "minor" and not bright:
        return ["moody", "punjabi-dark", "noir"], "sad or heavy: desaturated, cool shadows, low key"
    return ["cinematic", "punjabi-desi", "golden-hour"], "storytelling: natural earthy tones with a film curve"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    args = ap.parse_args()

    y, sr = librosa.load(args.input, sr=22050, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    bpm = float(np.atleast_1d(tempo)[0])
    while 0 < bpm < 60:  # drumless/ballad tracks often read at half or quarter tempo
        bpm *= 2
    key, mode, conf = detect_key(librosa.feature.chroma_cqt(y=y, sr=sr))
    energy = float(librosa.feature.rms(y=y)[0].mean())
    brightness = float(librosa.feature.spectral_centroid(y=y, sr=sr)[0].mean())
    looks, why = suggest(bpm, mode, energy, brightness)
    result = {
        "duration": round(len(y) / sr, 2), "bpm": round(bpm, 1),
        "beats": [round(t, 3) for t in librosa.frames_to_time(beats, sr=sr)],
        "key": f"{key} {mode}", "key_confidence": conf,
        "energy_rms": round(energy, 3), "brightness_hz": round(brightness),
        "sections": sections(y, sr),
        "suggested_grades": looks, "why": why,
        "note": "Music-only suggestion. Read the lyrics' meaning before choosing the final look.",
    }
    with open(args.output, "w") as f:
        json.dump(result, f, indent=1)
    print(f"wrote {args.output}: {result['bpm']} BPM, {result['key']}, suggest {looks[0]} ({why})")


if __name__ == "__main__":
    main()
