import numpy as np, json, sys, glob, cv2
from PIL import Image
from rembg import new_session, remove
S=sys.argv[1]; L=sys.argv[2]
sess=new_session('u2net_human_seg')
out={}
for p in sorted(glob.glob(L+'/stills/sf*.jpg')):
    im=Image.open(p).convert('RGB'); m=np.array(remove(im,session=sess,only_mask=True)).astype(np.float32)/255
    area=float((m>0.5).mean())
    g=cv2.cvtColor(np.array(im),cv2.COLOR_RGB2GRAY).astype(np.float32)
    # fallback saliency: local contrast energy
    sal=cv2.GaussianBlur(np.abs(cv2.Laplacian(g,cv2.CV_32F)),(0,0),15)+0.5*cv2.GaussianBlur(g,(0,0),25)
    col_s=sal.sum(0); cx_sal=float((col_s*np.arange(len(col_s))).sum()/col_s.sum()/len(col_s))
    if area>0.01:
        n,lab,st,_=cv2.connectedComponentsWithStats((m>0.5).astype(np.uint8))
        big=1+np.argsort(-st[1:,cv2.CC_STAT_AREA])[:2]
        mm=np.isin(lab,big)*m
        ys,xs=np.nonzero(mm>0.5)
        # weight upper body (heads) more
        top=ys.min(); h=ys.max()-top+1
        w=np.where(ys<top+0.5*h,2.0,1.0)
        cx=float((xs*w).sum()/w.sum()/m.shape[1]); src='human_mask'
    else: cx=cx_sal; src='saliency'
    out[p.split('/')[-1][:5]]=dict(cx=round(cx,3),area=round(area,3),src=src)
json.dump(out,open(S+'/cx.json','w'),indent=0); print(len(out))
