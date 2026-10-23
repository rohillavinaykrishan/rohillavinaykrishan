import numpy as np, json, sys
from PIL import Image, ImageDraw, ImageFont
S=sys.argv[1]; W,H=160,67
a=np.memmap(S+'/small.rgb',np.uint8,'r').reshape(-1,H,W,3)
c=json.load(open(S+'/cands.json'))
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',13)
per=60; cols=4
for k in range(0,len(c),per):
    ch=c[k:k+per]; rows=(len(ch)+cols-1)//cols
    im=Image.new('RGB',(cols*(2*W+12),rows*(H+4)),(40,40,40)); d=ImageDraw.Draw(im)
    for j,i in enumerate(ch):
        x=(j%cols)*(2*W+12); y=(j//cols)*(H+4)
        im.paste(Image.fromarray(np.array(a[i-1])),(x,y)); im.paste(Image.fromarray(np.array(a[i])),(x+W+2,y))
        d.rectangle([x,y,x+50,y+15],fill=(0,0,0)); d.text((x+2,y),str(i),fill=(255,255,0),font=f)
    im.save(f'{S}/pairs_{k//per}.png')
