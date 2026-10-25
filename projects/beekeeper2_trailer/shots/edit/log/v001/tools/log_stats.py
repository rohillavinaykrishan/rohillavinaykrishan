#!/usr/bin/env python3
"""Per-shot stats + thumbnails + contact sheet for the source trailer.
usage: log_stats.py <src.mp4> <outdir> <review_dir>"""
import sys, json, subprocess, os
import numpy as np
from PIL import Image
src, out, rev = sys.argv[1:4]
FPS = 24000/1001
TOTAL = 2092
STARTS = [0,86,476,500,524,549,575,598,622,647,671,731,746,781,807,862,903,915,927,941,961,972,986,
          1000,1025,1052,1072,1098,1141,1150,1170,1187,1196,1212,1231,1248,1258,1270,1279,1290,1302,
          1325,1417,1448,1462,1491,1504,1528,1540,1560,1571,1583,1597,1618,1627,1641,1657,1666,1676,
          1720,1806]
W,H = 1280,720; Y0,AH = 92,536   # active 2.39 area inside source letterbox
def grab(f):
    t = (f+0.5)/FPS
    raw = subprocess.run(["ffmpeg","-v","error","-ss",f"{t:.4f}","-i",src,"-frames:v","1",
                          "-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
    return np.frombuffer(raw,np.uint8).reshape(H,W,3)
os.makedirs(f"{out}/thumbs",exist_ok=True)
shots=[]
for i,s in enumerate(STARTS):
    e = STARTS[i+1] if i+1<len(STARTS) else TOTAL
    n = e-s
    samp = sorted(set([s+max(0,n//4), s+n//2, s+min(n-1,3*n//4)]))
    imgs=[grab(f)[Y0:Y0+AH].astype(np.float32) for f in samp]
    a=np.stack(imgs)
    y=0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]
    mid=grab(s+n//2)
    sid=f"s{i+1:03d}"
    Image.fromarray(mid).resize((320,180)).save(f"{out}/thumbs/{sid}.jpg",quality=88)
    shots.append(dict(id=sid,start_frame=s,end_frame=e,frames=n,
        start=round(s/FPS,3),end=round(e/FPS,3),duration=round(n/FPS,3),
        thumb=f"thumbs/{sid}.jpg",
        stats=dict(luma_mean=round(float(y.mean()),1),
                   luma_p5=round(float(np.percentile(y,5)),1),
                   luma_p95=round(float(np.percentile(y,95)),1),
                   clip_pct=round(float((y>250).mean()*100),2),
                   crush_pct=round(float((y<8).mean()*100),2),
                   rgb_mean=[round(float(a[...,c].mean()),1) for c in range(3)])))
json.dump(shots,open(f"{out}/_stats.json","w"),indent=1)
# contact sheet
from PIL import ImageDraw, ImageFont
try: font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",15)
except Exception: font=ImageFont.load_default()
cols=8; tw,th=320,180; lh=22
rows=(len(shots)+cols-1)//cols
sheet=Image.new("RGB",(cols*(tw+4)+4,rows*(th+lh+4)+4),(25,25,25))
d=ImageDraw.Draw(sheet)
def tc(t):
    m=int(t//60); sec=t-60*m; return f"{m:02d}:{sec:05.2f}"
for k,sh in enumerate(shots):
    x=4+(k%cols)*(tw+4); y=4+(k//cols)*(th+lh+4)
    sheet.paste(Image.open(f"{out}/{sh['thumb']}"),(x,y+lh))
    d.text((x+2,y+3),f"{sh['id']} {tc(sh['start'])}-{tc(sh['end'])} ({sh['duration']:.2f}s)",fill=(255,220,60),font=font)
os.makedirs(rev,exist_ok=True)
sheet.save(f"{rev}/footage_contact_sheet.jpg",quality=88)
print(len(shots),"shots")
