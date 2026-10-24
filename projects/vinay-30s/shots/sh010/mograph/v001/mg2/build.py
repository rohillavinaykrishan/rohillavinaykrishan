"""MG2 build: template + cues.json + name_layout.json -> compositions/mg2.html, index.html (4K), proxy.html (540x960)."""
import json, os, sys
H=os.path.dirname(os.path.abspath(__file__)); SH=os.path.abspath(os.path.join(H,'../../..'))
cues=json.load(open(os.path.join(SH,'director/v001/cues.json')))
lay=json.load(open(os.path.join(SH,'mograph/v001/name_layout.json')))
fps=cues['fps']; ev=cues['events']; shots={s['id']:s for s in cues['shots']}
h0=shots['H0']; c6=shots['C6']; pal=cues['palette']
FEND=h0['f_out']-1
Q=dict(fps=fps, hit=ev['HIT']['f'], silence=ev['SILENCE']['f'], charge=[c6['f_in'], c6['f_out']-1], end=FEND,
       duration_s=(FEND+1)/fps, drawCharge=True,
       pal=dict(white=pal['White Hot'], gold=pal['Champion Gold'], goldDeep=pal['Gold Deep']),
       hues=list(pal['fighters'].values()))
win=cues['layout_4k']['act3_window']
# H0 plate: graded > ungraded > placeholder (assets/H0.mp4 is a symlink made here)
cands=[os.path.join(SH,'color/v001/plates/H0.mp4'), os.path.join(SH,'edit/v001/plates/H0.mp4')]
src='assets/H0_placeholder.mp4'
for c in cands:
    if os.path.exists(c):
        link=os.path.join(H,'assets/H0.mp4')
        if os.path.lexists(link): os.remove(link)
        os.symlink(os.path.relpath(c, os.path.join(H,'assets')), link); src='assets/H0.mp4'; break
lite=dict(name_centre=lay['name_centre'], font=dict(size_px=lay['font']['size_px']),
          lines=[dict(text=l['text'],baseline_y=l['baseline_y'],glyphs=[dict(ch=g['ch'],pen_x=g['pen_x']) for g in l['glyphs']]) for l in lay['lines']])
t=open(os.path.join(H,'src/mg2.template.html')).read()
rep={'__LAYOUT__':json.dumps(lite),'__CUES__':json.dumps(Q),'__WIN_X__':str(win[0]),'__WIN_Y__':str(win[1]),'__WIN_W__':str(win[2]),'__WIN_H__':str(win[3]),
     '__H0_START__':f"{h0['f_in']/fps:.4f}",'__H0_DUR__':f"{h0['frames']/fps:.4f}",'__H0_SRC__':src}
rep['__KIT__']=open(os.path.join(SH,'mograph/v001/kit/kit.js')).read()
for k,v in rep.items(): t=t.replace(k,v)
os.makedirs(os.path.join(H,'compositions'),exist_ok=True)
open(os.path.join(H,'compositions/mg2.html'),'w').write(t)
def root(w,h,name):
    return f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={w}, height={h}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {w}px; height: {h}px; overflow: hidden; background: transparent; }}
    </style>
  </head>
  <body>
    <!-- MG2 SPECTRUM STRIKE, {name}. Root clock = master seconds; f0-f335 transparent, content f336-f{FEND}. -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{Q['duration_s']:.2f}" data-fps="{fps}" data-width="{w}" data-height="{h}">
      <div id="mg2" data-composition-id="mg2" data-composition-src="compositions/mg2.html" data-start="0" data-duration="{Q['duration_s']:.2f}" data-track-index="1" data-track-kind="graphics" data-width="{w}" data-height="{h}"></div>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
'''
open(os.path.join(H,'index.html'),'w').write(root(2160,3840,'4K master'))
P=os.path.join(H,'proxy'); os.makedirs(P,exist_ok=True)
open(os.path.join(P,'index.html'),'w').write(root(540,960,'540x960 proxy (renders the same compositions/mg2.html)'))
for d in ('assets','compositions'):
    l=os.path.join(P,d)
    if not os.path.lexists(l): os.symlink('../'+d,l)
import shutil; shutil.copy(os.path.join(H,'hyperframes.json'),P); shutil.copy(os.path.join(H,'package.json'),P)
print('built; H0 src =',src, Q)
