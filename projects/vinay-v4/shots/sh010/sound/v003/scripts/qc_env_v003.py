import numpy as np,soundfile as sf,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
V='/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/sound/'
fig,ax=plt.subplots(2,1,figsize=(22,9))
for f,c in [('v001/mix_master_fade1440.wav','0.75'),('v002/mix_master.wav','tab:orange'),('v003/mix_master.wav','tab:blue')]:
    m,sr=sf.read(V+f); y=m.mean(1); H=480; db=20*np.log10(np.sqrt((y[:len(y)//H*H].reshape(-1,H)**2).mean(1))+1e-9); tt=np.arange(len(db))*0.01
    ax[0].plot(tt,db,lw=.8,color=c,label=f); s=(tt>=4.6)&(tt<=7.2); ax[1].plot(tt[s],db[s],'.-',ms=2,lw=.8,color=c,label=f)
for a in ax:
    a.set_ylim(-100,0); a.grid(alpha=.3); a.legend(loc='lower left',fontsize=8)
    for k,t in {'f121':4.84,'117.30':5.20,'117.38':5.28,'118.40':6.30,'118.70':6.60,'HERO f173':6.92,'TITLE f275':11.0}.items(): a.axvline(t,color='k',lw=.6); a.text(t,-3,k,fontsize=8,rotation=90,va='top')
ax[1].axhline(-45,color='r',ls=':',lw=.8); ax[1].axhline(-60,color='r',ls=':',lw=.8); ax[1].set_xticks(np.arange(4.6,7.21,0.1))
ax[0].set_title('10 ms RMS dBFS, bed time (src = t + 112.10); v001 grey, v002 orange, v003 blue',loc='left')
plt.tight_layout(); plt.savefig(V+'v003/qc/qc_envelope_v001_v002_v003.png',dpi=70)
