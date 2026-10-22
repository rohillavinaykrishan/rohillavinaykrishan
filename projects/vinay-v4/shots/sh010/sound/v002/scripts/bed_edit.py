# v002 bed gain curve (removal edit only): fade-in 3 fr; fade to silence 117.30->117.38 (t 5.20->5.28);
# digital silence to 118.70 with a 20 ms de-click ramp ending at 118.70 (t 6.58->6.60); untouched from 118.70;
# tail fade 13.40->14.00 (linear, as v001 alt), silence to 15.00.
import sys,numpy as np,soundfile as sf
x,sr=sf.read(sys.argv[1]); x=x[:720000]; assert sr==48000 and len(x)==720000
t=np.arange(720000)/sr; g=np.ones_like(t)
def rc(a,b): return 0.5-0.5*np.cos(np.pi*np.clip((t-a)/(b-a),0,1))   # 0 at a -> 1 at b
g*=np.clip(t/0.12,0,1)                       # fade-in 0-0.12 (linear, as afade)
cut=np.where(t<5.20,1.0,np.where(t<5.28,1-rc(5.20,5.28),np.where(t<6.58,0.0,np.where(t<6.60,rc(6.58,6.60),1.0))))
g*=cut
g*=np.clip((14.00-t)/0.60,0,1)               # tail 13.40-14.00 linear
sf.write(sys.argv[2],x*g[:,None],sr,subtype='FLOAT')
print('silent samples',(g==0).sum(),' gain==1 from 6.60:',bool(np.all(g[(t>=6.60)&(t<13.40)]==1)))
