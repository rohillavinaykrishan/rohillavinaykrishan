"""VAD-OFF Whisper gate. usage: whisper_novad.py in.wav out.json --models small,medium --windows "0:15,0:4,..." [--channels full,mid,side] [--offset SRC0]
Each window is cut from the file, optionally converted to mid (L+R)/2 or side (L-R)/2, resampled to 16 kHz, and transcribed with
vad_filter=False, temperature 0, condition_on_previous_text=False, word timestamps. Word times are reported in file time."""
import argparse,json,numpy as np,soundfile as sf
from scipy.signal import resample_poly
from faster_whisper import WhisperModel
ap=argparse.ArgumentParser(); ap.add_argument('inp'); ap.add_argument('out')
ap.add_argument('--models',default='small,medium'); ap.add_argument('--windows',default='0:15'); ap.add_argument('--channels',default='full,mid,side')
a=ap.parse_args()
x,sr=sf.read(a.inp,dtype='float32'); x=x if x.ndim==2 else np.stack([x,x],1)
chans={'full':x.mean(1),'mid':(x[:,0]+x[:,1])/2,'side':(x[:,0]-x[:,1])/2}   # 'full' = mono downmix = mid; kept for clarity
res=[]
for mname in a.models.split(','):
    model=WhisperModel(mname,device='cpu',compute_type='int8',cpu_threads=2)
    for ch in a.channels.split(','):
        for w in a.windows.split(','):
            t0,t1=map(float,w.split(':')); seg=chans[ch][int(t0*sr):int(t1*sr)]
            if np.abs(seg).max()>0: seg=seg/np.abs(seg).max()*0.9      # normalise (side is quiet)
            y=resample_poly(seg,1,3).astype(np.float32) if sr==48000 else resample_poly(seg,16000,sr).astype(np.float32)
            segs,_=model.transcribe(y,language='en',vad_filter=False,temperature=0.0,condition_on_previous_text=False,word_timestamps=True,beam_size=5)
            words=[(round(t0+wd.start,2),round(t0+wd.end,2),wd.word.strip(),round(wd.probability,2)) for s in segs for wd in (s.words or [])]
            r=dict(model=mname,ch=ch,win=[t0,t1],text=' '.join(z[2] for z in words),words=words); res.append(r)
            print(f"{mname:6s} {ch:4s} [{t0:5.2f}-{t1:5.2f}] {r['text']!r}",flush=True)
json.dump(res,open(a.out,'w'),indent=1)
