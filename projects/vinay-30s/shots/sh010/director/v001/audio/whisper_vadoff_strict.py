# Stricter VAD-OFF check: no_speech_threshold disabled (nothing is dropped), model as argv[3] (small|medium).
# usage: vfx-python whisper_vadoff_strict.py in.wav out.json medium
import sys, json
from faster_whisper import WhisperModel
m = WhisperModel(sys.argv[3] if len(sys.argv)>3 else "small", device="cpu", compute_type="int8", cpu_threads=2)
segs, info = m.transcribe(sys.argv[1], vad_filter=False, word_timestamps=True, beam_size=5, language="en",
                          condition_on_previous_text=False, no_speech_threshold=None, log_prob_threshold=None)
out={"file":sys.argv[1],"vad_filter":False,"no_speech_threshold":None,"model":sys.argv[3] if len(sys.argv)>3 else "small","segments":[]}
for s in segs:
    out["segments"].append({"start":s.start,"end":s.end,"text":s.text,"no_speech_prob":s.no_speech_prob,"avg_logprob":s.avg_logprob,
        "words":[[w.start,w.end,w.word,w.probability] for w in (s.words or [])]})
json.dump(out, open(sys.argv[2],"w"), indent=1)
for s in out["segments"]: print(round(s["start"],2), round(s["end"],2), s["text"], round(s["no_speech_prob"],2), round(s["avg_logprob"],2))
print("n", len(out["segments"]))
