import json,sys,numpy as np,soundfile as sf
x,sr=sf.read(sys.argv[1]); m=x.mean(1) if x.ndim>1 else x
H=int(sr*0.01); n=len(m)//H
rms=np.array([np.sqrt(np.mean(m[i*H:(i+1)*H]**2))+1e-12 for i in range(n)]); db=20*np.log10(rms)
# spectral flux (positive) on 10ms hop, 20ms window
W=2*H; win=np.hanning(W); prev=None; flux=np.zeros(n)
for i in range(n):
    s=m[i*H:i*H+W]
    if len(s)<W: break
    sp=np.abs(np.fft.rfft(s*win)); lsp=np.log1p(sp*100)
    if prev is not None: flux[i]=np.maximum(lsp-prev,0).sum()
    prev=lsp
rise=np.r_[0,np.diff(db)]
cues=json.load(open(sys.argv[2]))['music_hits']; IN=112.10
out={}
for k,v in cues.items():
    if isinstance(v['f'],list): continue
    t=v['f']/25; lo=int(round((t-0.12)/0.01)); hi=int(round((t+0.12)/0.01))+1
    i_f=lo+int(np.argmax(flux[lo:hi])); i_r=lo+int(np.argmax(rise[lo:hi]))
    out[k]=dict(f=v['f'],t=round(t,2),src_cue=v['src'],flux_t=round(i_f*0.01,2),rise_t=round(i_r*0.01,2),
        rise_db=round(float(rise[i_r]),1),db_after=round(float(db[i_r:i_r+4].max()),1),
        off_frames_flux=round((i_f*0.01-t)*25,2),off_frames_rise=round((i_r*0.01-t)*25,2))
    print(k,out[k])
# silence: 10ms bins 6.0-7.2
print('dB 6.20-7.10 bed time (src+112.10):')
for i in range(620,712): print(f"{i/100:.2f}/{IN+i/100:.2f}:{db[i]:.1f}",end='  ' if (i-619)%8 else '\n')
print()
json.dump(dict(db=db.tolist(),flux=flux.tolist(),hits=out),open(sys.argv[3],'w'))
