# Replace bed t [A,B] with the demucs no-vocals stem, linear crossfades of XF s (stems are phase-coherent with the original).
import sys,numpy as np,soundfile as sf
orig_p,nv_p,out_p=sys.argv[1:4]; A,B,XF=map(float,sys.argv[4:7])
o,sr=sf.read(orig_p); n,sr2=sf.read(nv_p); assert sr==sr2==48000
L=min(len(o),len(n)); o=o[:720000]; n=n[:720000]; assert len(o)==720000 and len(n)==720000
t=np.arange(720000)/sr
w=np.clip((t-(A-XF))/XF,0,1)*np.clip(((B+XF)-t)/XF,0,1)   # 0 outside, ramps over XF before A and after B
y=o*(1-w[:,None])+n*w[:,None]
sf.write(out_p,y,sr,subtype='FLOAT'); print('wrote',out_p,'w>0 from',t[w>0][0],'to',t[w>0][-1])
