import json, sys, numpy as np
sys.path.insert(0,sys.argv[1]); S=sys.argv[1]; L=sys.argv[2]
from notes import N, CX, HERO, QFIX, MOVEFIX, SOLVFIX
FPS=24000/1001
sh=json.load(open(S+'/shots_raw.json')); cx=json.load(open(S+'/cx.json'))
pf=np.load(S+'/perframe.npy')
lq=np.log([s['lap'] for s in sh]); lq_p=lambda v:(lq<v).mean()
def camera(s,dur):
    i0,i1=s['i0'],s['i1']; m=pf[i0+1:i1+1]
    if len(m)==0: return 'locked'
    mag=m[:,8]; dx=m[:,5]; dy=m[:,6]
    fast=(mag>8).sum()
    ndx,ndy=abs(dx.sum()),abs(dy.sum()); travel=max(ndx,ndy)
    if fast>=2 and fast< 0.5*len(m) and mag.max()>10: return 'whip'
    if np.median(mag)<0.15 and travel<6: return 'locked'
    if travel>=12 and np.median(np.abs(dx if ndx>=ndy else dy))>0.25:
        return 'pan' if ndx>=ndy else 'tilt'
    if s['res']>0.45 and np.median(mag)>0.4 and travel<12: 
        # motion without net translation: zoom/dolly or subject motion or shake
        jit=np.std(np.diff(dx))+np.std(np.diff(dy))
        return 'handheld' if jit>0.4 else 'dolly'
    if np.median(mag)<0.4: 
        jit=np.std(np.diff(dx))+np.std(np.diff(dy))
        return 'handheld' if jit>0.25 else 'locked'
    return 'handheld'
out=[]
for k,s in enumerate(sh):
    n=k+1; sid='sf%03d'%n; i0,i1=s['i0'],s['i1']; dur=(i1-i0+1)/FPS
    chars,action=N[n]
    cam=MOVEFIX.get(n,camera(s,dur))
    travel=max(abs(s['net_dx']),abs(s['net_dy']))
    solv=bool(cam in('pan','tilt','dolly','handheld','whip') and s['res']>=0.35 and s['mag']>=0.6 and travel>=10 and dur>=0.9 and s['luma']>35 and s['blk']<3.0)
    if n==112: solv=True
    solv=SOLVFIX.get(n,solv)
    # quality: sharpness percentile minus blocking & darkness penalties
    q=1+4*lq_p(np.log(s['lap']))
    if s['blk']>2.5: q-=0.7
    if s['blk']>4: q-=0.8
    if s['luma']<25: q-=0.6
    q=int(min(5,max(1,round(q))))
    q=QFIX.get(n,q)
    c=CX.get(n,cx[sid]['cx']); c=float(min(0.882,max(0.118,c)))
    e=dict(id=sid,
      **{'in':round(i0/FPS,3),'out':round((i1+1)/FPS,3)},
      in_frame=i0,out_frame=i1,frames=i1-i0+1,duration=round(dur,3),
      characters=chars,action=action,
      camera=dict(move=cam,solvable=solv,flow_px_per_frame=round(s['mag'],2),parallax_residual=round(s['res'],2),net_travel_px=round(travel,1)),
      mean_rgb=[round(v) for v in s['mean_rgb']],dominant_hue=s['hue'],dominant_hue_deg=s['hue_deg'],blue_cast=s['blue'],
      best_vertical_crop_cx=round(c,3),best_vertical_crop_x_px=int(round(c*1280-150.75)),
      crop_cx_source=('by_eye' if n in CX else cx[sid]['src']),
      quality=q,sharpness_lapvar=round(s['lap']),blockiness=round(s['blk'],2),mean_luma=round(s['luma']),
      hero=n in HERO,still=f'stills/{sid}.jpg',still_frame=s['still_frame'])
    out.append(e)
# shot-level overrides from the brief
for e in out:
    if e['id']=='sf112': e['camera']['note']='continuous oner; calm, COLMAP-solvable part is 124.37-126.54 (frames 2982-3034), whip-like follows after ~126.1'
doc=dict(source='projects/sukanya-v2/source/trailer.mp4',fps='24000/1001',frames=4046,duration=168.752,
  active_picture='crop=1280:536:0:92',coords='times in seconds (in inclusive, out exclusive); frames 0-based source frames, out_frame inclusive; crop cx is 0-1 across the 1280-wide active picture; crop_x_px is the left edge of a 301.5x536 (9:16) window in active-picture pixels',
  method='ffmpeg scene score + histogram and normalised pixel-difference peaks, every cut checked by eye on frame pairs; 12 false cuts (flashes, whip, title animation) removed',
  shots=out)
json.dump(doc,open(L+'/shots.json','w'),indent=1)
from collections import Counter
print(Counter(e['camera']['move'] for e in out)); print('solvable',[e['id'] for e in out if e['camera']['solvable']]); print(Counter(e['quality'] for e in out))
for e in out: print(e['id'],e['camera']['move'],e['quality'],e['dominant_hue'],end=' | ')
