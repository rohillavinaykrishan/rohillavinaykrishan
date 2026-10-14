"""Audio/Edit department: speech or lyrics to subtitles with word timings (faster-whisper).

  vfx-python transcribe.py song.mp3 song.srt
  vfx-python transcribe.py interview.mp4 words.json --model small --language hi
Output format follows the extension: .srt, .vtt, .json (segments + words), .txt
"""
import argparse
import json
from pathlib import Path

from faster_whisper import WhisperModel


def ts(t, sep=","):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02}:{int(m):02}:{int(s):02}{sep}{int((s % 1) * 1000):03}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--model", default="small", help="tiny | base | small | medium | large-v3 (slow on CPU)")
    ap.add_argument("--language", default=None, help="e.g. en, hi; auto-detect if omitted")
    args = ap.parse_args()

    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(args.input, language=args.language, word_timestamps=True, vad_filter=True)
    segs = [{"start": s.start, "end": s.end, "text": s.text.strip(),
             "words": [{"start": w.start, "end": w.end, "word": w.word.strip()} for w in s.words or []]}
            for s in segments]

    out, ext = Path(args.output), Path(args.output).suffix.lower()
    if ext == ".json":
        out.write_text(json.dumps({"language": info.language, "segments": segs}, ensure_ascii=False, indent=1))
    elif ext in (".srt", ".vtt"):
        sep = "," if ext == ".srt" else "."
        lines = [] if ext == ".srt" else ["WEBVTT", ""]
        for n, s in enumerate(segs, 1):
            if ext == ".srt":
                lines.append(str(n))
            lines += [f"{ts(s['start'], sep)} --> {ts(s['end'], sep)}", s["text"], ""]
        out.write_text("\n".join(lines), encoding="utf-8")
    else:
        out.write_text("\n".join(s["text"] for s in segs), encoding="utf-8")
    print(f"wrote {out} ({len(segs)} segments, language={info.language})")


if __name__ == "__main__":
    main()
