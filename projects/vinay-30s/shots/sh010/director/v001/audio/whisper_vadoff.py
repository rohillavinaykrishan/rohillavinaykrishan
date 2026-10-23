# Whisper check with VAD OFF (VAD hides vocals under music). usage: vfx-python whisper_vadoff.py in.wav out.json
import sys, json
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=2)
segs, info = m.transcribe(sys.argv[1], vad_filter=False, word_timestamps=True, beam_size=5,
                          condition_on_previous_text=False, no_speech_threshold=0.6)
out = {"file": sys.argv[1], "vad_filter": False, "model": "small", "language": info.language,
       "language_prob": info.language_probability, "segments": []}
for s in segs:
    out["segments"].append({"start": s.start, "end": s.end, "text": s.text, "no_speech_prob": s.no_speech_prob,
        "avg_logprob": s.avg_logprob, "words": [[w.start, w.end, w.word, w.probability] for w in (s.words or [])]})
json.dump(out, open(sys.argv[2], "w"), indent=1)
print(json.dumps({"lang": out["language"], "n": len(out["segments"]),
  "segs": [(round(s["start"],2), round(s["end"],2), s["text"], round(s["no_speech_prob"],2), round(s["avg_logprob"],2)) for s in out["segments"]]}, indent=0))
