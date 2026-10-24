# usage: clean.py plate.mp4 sam_alpha.mov outdir name
import sys, subprocess, numpy as np, cv2, os
plate, src, outdir, name = sys.argv[1:5]
W,H=2400,900
def rd(path,vf,ch):
    b=subprocess.run(["ffmpeg","-v","error","-i",path,"-vf",vf,"-f","rawvideo","-"],capture_output=True,check=True).stdout
    return np.frombuffer(b,np.uint8).reshape((-1,H,W) if ch==1 else (-1,H,W,ch))
a=rd(src,"alphaextract,format=gray",1).astype(np.float32)
g=rd(plate,"format=gray",1)
n=len(a); assert n==len(g)
gy,gx=np.mgrid[0:H,0:W].astype(np.float32)
def warp(j,i):  # bring matte j into frame i
    s=0.5  # flow at half res
    gi=cv2.resize(g[i],None,fx=s,fy=s); gj=cv2.resize(g[j],None,fx=s,fy=s)
    f=cv2.calcOpticalFlowFarneback(gi,gj,None,0.5,5,31,5,7,1.5,0)
    f=cv2.resize(f,(W,H))/s
    return cv2.remap(a[j],gx+f[...,0],gy+f[...,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
d=os.path.join(outdir,f"{name}_matte_png"); os.makedirs(d,exist_ok=True)
for i in range(n):
    prev=warp(i-1,i) if i>0 else a[i]; nxt=warp(i+1,i) if i<n-1 else a[i]
    m=np.median(np.stack([prev,a[i],nxt]),0).astype(np.uint8)   # 3-frame motion-compensated median
    core=cv2.erode((a[i]>127).astype(np.uint8)*255,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(13,13)))
    m=np.maximum(m,core)                                         # median only acts on the edge band
    m=cv2.erode(m,k,iterations=1)                               # erode 1 px
    m=cv2.GaussianBlur(m,(0,0),2)                               # feather 2 px
    iou=((m>127)&(a[i]>127)).sum()/max(((m>127)|(a[i]>127)).sum(),1)
    cv2.imwrite(os.path.join(d,f"{name}_matte.{i:04d}.png"),m)
    print(name,i,"IoU vs raw",round(float(iou),3),flush=True)
