import json,numpy as np,soundfile as sf,librosa
x,sr=sf.read('/tmp/claude-0/-home-user-rohillavinaykrishan/5fe3b9fd-8381-5a1b-b6a0-30ea036f781a/scratchpad/bed_soxr_raw.wav'); y=x[:720000].mean(1).astype(np.float32)
oenv=librosa.onset.onset_strength(y=y,sr=sr,hop_length=240)
tempo,beats=librosa.beat.beat_track(onset_envelope=oenv,sr=sr,hop_length=240,start_bpm=172,tightness=200)
bt=librosa.frames_to_time(beats,sr=sr,hop_length=240); per=np.median(np.diff(bt)); print('tempo',np.round(tempo,1),'beat period',round(per,4),'n beats',len(bt))
# fit a linear grid to beats
k=np.round((bt-bt[0])/per); A=np.vstack([k,np.ones_like(k)]).T; (p,t0),*_=np.linalg.lstsq(A,bt,rcond=None); print('grid period %.4f s (%.1f BPM) phase %.3f'%(p,60/p,t0))
res=json.load(open('/tmp/claude-0/-home-user-rohillavinaykrishan/5fe3b9fd-8381-5a1b-b6a0-30ea036f781a/scratchpad/nv/raw_spans.json'))
def grid_err(t,div):   # distance (ms) to nearest 1/div-beat grid point
    g=p/div; return abs(((t-t0)/g-np.round((t-t0)/g)))*g*1000
rng=np.random.default_rng(0)
for r in res:
    if r['model']!='medium' or r['ch']!='mid' or r['win'] not in ([0.0,4.0],[3.6,5.4],[8.0,11.0]): continue
    st=np.array([w[0] for w in r['words']])
    e=np.array([grid_err(t,4) for t in st])        # 16th-note grid
    rnd=np.array([grid_err(t,4) for t in rng.uniform(r['win'][0],r['win'][1],5000)])
    print(r['win'],repr(r['text']))
    print('   word starts',[ (w[0],w[2]) for w in r['words']])
    print('   16th grid (%.0f ms) median err %.1f ms vs random %.1f ms; IOIs'%(p/4*1000,np.median(e),np.median(rnd)),np.round(np.diff(st),3).tolist())
