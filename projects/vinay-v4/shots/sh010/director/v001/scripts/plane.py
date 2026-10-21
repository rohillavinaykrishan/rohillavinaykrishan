import numpy as np, cv2, json
W='/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/director/v001/cm3_beach'; m=W+'/sparse_relax/0'
cam=[l.split() for l in open(m+'/cameras.txt') if not l.startswith('#')][0]
w,h,f,cx,cy,k=int(cam[2]),int(cam[3]),*map(float,cam[4:8])
L=[l for l in open(m+'/images.txt') if not l.startswith('#')]
imgs={}
for i in range(0,len(L),2):
    a=L[i].split(); imgs[a[9]]=(np.array(list(map(float,a[1:5]))),np.array(list(map(float,a[5:8]))))
def R(q):
    w_,x,y,z=q; return np.array([[1-2*(y*y+z*z),2*(x*y-z*w_),2*(x*z+y*w_)],[2*(x*y+z*w_),1-2*(x*x+z*z),2*(y*z-x*w_)],[2*(x*z-y*w_),2*(y*z+x*w_),1-2*(x*x+y*y)]])
P=np.array([list(map(float,l.split()[1:4])) for l in open(m+'/points3D.txt') if not l.startswith('#')])
names=sorted(imgs)
def proj(n,X):
    q,t=imgs[n]; Xc=(R(q)@X.T).T+t; x=Xc[:,0]/Xc[:,2]; y=Xc[:,1]/Xc[:,2]; d=1+k*(x*x+y*y); return np.c_[f*x*d+cx,f*y*d+cy],Xc[:,2]
# ground candidates: in frame 19 projected below v>0.62h
uv,z=proj(names[18],P); sel=(uv[:,1]>0.62*h)&(z>0)
G=P[sel]; best=None; rng=np.random.default_rng(0)
for _ in range(3000):
    s=G[rng.choice(len(G),3,replace=False)]; nrm=np.cross(s[1]-s[0],s[2]-s[0]); 
    if np.linalg.norm(nrm)<1e-9: continue
    nrm/=np.linalg.norm(nrm); d=-nrm@s[0]; inl=np.abs(G@nrm+d)<0.15
    if best is None or inl.sum()>best[0]: best=(inl.sum(),nrm,d)
cnt,nrm,d=best
# orient normal toward cameras
C=np.array([-R(imgs[n][0]).T@imgs[n][1] for n in names])
if (C@nrm+d).mean()<0: nrm,d=-nrm,-d
hcam=(C@nrm+d)
print('ground candidates',len(G),'inliers',cnt,'cam height above ground (colmap units) min/mean/max',hcam.min().round(3),hcam.mean().round(3),hcam.max().round(3))
# metric scale: assume mean camera height 1.0 m (low handheld / dolly) 
s=1.0/hcam.mean(); print('scale m/unit',round(s,4),'baseline m',round(np.linalg.norm(C[-1]-C[0])*s,2))
# place an upright billboard: centre on ground at a point ahead of middle camera
q,t=imgs[names[18]]; Rm=R(q); fwd=Rm.T@np.array([0,0,1.]); 
fwd_g=fwd-(fwd@nrm)*nrm; fwd_g/=np.linalg.norm(fwd_g); right=np.cross(fwd_g,nrm); 
Cm=C[18]-(C[18]@nrm+d)*nrm
out={}
for dist_m,H_m,Wd_m in [(9,2.2,16)]:
    c=Cm+fwd_g*dist_m/s
    corners=[c-right*Wd_m/2/s, c+right*Wd_m/2/s, c+right*Wd_m/2/s+nrm*H_m/s, c-right*Wd_m/2/s+nrm*H_m/s]
    corners=np.array(corners)
    tiles=[]
    for n in names[::6]+[names[-1]]:
        im=cv2.imread(W+'/images/'+n); uv,z=proj(n,corners)
        if (z>0).all(): cv2.polylines(im,[uv.astype(np.int32)],True,(255,60,220),3)
        # ground grid
        for a in np.linspace(-12,12,13):
            for bb in [(np.linspace(2,30,30))]:
                pts=np.array([Cm+fwd_g*b/s+right*a/s for b in bb]); u2,z2=proj(n,pts); ok=z2>0
                cv2.polylines(im,[u2[ok].astype(np.int32)],False,(120,255,200),1)
        cv2.putText(im,n,(8,24),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,255),2); tiles.append(cv2.resize(im,(480,201)))
    while len(tiles)%2: tiles.append(np.zeros_like(tiles[0]))
    rows=[np.hstack(tiles[i:i+2]) for i in range(0,len(tiles),2)]
    cv2.imwrite('/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/director/v001/layout_test_beach.png',np.vstack(rows))
json.dump(dict(normal=nrm.tolist(),d=float(d),scale_m_per_unit=float(s),focal_px_960=f,k1=k),open(W+'/../ground_plane_beach.json','w'),indent=1)
