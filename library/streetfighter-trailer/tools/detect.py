import numpy as np, json, sys
S=sys.argv[1]
W,H=160,67
a=np.fromfile(S+'/small.rgb',np.uint8).reshape(-1,H,W,3).astype(np.float32)
N=len(a); print(N)
sc=np.array(json.load(open(S+'/scores.json'))['s'])
# histogram diff: 8x8x8 rgb hist normalised
q=(a//32).astype(int); idx=q[...,0]*64+q[...,1]*8+q[...,2]
h=np.stack([np.bincount(i.ravel(),minlength=512) for i in idx]).astype(np.float32); h/=h.sum(1,keepdims=True)
hd=np.r_[0,0.5*np.abs(h[1:]-h[:-1]).sum(1)]
# luma-normalised pixel diff (robust to dark)
g=a.mean(3); gn=(g-g.mean((1,2),keepdims=True))/(g.std((1,2),keepdims=True)+4)
pd=np.r_[0,np.abs(gn[1:]-gn[:-1]).mean((1,2))]
np.save(S+'/feat.npy',np.stack([sc,hd,pd],1))
def peaks(x,k=6,ratio=3.0,minv=0.0):
    out=[]
    for i in range(1,N):
        lo=max(0,i-k);hi=min(N,i+k+1)
        nb=np.r_[x[lo:i],x[i+1:hi]]
        if x[i]==x[lo:hi].max() and x[i]>minv and x[i]>ratio*(np.median(nb)+1e-3): out.append(i)
    return out
P1=set(peaks(pd,ratio=2.5,minv=0.35)); P2=set(peaks(hd,ratio=3,minv=0.25)); P0=set(i for i in range(N) if sc[i]>0.3)
allc=sorted(P0|P1|P2)
for i in allc: print(i, round(i*1001/24000,2), 'sc%.2f hd%.2f pd%.2f'%(sc[i],hd[i],pd[i]), ''.join(c for c,P in zip('SHP',[P0,P2,P1]) if i in P))
print(len(allc))
json.dump(allc,open(S+'/cands.json','w'))
