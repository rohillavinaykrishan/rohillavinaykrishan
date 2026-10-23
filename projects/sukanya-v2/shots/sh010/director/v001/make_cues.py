import json
S0=116.30; FPS=25; N=450
mood=json.load(open('/home/user/rohillavinaykrishan/projects/sukanya-v2/source/client_music_mood.json'))
beats=[round((b-S0)*FPS) for b in mood['beats'] if S0-0.01<=b<S0+18.0]
beats=[b for b in beats if 0<=b<N]
# key music events (bed-relative frames), from director analysis (20 ms / 10 ms RMS + sub-band <120 Hz)
events={
 "hats_build_start":{"f":8,"src_s":116.62,"note":"hi-hat layer rises (+8 dB >4 kHz)"},
 "bass_thin":{"f":158,"src_s":122.62,"note":"sub band starts falling (45->35 dB)"},
 "bass_back":{"f":178,"src_s":123.40,"note":"bass returns briefly"},
 "fill_1":{"f":219,"src_s":125.06},"fill_2":{"f":224,"src_s":125.26},"fill_3":{"f":232,"src_s":125.56},"fill_4":{"f":238,"src_s":125.80},
 "bass_out":{"f":233,"f_end":253,"src_s":[125.6,126.4],"note":"sub band at 19-21 dB: the hole before the drop"},
 "riser":{"f":254,"src_s":126.48},
 "DROP":{"f":261,"src_s":126.74,"note":"sub band +33 dB in 0.3 s; loudest attack of the window. NAME POP + FIST CONTACT"},
 "audio_fade":{"f":425,"f_end":450}}
def sh(id,src_in,src_out,f_in,f_out,chars,crop,layer,notes=""):
    return dict(id=id,src_in=src_in,src_out=src_out,f_in=f_in,f_out=f_out,characters=chars,crop=crop,layer=layer,notes=notes)
FULL="1280:536:0:92"
shots=[
 sh("A01",38.29,39.62,0,42,["Dhalsim","Ken"],"960:536:160:92","roll_panel","lib sf032 (q4): Ken knocked down on the white arena floor, Dhalsim stance"),
 sh("A02",141.90,142.76,42,84,["unknown (aerial kick; lib sf124)"],"960:536:160:92","roll_panel","fighter id: librarian to confirm; flying kick through arena light shafts; 0.70 s source over 1.68 s = 42% (optical-flow slow-mo, establishing pace)"),
 sh("A03",62.00,62.90,84,105,["E. Honda"],"720:536:300:92","roll_panel","close-up stare, sauna; 2-beat hold"),
 sh("A04",109.45,110.45,105,126,["unknown (red-jacket fighter; lib sf097)"],FULL,"roll_panel","fighter vs silhouettes in light slats"),
 sh("A05",112.58,113.40,126,147,["Blanka"],"960:536:160:92","roll_panel","leaps over the cage, arms up"),
 sh("A06",135.90,136.80,147,168,["Ken","opponent (aerial)"],FULL,"roll_panel","arena light shafts, aerial clash"),
 sh("A07",40.92,41.55,168,188,["Ken"],"960:536:160:92","roll_panel","handstand flip in light shafts"),
 sh("A08",51.97,52.76,188,209,["Balrog","Ken"],"1280:536:0:92","roll_panel","lib sf046 (q4): Balrog stands over Ken knocked down, arena wide"),
 sh("A09",107.00,107.50,209,219,["unknown (psycho-power energy ball; lib sf093 q2)"],"960:536:160:92","roll_panel","violet energy ball - stays in palette"),
 sh("A10",123.70,123.90,219,224,["Chun-Li"],"960:536:160:92","roll_panel","lib sf111 (q4): Chun-Li screams in front of a fireball; half-beat flash"),
 sh("A11",130.30,130.62,224,232,["Ryu","Blanka"],"960:536:160:92","roll_panel","cage, purple spark"),
 sh("A12",95.45,95.70,232,238,["Guile"],"720:536:280:92","roll_panel","the flat-top glare"),
 sh("A13",121.30,121.50,238,243,["Cammy"],"720:536:280:92","roll_panel","braids, blue leotard (tritone)"),
 sh("C00",143.73,143.977,243,261,["Ryu","Ken"],"1280:536:0:92","charge","fists approach at ~33% speed (optical flow), drained to near-mono; CONTACT frame 143.977 lands on f261"),
 sh("B01",143.977,144.06,261,277,["Ryu","Ken"],"1280:536:0:92","super_band","fist contact, hold+ramp 100%->20% then freeze-frame tail; full colour (blue remapped to mulberry)"),
 sh("B02",50.10,50.65,277,289,["Balrog","Ken"],FULL,"super_band","low-angle uppercut"),
 sh("B03",139.75,140.25,289,300,["Blanka"],FULL,"super_band","electric dash"),
 sh("B04",113.55,114.00,300,310,["Vega? (red room backflip, librarian to confirm)"],FULL,"super_band","backflip"),
 sh("B05",123.00,123.45,310,320,["fighters in silhouette"],FULL,"super_band","explosion silhouettes - saffron firewall"),
 sh("B06",132.35,132.80,320,330,["Ken","Dhalsim"],FULL,"super_band","punch exchange, crowd"),
 sh("B07",101.36,101.81,330,340,["Cammy? (aerial flip over club crowd)"],FULL,"super_band","flip over the crowd; magenta/blue club light -> remap"),
 sh("B08",152.00,152.40,340,350,["Chun-Li"],FULL,"super_band","buns, turn to camera; band collapses into the title on f350"),
 sh("T01",None,None,350,450,["line-up art (assets_prev/lineup_restored_2160_r470.png)"],"full 2160 width, bottom-anchored","title","slow push 1.00->1.04, tritone + saffron rim"),
]
palette={"aubergine_ink":"#14080F","mulberry":"#4A1838","plum_mid":"#7A2E5C","saffron":"#FFB12A","ki_white":"#FFF3DC","chalk":"#D9CFC3","cinnabar_spark":"#FF5A1F"}
fonts={"roll":"Montserrat 500","name_hero":"Barlow Condensed 900 Italic","card_lines":"Barlow Condensed 600 (tracked 0.30em)","hud":"Chakra Petch 600"}
cues=dict(project="sukanya-v2",title="SUPER ART",fps=FPS,frames=N,duration_s=18.0,size="2160x3840",
 music=dict(file="source/client_music.mp3",src_in=S0,src_out=S0+18.0,bed="shots/sh010/director/v001/audio/bed_client_116.30-134.30.wav",bpm=136,frames_per_beat=11.03,key="D minor"),
 beats_f=beats,events=events,shots=shots,palette=palette,fonts=fonts,
 roll=dict(source="source/movie.mp4 63.5-66.0 s (720x1280)",row_pitch_src_px=23,scroll_src_px_s=117,gutter_x_src=361,
   scale_to_4k=3.0*1.35,row_pitch_4k=93,scroll_4k_px_per_frame=19.0,her_row="SHAHRUKH KHAN | SUKANYA DILIP DHARIYA",her_row_y_at_f243=1536))
json.dump(cues,open('/home/user/rohillavinaykrishan/projects/sukanya-v2/shots/sh010/director/v001/cues.json','w'),indent=1)
print(beats)
