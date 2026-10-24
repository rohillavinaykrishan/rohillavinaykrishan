import numpy as np,soundfile as sf,librosa,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d='/tmp/claude-0/-home-user-rohillavinaykrishan/5fe3b9fd-8381-5a1b-b6a0-30ea036f781a/scratchpad/'
o,sr=sf.read(d+'bed_soxr_raw.wav'); o=o[:720000]; r,_=sf.read(d+'nv/rep_1.0_1.0_0.5_0.06.wav')
a,b=8.4,10.9; fig,ax=plt.subplots(3,1,figsize=(22,14))
for a_,(n,y) in zip(ax[:2],[('original (mid)',o),('repaired (mid)',r)]):
    m=(y[:,0]+y[:,1])/2; D=librosa.amplitude_to_db(np.abs(librosa.stft(m[int(a*sr):int(b*sr)],n_fft=2048,hop_length=240)),ref=1.0)
    fr=librosa.fft_frequencies(sr=sr,n_fft=2048); k=fr<=8000
    a_.pcolormesh(a+np.arange(D.shape[1])*240/sr,fr[k],D[k],vmin=-40,vmax=40,shading='auto',cmap='magma'); a_.set_yscale('symlog',linthresh=500); a_.set_ylim(50,8000)
    a_.set_title(n,loc='left'); a_.axvline(8.90,color='c'); a_.axvline(10.36,color='c'); a_.axvline(10.04,color='w',ls=':')
    a_.set_xticks(np.arange(a,b,0.1)); a_.tick_params(labelsize=7)
H=480
for n,y,c in [('original',o,'0.6'),('repaired',r,'tab:blue')]:
    m=y.mean(1); db=20*np.log10(np.sqrt((m[:len(m)//H*H].reshape(-1,H)**2).mean(1))+1e-9); tt=np.arange(len(db))*0.01; s=(tt>=a)&(tt<b)
    ax[2].plot(tt[s],db[s],'.-',ms=2,lw=.8,color=c,label=n)
ax[2].axvline(8.90,color='c'); ax[2].axvline(10.36,color='c'); ax[2].axvline(10.04,color='k',ls=':'); ax[2].legend(); ax[2].grid(alpha=.3); ax[2].set_xticks(np.arange(a,b,0.1)); ax[2].tick_params(labelsize=7)
ax[2].set_title('10 ms RMS dBFS (full mix); cyan = repair span 121.00-122.46, dotted = f251',loc='left')
plt.tight_layout(); plt.savefig(d+'nv/ab_c.png',dpi=65)
# onset at f251
for n,y in [('orig',o),('rep',r)]:
    m=y.mean(1); e=20*np.log10(np.sqrt(uniform:=None) if False else 1) if False else None
import scipy.ndimage as nd
for n,y in [('orig',o),('rep',r)]:
    m=y.mean(1); H2=240; env=20*np.log10(np.sqrt(nd.uniform_filter1d(m**2,720))[::H2]+1e-9); t=np.arange(len(env))*H2/sr
    sel=(t>=9.94)&(t<=10.14); i=np.argmax(np.diff(env[sel],3)); print(n,'f251 max 15ms rise at %.3f: +%.1f dB, level after %.1f dB'%(t[sel][i+3],np.diff(env[sel],3)[i],env[sel][i+3:i+10].max()))
