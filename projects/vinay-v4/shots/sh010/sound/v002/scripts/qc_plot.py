import numpy as np,soundfile as sf,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
O='/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/sound/v001/'
cues={'f6':0.24,'f69':2.75,'f81':3.24,'f113':4.50,'f121':4.84,'f137 dip':5.48,'f141':5.65,'HERO f173':6.92,'f208':8.31,'f251':10.04,'TITLE f275':11.00,'f291':11.66,'f304':12.16}
fig,ax=plt.subplots(2,1,figsize=(24,9))
for a,f in zip(ax,['mix_master.wav','mix_master_altfade_13.40-14.00.wav']):
    m,sr=sf.read(O+f); y=m.mean(1); H=480; db=20*np.log10(np.sqrt((y[:len(y)//H*H].reshape(-1,H)**2).mean(1))+1e-9)
    a.plot(np.arange(len(db))*0.01,db,lw=0.8); a.set_ylim(-60,0); a.set_xlim(0,15); a.set_xticks(np.arange(0,15.01,0.5)); a.grid(alpha=.3)
    a.axvspan(6.37,6.60,color='grey',alpha=.3,label='near-silence 118.47-118.70')
    a.axvspan(5.27,6.36,color='red',alpha=.15,label='VOICE "You lose" (~117.4-118.46)')
    a.axvspan(14.06,15.0,color='magenta',alpha=.15,label='VOICE "I\'m a street-" (126.16->)')
    for k,t in cues.items(): a.axvline(t,color='k',lw=.8); a.text(t,-2,k,fontsize=7,rotation=90,va='top')
    a.set_title(f+'  (10 ms RMS dBFS, bed time; src = t + 112.10)',loc='left'); a.legend(loc='lower left',fontsize=8)
plt.tight_layout(); plt.savefig(O+'qc/qc_envelope_cues.png',dpi=70)
