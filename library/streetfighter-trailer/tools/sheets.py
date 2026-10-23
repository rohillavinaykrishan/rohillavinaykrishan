import json, sys
from PIL import Image, ImageDraw, ImageFont
L=sys.argv[1]; d=json.load(open(L+'/shots.json'))['shots']
fb=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',15)
fs=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
def tile(e,w):
    t=Image.open(L+'/'+e['still']).convert('RGB'); t=t.resize((w,round(w*t.height/t.width)),Image.LANCZOS)
    im=Image.new('RGB',(w,t.height+34),(18,18,18)); im.paste(t,(0,0)); dr=ImageDraw.Draw(im)
    c=e['best_vertical_crop_cx']*w; hw=w*0.2355/2
    dr.line([c-hw,0,c-hw,t.height-1],fill=(0,255,0)); dr.line([c+hw,0,c+hw,t.height-1],fill=(0,255,0))
    lab=f"{e['id']}  {e['in']:.2f}-{e['out']:.2f}s  q{e['quality']}"+(' HERO' if e['hero'] else '')
    dr.text((3,2),lab,fill=(255,230,0),font=fb,stroke_width=2,stroke_fill=(0,0,0))
    ch=', '.join(e['characters']) if e['characters'] else '-'
    cam=e['camera']['move']+(' SOLVABLE' if e['camera']['solvable'] else '')
    dr.text((3,t.height+2),f"{ch} | {cam}",fill=(255,255,255),font=fs)
    dr.text((3,t.height+17),e['action'][:int(w/6.6)],fill=(170,170,170),font=fs)
    return im
def sheet(es,w,cols,out,title):
    ts=[tile(e,w) for e in es]; th=max(t.height for t in ts); rows=(len(ts)+cols-1)//cols
    im=Image.new('RGB',(cols*(w+4),rows*(th+4)+28),(0,0,0)); dr=ImageDraw.Draw(im)
    dr.text((6,5),title,fill=(255,255,255),font=fb)
    for i,t in enumerate(ts): im.paste(t,((i%cols)*(w+4),28+(i//cols)*(th+4)))
    im.save(out,optimize=True) if out.endswith('.png') else im.save(out,quality=88,optimize=True)
H=[e for e in d if e['hero']]
sheet(H,384,4,L+'/heroes.png',f'Street Fighter trailer - {len(H)} hero shots (green lines = 9:16 crop window)')
for k in range(0,len(d),40):
    es=d[k:k+40]; sheet(es,320,5,L+f'/sheets/sheet_{k//40+1:02d}.jpg',f"Street Fighter trailer shots {es[0]['id']}-{es[-1]['id']}  ({es[0]['in']:.1f}-{es[-1]['out']:.1f}s)")
