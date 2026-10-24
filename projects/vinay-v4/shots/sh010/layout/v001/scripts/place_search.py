# place_search.py : search MONUMENT_ANCHOR (x, y, rotz) so the monument passes the 9.2.4 checks on all 52 frames
import json, numpy as np, itertools
L='/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/layout/v001/'
cj=json.load(open(L+'cams.json')); f,cx,cy,k1,W,H=cj['f'],cj['cx'],cj['cy'],cj['k1'],cj['width'],cj['height']
TOP=3.99; HALF=2160/(2808/W)/2
# box surface samples (local)
g=np.linspace(0,1,9); pts=[]
for a,b in itertools.product(g,g):
    for fx in (-3.9,3.9): pts.append((fx,-0.5+a,TOP*b))
    for fy in (-0.5,0.5): pts.append((-3.9+7.8*a,fy,TOP*b))
    for fz in (0,TOP): pts.append((-3.9+7.8*a,-0.5+b,fz))
B=np.array(pts)
Rs=[(np.array(c['R']),np.array(c['t'])) for c in cj['frames']]
def ev(ax,ay,rz):
    r=np.radians(rz); c_,s_=np.cos(r),np.sin(r); X=np.c_[ax+c_*B[:,0]-s_*B[:,1], ay+s_*B[:,0]+c_*B[:,1], B[:,2]]
    cen=np.array([ax,ay,TOP/2]); bb=[];cr=[]
    for R,t in Rs:
        Xc=X@R.T+t; x=Xc[:,0]/Xc[:,2]; y=Xc[:,1]/Xc[:,2]; d=1+k1*(x*x+y*y); u=f*x*d+cx; v=f*y*d+cy
        bb.append((u.min(),v.min(),u.max(),v.max()))
        cc=R@cen+t; xx,yy=cc[0]/cc[2],cc[1]/cc[2]; cr.append(f*xx*(1+k1*(xx*xx+yy*yy))+cx)
    bb=np.array(bb); cr=np.array(cr); k=np.exp(-0.5*(np.arange(-12,13)/6.0)**2); k/=k.sum()
    cxs=np.clip(np.convolve(np.r_[np.full(12,cr[0]),cr,np.full(12,cr[-1])],k,'valid'),493,787)
    mx=np.minimum.reduce([bb[:,0]-(cxs-HALF), (cxs+HALF)-bb[:,2], bb[:,1]-0.06*H, H-bb[:,3]])  # margin px (>=0 ok)
    return mx.min(), mx, bb, cxs
if __name__=='__main__':
    print('lookdev (1.5,12.5,-12): min margin %.1f'%ev(1.5,12.5,-12)[0])
    res=[]
    for ax in np.arange(-3,3.01,0.5):
        for ay in np.arange(12.5,20.01,0.5):
            for rz in (-20,-16,-12,-8,-4,0):
                m=ev(ax,ay,rz)[0]; res.append((m,ax,ay,rz))
    ok=[r for r in res if r[0]>=8]
    print('passing (margin>=8px):',len(ok))
    # prefer the closest to the lookdev placement (largest on screen) among passing ones, report a few
    ok.sort(key=lambda r:(r[2],abs(r[1]-1.5),abs(r[3]+12)))
    for r in ok[:12]: print('margin %.1f  x %.1f y %.1f rz %d'%r)
    print('best margin overall',sorted(res)[-3:])
