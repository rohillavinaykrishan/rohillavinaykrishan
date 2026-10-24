import json,sys
L=sys.argv[1]; d=json.load(open(L+'/shots.json')); a=json.load(open(L+'/audio_map.json'))
for e in d['shots']:
    e['audio']=[dict(label=s['label'],text=s['text'],start=s['start'],end=s['end']) for s in a['speech_spans'] if s['start']<e['out'] and s['end']>e['in']]
    e['in_clean_music_window']=any(w['start']<=e['in'] and w['end']>=e['out'] for w in a['clean_music_windows'])
json.dump(d,open(L+'/shots.json','w'),indent=1)
print(sum(e['in_clean_music_window'] for e in d['shots']))
