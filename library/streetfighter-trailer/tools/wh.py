import json, sys
from faster_whisper import WhisperModel
m=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=3)
segs,info=m.transcribe(sys.argv[1],language='en',vad_filter=False,word_timestamps=True,beam_size=5,condition_on_previous_text=False,no_speech_threshold=0.9,log_prob_threshold=-2.0,compression_ratio_threshold=2.8)
out=[]
for s in segs:
    out.append(dict(start=round(s.start,2),end=round(s.end,2),text=s.text.strip(),avg_logprob=round(s.avg_logprob,3),no_speech_prob=round(s.no_speech_prob,3),
      words=[dict(start=round(w.start,2),end=round(w.end,2),word=w.word.strip(),p=round(w.probability,3)) for w in s.words]))
    print(out[-1]['start'],out[-1]['end'],out[-1]['text'],flush=True)
json.dump(dict(model='small',vad_filter=False,segments=out),open(sys.argv[2],'w'),indent=1)
