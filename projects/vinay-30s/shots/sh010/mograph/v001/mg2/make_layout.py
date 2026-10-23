"""MG2: builds ../name_layout.json (the only layout of the name) from the real font metrics."""
import json, os
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
HERE=os.path.dirname(os.path.abspath(__file__))
SH=os.path.abspath(os.path.join(HERE,'../../..'))
FONT=os.path.join(SH,'director/v001/fonts/Unbounded-900.ttf')
f=TTFont(FONT); upm=f['head'].unitsPerEm; cap=f['OS/2'].sCapHeight
cmap=f.getBestCmap(); hm=f['hmtx']; gs=f.getGlyphSet()
KERN={('A','Y'):-165,('R','O'):-9}   # GPOS pair values for these letters (checked against the font)
CAP_PX=230; PITCH=270; CX,CY=1080,1550; TRACK_EM=0.02; MAXW=1880
size=CAP_PX*upm/cap
lines=['VINAY','KRISHAN','ROHILLA']
def ink(ch):
    bp=BoundsPen(gs); gs[cmap[ord(ch)]].draw(bp); return bp.bounds
def measure(w,s):
    t=TRACK_EM*s; x=0; glyphs=[]
    for i,ch in enumerate(w):
        b=ink(ch); glyphs.append(dict(ch=ch,pen_x=x,ink_x0=x+b[0]*s/upm,ink_x1=x+b[2]*s/upm))
        x+=hm[cmap[ord(ch)]][0]*s/upm
        if i<len(w)-1: x+=t+KERN.get((ch,w[i+1]),0)*s/upm
    return glyphs
scale=1.0
widest=max(g[-1]['ink_x1']-g[0]['ink_x0'] for g in (measure(w,size) for w in lines))
if widest>MAXW: scale=MAXW/widest
size*=scale; cap_px=CAP_PX*scale; pitch=PITCH*scale
block_h=2*pitch+cap_px; top=CY-block_h/2
out=dict(owner='MG2 (shots/sh010/mograph/v001/mg2)', version='v001',
  canvas=[2160,3840], units='px at 4K (2160x3840), y down',
  font=dict(family='Unbounded', weight=900, file='shots/sh010/director/v001/fonts/Unbounded-900.ttf',
            size_px=round(size,3), cap_height_px=round(cap_px,3), letter_spacing_px=round(TRACK_EM*size,3),
            tracking_em=TRACK_EM, kerning='font GPOS on (only pairs in the name: A-Y -165u, R-O -9u)', text_transform='none (text is already caps)'),
  name_centre=[CX,CY], line_pitch_px=round(pitch,3), scale_applied=round(scale,5),
  block_ink_box=None, lines=[],
  css_recipe=("Each line: position:absolute; left:<pen_x0>px; top:<baseline_y - ascent_px>px; "
    "font:900 <size_px>px Unbounded; letter-spacing:<letter_spacing_px>px; line-height:<ascent_px+descent_px>px; "
    "white-space:nowrap; font-kerning:normal. ascent/descent = hhea 995/245 units -> see font.ascent_px. "
    "Or place each glyph at glyphs[].pen_x (absolute) on the baseline. Visual centre = ink centre (not advance centre)."),
  colours=dict(fill='#FFF8EC', glow='#FFC94D 45% outer 36px', keyline='#C7851E 2px offset (0,+6px)'))
asc=f['hhea'].ascent*size/upm; desc=-f['hhea'].descent*size/upm
out['font']['ascent_px']=round(asc,3); out['font']['descent_px']=round(desc,3)
bx0,by0,bx1,by1=1e9,1e9,-1e9,-1e9
for i,w in enumerate(lines):
    g=measure(w,size); x0=g[0]['ink_x0']; x1=g[-1]['ink_x1']; off=CX-(x0+x1)/2
    base=top+cap_px+i*pitch
    gl=[dict(ch=q['ch'],pen_x=round(q['pen_x']+off,2),ink_x0=round(q['ink_x0']+off,2),ink_x1=round(q['ink_x1']+off,2)) for q in g]
    box=[round(x0+off,2),round(base-cap_px,2),round(x1-x0,2),round(cap_px,2)]
    out['lines'].append(dict(text=w,baseline_y=round(base,2),pen_x0=round(g[0]['pen_x']+off,2),
        ink_box=box,ink_box_note='[x,y,w,h]: cap-height box (no overshoot); letters have no descenders',
        css_top_px=round(base-asc,2),glyphs=gl))
    bx0=min(bx0,box[0]);by0=min(by0,box[1]);bx1=max(bx1,box[0]+box[2]);by1=max(by1,box[1]+box[3])
out['block_ink_box']=[round(bx0,2),round(by0,2),round(bx1-bx0,2),round(by1-by0,2)]
p=os.path.join(SH,'mograph/v001/name_layout.json')
json.dump(out,open(p,'w'),indent=1); print(json.dumps({k:out[k] for k in ['font','block_ink_box']},indent=1))
for l in out['lines']: print(l['text'],l['ink_box'],l['baseline_y'],l['pen_x0'],l['css_top_px'])
