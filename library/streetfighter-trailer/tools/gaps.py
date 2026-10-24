import json, sys, numpy as np, soundfile as sf
from faster_whisper import WhisperModel
S=sys.argv[1]; model=sys.argv[2]
y,sr=sf.read(S+'/a16.wav')
gaps=[(18.4,22.5),(58.3,62.8),(63.5,78.2),(81.0,82.7),(83.7,87.4),(104.5,110.0),(111.8,117.2),(118.3,127.5),(130.3,131.8),(132.1,138.6),(144.0,156.7)]
m=WhisperModel(model,device='cpu',compute_type='int8',cpu_threads=3)
out=[]
for a,b in gaps:
    seg=y[int(a*sr):int(b*sr)].astype(np.float32)
    ss,_=m.transcribe(seg,language='en',vad_filter=False,word_timestamps=True,beam_size=5,condition_on_previous_text=False,no_speech_threshold=0.95,log_prob_threshold=-3.0)
    for s in ss:
        e=dict(start=round(a+s.start,2),end=round(a+s.end,2),text=s.text.strip(),avg_logprob=round(s.avg_logprob,3),no_speech_prob=round(s.no_speech_prob,3),
               words=[dict(start=round(a+w.start,2),end=round(a+w.end,2),word=w.word.strip(),p=round(w.probability,3)) for w in s.words],gap=[a,b])
        out.append(e); print(e['start'],e['end'],e['avg_logprob'],e['no_speech_prob'],e['text'],flush=True)
json.dump(out,open(S+f'/gaps_{model}.json','w'),indent=1)
