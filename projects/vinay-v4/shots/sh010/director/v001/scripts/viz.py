import numpy as np, cv2, sys, glob, os
W=sys.argv[1]; m=glob.glob(W+'/sparse_relax/0')[0]; out=sys.argv[2]
cam=[l.split() for l in open(m+'/cameras.txt') if not l.startswith('#')][0]
w,h,f,cx,cy,k=int(cam[2]),int(cam[3]),*map(float,cam[4:8])
L=[l for l in open(m+'/images.txt') if not l.startswith('#')]
imgs={}
for i in range(0,len(L),2):
    a=L[i].split(); q=np.array(list(map(float,a[1:5]))); t=np.array(list(map(float,a[5:8]))); imgs[a[9]]=(q,t)
P=[];C=[]
for l in open(m+'/points3D.txt'):
    if l.startswith('#'): continue
    a=l.split(); P.append(list(map(float,a[1:4]))); C.append(int(a[7]) if False else float(a[7]))
P=np.array(P); E=np.array(C)
def R(q):
    w_,x,y,z=q; return np.array([[1-2*(y*y+z*z),2*(x*y-z*w_),2*(x*z+y*w_)],[2*(x*y+z*w_),1-2*(x*x+z*z),2*(y*z-x*w_)],[2*(x*z-y*w_),2*(y*z+x*w_),1-2*(x*x+y*y)]])
names=sorted(imgs); centers=[]
for n in names:
    q,t=imgs[n]; Rm=R(q); centers.append(-Rm.T@t)
centers=np.array(centers)
q,t=imgs[names[len(names)//2]]; Rm=R(q); Xc=(Rm@P.T).T+t; depth=np.median(Xc[:,2])
base=np.linalg.norm(centers[-1]-centers[0]); path=np.sum(np.linalg.norm(np.diff(centers,axis=0),axis=1))
print(f"focal {f:.1f}px @{w}  k1 {k:.3f}  hFOV {np.degrees(2*np.arctan(w/2/f)):.1f}deg  frames {len(names)}  pts {len(P)}")
print(f"camera baseline first-last {base:.3f}  path {path:.3f}  median scene depth {depth:.3f}  baseline/depth {base/depth:.3f}")
rot=np.degrees(np.arccos(np.clip((np.trace(R(imgs[names[0]][0]).T@R(imgs[names[-1]][0]))-1)/2,-1,1)))
print(f"rotation first-last {rot:.1f} deg")
tiles=[]
for n in [names[0],names[len(names)//2],names[-1]]:
    im=cv2.imread(W+'/images/'+n); q,t=imgs[n]; Rm=R(q); Xc=(Rm@P.T).T+t; ok=Xc[:,2]>0
    x=Xc[ok,0]/Xc[ok,2]; y=Xc[ok,1]/Xc[ok,2]; r2=x*x+y*y; d=1+k*r2
    u=f*x*d+cx; v=f*y*d+cy
    for uu,vv in zip(u,v):
        if 0<=uu<w and 0<=vv<h: cv2.drawMarker(im,(int(uu),int(vv)),(80,255,190),cv2.MARKER_CROSS,7,1)
    cv2.putText(im,n,(8,24),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,255),2)
    tiles.append(im)
cv2.imwrite(out,np.vstack(tiles))
np.savetxt(os.path.join(W,'cam_centers.txt'),centers)
