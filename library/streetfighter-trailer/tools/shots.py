import numpy as np, json, sys, colorsys
S=sys.argv[1]
FPS=24000/1001
c=json.load(open(S+'/cands.json'))
false={187,392,399,419,1119,1903,2376,2467,3105,3212,3692,3694}
cuts=[0]+[x for x in c if x not in false]
N=4046; cuts.append(N)
pf=np.load(S+'/perframe.npy')  # i,lap,sd,mean,blk,dx,dy,res,mag
a=np.memmap(S+'/small.rgb',np.uint8,'r').reshape(-1,67,160,3)
def huename(h):
    names=[(15,'red'),(45,'orange'),(70,'yellow'),(160,'green'),(200,'cyan'),(255,'blue'),(290,'purple'),(335,'magenta'),(361,'red')]
    for lim,n in names:
        if h<lim: return n
shots=[]
for k in range(len(cuts)-1):
    i0,i1=cuts[k],cuts[k+1]-1
    fr=np.asarray(a[i0:i1+1],np.float32)
    m=fr.reshape(-1,3).mean(0)
    hsv=np.array([colorsys.rgb_to_hsv(*(p/255)) for p in fr[::max(1,len(fr)//6)].reshape(-1,3)[::7]])
    w=(hsv[:,1]>0.25)&(hsv[:,2]>0.12)
    if w.mean()<0.08: hue='neutral'; hd=None
    else:
        hh=np.histogram(hsv[w,0]*360,bins=36,range=(0,360))[0]; hd=int(hh.argmax()*10+5); hue=huename(hd)
    seg=pf[i0:i1+1]
    lo=i0+int(0.15*(i1-i0)); hi=i0+int(0.85*(i1-i0))
    cand=pf[lo:hi+1] if hi>lo else seg
    cand=cand[cand[:,3]>12] if (cand[:,3]>12).any() else cand
    best=int(cand[cand[:,1].argmax(),0])
    mot=pf[i0+1:i1+1] if i1>i0 else seg
    shots.append(dict(i0=i0,i1=i1,mean_rgb=[round(float(x),1) for x in m],hue=hue,hue_deg=hd,blue=bool(m[2]>m[0]),
      still_frame=best,lap=float(pf[best,1]),sd=float(pf[best,2]),luma=float(seg[:,3].mean()),blk=float(np.median(seg[:,4])),
      dx=float(np.median(np.abs(mot[:,5]))),dy=float(np.median(np.abs(mot[:,6]))),sdx=float(np.std(mot[:,5])),sdy=float(np.std(mot[:,6])),
      res=float(np.median(mot[:,7])),mag=float(np.median(mot[:,8])),magmax=float(mot[:,8].max()),
      net_dx=float(mot[:,5].sum()),net_dy=float(mot[:,6].sum())))
json.dump(shots,open(S+'/shots_raw.json','w'))
print(len(shots))
for n,s in enumerate(shots):
    print(n+1,s['i0'],s['i1'],round((s['i1']-s['i0']+1)/FPS,2),s['hue'],'lap%.0f blk%.2f luma%.0f mag%.2f max%.1f dx%.2f dy%.2f ndx%.0f ndy%.0f res%.2f'%(s['lap'],s['blk'],s['luma'],s['mag'],s['magmax'],s['dx'],s['dy'],s['net_dx'],s['net_dy'],s['res']))
