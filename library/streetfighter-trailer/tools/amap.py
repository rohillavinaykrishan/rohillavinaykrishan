import json, sys
S,L=sys.argv[1],sys.argv[2]
wh=json.load(open(S+'/whisper_novad.json'))['segments']; gm=json.load(open(S+'/gaps_medium.json'))
pitch={(p['start'],p['end']):p for p in json.load(open(S+'/pitch.json'))}
shots=json.load(open(L+'/shots.json'))['shots']; mus=json.load(open(S+'/music.json'))
def tight(s):
    w=s['words']
    st=s['start']
    if len(w)>1 and w[0]['end']-w[0]['start']>0.5: st=round(max(st,w[0]['end']-0.45),2)
    return st
spans=[]
def add(st,en,text,label,conf,src,note=None,pkey=None):
    e=dict(start=st,end=en,text=text,label=label,confidence=conf,source=src)
    if note: e['note']=note
    p=pitch.get(pkey)
    if p: e['pitch_metrics']={k:p[k] for k in ('voiced_frac','stable_frac','longest_note_s','pitch_range_st')}
    e['shots']=[x['id'] for x in shots if x['in']<en and x['out']>st]
    spans.append(e)
UNCERT={131.62,77.98}
for s in wh:
    if s['start'] in UNCERT: continue
    t=s['text']; st=tight(s); en=s['end']; note=None; conf='high' if s['avg_logprob']>-0.6 else 'medium'
    if abs(s['start']-117.0)<0.1: st,en,conf,note=117.37,118.46,'high','times from the brief (Whisper 117.0-118.5)'
    if abs(s['start']-156.5)<0.1: note="'Kyle' is a low-probability word (p=0.14); may be a name such as 'Guile' - not verified. Brief puts 'You did that' at ~157.3"
    if abs(s['start']-138.48)<0.1: note="Whisper heard 'To live has to fight' (low word probs); likely 'To live is to fight', mirrored by the next line"
    if abs(s['start']-42.06)<0.1: note="probably 'I spent years living in Ryu's shadow'"
    if abs(s['start']-163.92)<0.1: conf,note='medium','not in the earlier VAD-on transcript; end-card area, unverified'
    if abs(s['start']-99.4)<0.1: note="text uncertain ('free fighting' may be 'street fighting')"
    add(st,en,t,'dialogue',conf,'whisper-small VAD off, full pass',note,(s['start'],s['end']))
# vocals recovered from targeted gap passes / brief
add(79.06,81.42,"I won't deny it, I'ma show you",'sung','medium','whisper-medium gap pass','rap lyric over the music bed; full pass heard "I won\'t deny a machine" 77.98-81.2',(79.06,81.42))
add(84.3,87.0,"Ain't no stopping me",'sung','medium','whisper-medium gap pass (also small)','rap lyric; first word stretched, vocal likely starts ~85.5',(84.3,87.0))
add(112.1,116.1,"(rap hook - words unclear)",'sung','high (span from brief)','brief; Whisper small heard "I\'m gonna make it down the chain... no no no" (low confidence)',None,(112.1,116.1))
add(121.0,122.46,"It might sting a little",'dialogue','high (from brief)','brief; Whisper medium heard "It\'s nice to be a little..." 120.96-122.56','Cammy (sf109)',(121.0,122.46))
add(126.16,127.58,"I'm a street fighter",'sung','medium','brief start 126.16; Whisper medium 126.32-127.58','shouted/rapped title lyric in the music; treat as part of the song, not a character line',(126.16,127.58))
add(144.0,153.92,"(chanted count - 'five, four, three, two, one' / 'one, two, three, four')",'sung','low','whisper medium + small gap passes disagree','rhythmic chant in the track; words not reliable',(144.0,153.92))
spans.sort(key=lambda e:e['start'])
uncertain=[dict(start=131.62,end=132.26,text='No.',note='word p=0.03, probably not speech'),
           dict(start=135.5,end=137.42,text='Or you can!',note='medium only, first word p=0.05'),
           dict(start=58.3,end=58.48,text='Fight.',note='small gap pass only'),
           dict(start=63.5,end=63.66,text='Come on!',note='small gap pass only')]
# clean music windows: >=10 s with no dialogue
dlg=sorted([(e['start'],e['end']) for e in spans if e['label']=='dialogue'])
gaps=[];prev=0.0
for a,b in dlg+[(168.75,168.75)]:
    if a-prev>=10: gaps.append((prev,a))
    prev=max(prev,b)
cmw=[]
for a,b in gaps:
    a2,b2=round(a+0.15,2),round(b-0.15,2)
    sung=[(e['start'],e['end'],e['text']) for e in spans if e['label']=='sung' and e['start']<b2 and e['end']>a2]
    cmw.append(dict(start=a2,end=b2,duration=round(b2-a2,2),contains_sung=[dict(start=x,end=y,text=t) for x,y,t in sung],
        shots=[x['id'] for x in shots if x['in']<b2 and x['out']>a2]))
voc=sorted([(e['start'],e['end']) for e in spans])
inst=[];prev=0.0
for a,b in voc+[(168.75,168.75)]:
    if a-prev>=5: inst.append(dict(start=round(prev+0.15,2),end=round(a-0.15,2),duration=round(a-prev-0.3,2)))
    prev=max(prev,b)
doc=dict(source='projects/sukanya-v2/source/trailer.mp4',duration=mus['duration'],
  method=dict(asr='faster-whisper small, int8 CPU, vad_filter=False, word timestamps; gaps re-run as short clips with small and medium (VAD off)',
    labels='dialogue = spoken character line; sung = rapped/sung vocal in the music track. Labels set by content and the brief; pYIN pitch metrics measured on the full mix are attached for reference but are NOT reliable under the music bed',
    start_fix='where Whisper stretched the first word over >0.5 s, start = first word end - 0.45 s'),
  speech_spans=spans, uncertain_vocals=uncertain,
  clean_music_windows=cmw, instrumental_windows_no_vocals=inst,
  music=dict(sections=mus['sections'],loudest_hits=mus['loudest_hits'],silences_below_40dBFS=mus['silences'],
    onsets=mus['onsets'],rms_curve_0p5s_dbfs=mus['rms_curve_0p5s'],
    note='sections from MFCC+chroma novelty (about 4-8 s each); trailer music is a cut-up bed, so tempo per section is approximate'),
  known_facts_from_brief=dict(you_lose=[117.37,118.46],cammy_it_might_sting_a_little=[121.0,122.46],sung_rap_hook=[112.1,116.1],im_a_street_fighter_from=126.16,you_did_that='~157.3'))
json.dump(doc,open(L+'/audio_map.json','w'),indent=1)
for e in spans: print(e['start'],e['end'],e['label'],e['confidence'][:6],e['text'][:50],e['shots'])
print('CMW',[(c['start'],c['end'],c['duration']) for c in cmw]); print('INST',inst)
