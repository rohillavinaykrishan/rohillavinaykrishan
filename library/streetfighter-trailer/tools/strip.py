import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont
S=sys.argv[1]; out=sys.argv[2]; L=[int(x) for x in sys.argv[3].split(',')]
offs=[int(x) for x in (sys.argv[4] if len(sys.argv)>4 else '-4,-2,-1,0,1,3').split(',')]
W,H=160,67
a=np.memmap(S+'/small.rgb',np.uint8,'r').reshape(-1,H,W,3)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',12)
im=Image.new('RGB',(len(offs)*(W+2),len(L)*(H+3)),(60,0,0)); d=ImageDraw.Draw(im)
for r,i in enumerate(L):
  for c,o in enumerate(offs):
    j=min(max(i+o,0),len(a)-1); x=c*(W+2); y=r*(H+3)
    im.paste(Image.fromarray(np.array(a[j])),(x,y)); d.text((x+2,y),str(j),fill=(255,255,0) if o else (0,255,0),font=f)
im.save(out)
