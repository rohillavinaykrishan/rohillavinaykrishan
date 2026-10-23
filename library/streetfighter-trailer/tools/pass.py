import numpy as np, cv2, subprocess, sys, json
S=sys.argv[1]; src=sys.argv[2]
W,H=1280,536
p=subprocess.Popen(['ffmpeg','-v','error','-i',src,'-an','-vf','crop=1280:536:0:92','-f','rawvideo','-pix_fmt','gray','-'],stdout=subprocess.PIPE,bufsize=W*H*4)
rows=[]; prev=None; i=0
bm_r=(np.arange(H-1)%8==3)  # diff between row y and y+1 where y+1 %8==4
bm_c=(np.arange(W-1)%8==7)
while True:
    b=p.stdout.read(W*H)
    if len(b)<W*H: break
    g=np.frombuffer(b,np.uint8).reshape(H,W).astype(np.float32)
    lap=cv2.Laplacian(g,cv2.CV_32F).var()
    sd=g.std(); mean=g.mean()
    dr=np.abs(np.diff(g,axis=0)).mean(1); dc=np.abs(np.diff(g,axis=1)).mean(0)
    blk=(dr[bm_r].mean()/(dr[~bm_r].mean()+1e-3)+dc[bm_c].mean()/(dc[~bm_c].mean()+1e-3))/2
    s=cv2.resize(g,(320,134),interpolation=cv2.INTER_AREA)
    dx=dy=res=mag=0.0
    if prev is not None:
        fl=cv2.calcOpticalFlowFarneback(prev,s,None,0.5,3,15,3,5,1.2,0)
        ys,xs=np.mgrid[0:134:4,0:320:4]; f=fl[::4,::4]
        src_=np.stack([xs.ravel(),ys.ravel()],1).astype(np.float32); dst=src_+f.reshape(-1,2)
        M,inl=cv2.estimateAffinePartial2D(src_,dst,method=cv2.RANSAC,ransacReprojThreshold=1.0)
        if M is not None:
            pr=src_@M[:,:2].T+M[:,2]; r=np.linalg.norm(dst-pr,axis=1)
            res=float(np.median(r)); dx=float(M[0,2]); dy=float(M[1,2])
        mag=float(np.median(np.linalg.norm(f.reshape(-1,2),axis=1)))
    rows.append([i,lap,sd,mean,blk,dx,dy,res,mag]); prev=s; i+=1
np.save(S+'/perframe.npy',np.array(rows,np.float32)); print(i)
