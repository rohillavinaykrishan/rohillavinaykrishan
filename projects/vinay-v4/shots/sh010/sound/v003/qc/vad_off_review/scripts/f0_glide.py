# Fill the untracked end glide (10.10-10.38) of the spoken line with the centre channel's spectral peak in 220-560 Hz
import numpy as np,soundfile as sf,librosa
d='/tmp/claude-0/-home-user-rohillavinaykrishan/5fe3b9fd-8381-5a1b-b6a0-30ea036f781a/scratchpad/nv/'
C,sr=sf.read(d+'center.wav'); X=np.abs(librosa.stft(C,n_fft=8192,hop_length=480)); fr=librosa.fft_frequencies(sr=sr,n_fft=8192); ft=librosa.frames_to_time(np.arange(X.shape[1]),sr=sr,hop_length=480)
tt,f0,vp=np.load(d+'f0c.npy'); f0=f0.copy()
band=(fr>=220)&(fr<=560)
for i,t in enumerate(tt):
    if 10.10<=t<=10.38 and f0[i]<=0:
        j=np.argmin(np.abs(ft-t)); col=X[band,j]; k=np.argmax(col)
        if col[k]>2.5*np.median(col): f0[i]=fr[band][k]
s=(tt>=10.0)&(tt<=10.4); print([(round(a,2),round(b)) for a,b in zip(tt[s],f0[s])][::3])
np.save(d+'f0c_glide.npy',np.stack([tt,f0,vp]))
