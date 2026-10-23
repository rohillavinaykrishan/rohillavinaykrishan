# Regenerates cues.json (the single timing source). Edit the tables here, never cues.json by hand.
# usage: python3 make_cues.py   (run from this folder)
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = "/home/user/rohillavinaykrishan/library/streetfighter-trailer/shots.json"
lib = {s["id"]: s for s in json.load(open(LIB))["shots"]}
FPS = 25; N = 750

HUES = {  # fighter colour code (hex) - the roster spectrum, in wheel order
 "Ryu": ("HADOU CRIMSON", "#E3203A"), "Ken": ("SHORYU ORANGE", "#FF5E1A"), "Dhalsim": ("YOGA AMBER", "#FFA21C"),
 "Blanka": ("VOLT LIME", "#9BEA2E"), "Guile": ("SONIC TEAL", "#17C9A6"), "Chun-Li": ("KIKOKEN BLUE", "#2F6DFF"),
 "M. Bison": ("PSYCHO VIOLET", "#8B3DFF"), "E. Honda": ("SUMO MAGENTA", "#FF2D8F")}

def crop(sid, w, scale_note=""):
    s = lib[sid]; cx = s["best_vertical_crop_cx"] * 1280
    x = int(round(min(max(cx - w / 2, 0), 1280 - w) / 2) * 2)
    return f"{w}:536:{x}:92"

# id, layer, f_in, f_out(excl), lib id, src_in, speed, crop_w, characters, grade, note
SHOTS = [
 # ACT 1 ROSTER - window 2160x904 (full 1280x536 active, x1.6875), duotone per fighter
 ("R1","roster",19,46,"sf125",142.80,0.833,1280,["Ryu"],"duo:Ryu","raises fist, blue light"),
 ("R2","roster",46,71,"sf117",133.25,1.0,1280,["Ken"],"duo:Ken","yells as he charges, light shafts"),
 ("R3","roster",71,96,"sf032",38.30,1.0,1280,["Dhalsim"],"duo:Dhalsim","fighting stance, arena (tilt)"),
 ("R4","roster",96,121,"sf100",112.58,0.9,1280,["Blanka"],"duo:Blanka","roars, arms raised (pan)"),
 ("R5","roster",121,145,"sf082",95.02,0.95,1280,["Guile"],"duo:Guile","flat-top stare into camera"),
 ("R6","roster",145,171,"sf135",151.90,1.0,1280,["Chun-Li"],"duo:Chun-Li","blue qipao, bloodied, glares"),
 ("R7","roster",171,197,"sf107",119.60,0.65,1280,["M. Bison"],"duo:M. Bison","red uniform, peaked cap; 0.65x = frame-blend, not mci"),
 ("R8","roster",197,223,"sf053",62.00,0.95,1280,["E. Honda"],"duo:E. Honda","sumo topknot glare (picture only)"),
 # ACT 2 CLASH - window 2160x1206 (960x536 crop, x2.25), TRUE COLOUR grade
 ("C1","clash",237,263,"sf110",122.93,0.70,960,["fighters (silhouettes)"],"true","silhouettes vs explosion; lands on the S2 entry hit"),
 ("C2","clash",263,280,"sf046",52.00,1.0,960,["Balrog","Ken"],"true","Balrog stands over a downed Ken"),
 ("C3","clash",280,298,"sf116",131.90,1.0,960,["Ken","Dhalsim"],"true","Ken squares up to Dhalsim"),
 ("C4","clash",298,316,"sf121",138.40,1.0,960,["Ken","Ryu"],"true","Ken and Ryu side by side, stances"),
 ("C5","clash",316,336,"sf119",135.90,1.0,960,["Ken"],"true","jump kick, arena wide"),
 ("C6","clash",336,357,"sf033",39.65,0.60,960,["Dhalsim"],"true>drain","lunge; ramp 1.0 -> 0.2 (avg 0.6) under 'I'm a street fighter', drains to mono by f356"),
 # ACT 3 STRIKE - window 2160x904 (full), TRUE COLOUR
 ("H0","strike",365,387,"sf045",50.75,0.30,1280,["Balrog","Ken"],"true","GLOVE CONTACT FRAME = f365 (editor frame-steps 50.05-51.97 and sets src_in; proof PNG). 0.30x after contact"),
 ("F1","strike",387,398,"sf130",146.15,1.0,1280,["unknown (red spin kick)"],"true","upside-down spin kick, crowd"),
 ("F2","strike",398,409,"sf128",144.86,1.0,1280,["Blanka"],"true","swats a man in an orange jumpsuit"),
 ("F3","strike",409,420,"sf109",121.40,1.0,1280,["Cammy"],"true","fires rotary weapon, muzzle flash"),
 ("F4","strike",420,430,"sf095",108.16,1.0,1280,["Chun-Li"],"true","slash, blade across frame"),
 ("F5","strike",430,441,"sf122",139.76,1.0,1280,["Blanka"],"true","leaps across the warehouse"),
 ("F6","strike",441,451,"sf084",97.40,1.0,1280,["Cammy"],"true","strides down a neon street"),
 ("F7","strike",451,463,"sf131",147.00,1.0,1280,["unknown (handstand)"],"true","handstand in light shafts"),
 ("F8","strike",463,474,"sf120",137.30,1.0,1280,["Ken","Ryu"],"true","back to back, warehouse"),
 ("F9","strike",474,485,"sf123",140.80,1.0,1280,["unknown"],"true","fighter on the arena floor after a hit"),
]
# ACT 4 ROSTER WALL tiles: 482x430 at 4K from a 600x536 crop (downscale = crisp). Clip plays slow then holds its last frame.
TILES = [  # id, char, lib id, src_in, arrive f, slot (row,col)
 ("T1","Ryu","sf125",142.95,494,(0,0)), ("T2","Ken","sf031",37.52,512,(0,1)), ("T3","Dhalsim","sf032",38.70,529,(0,2)),
 ("T4","Blanka","sf100",112.70,547,(0,3)), ("T5","Guile","sf082",95.20,564,(1,0)), ("T6","Chun-Li","sf135",152.40,582,(1,1)),
 ("T7","M. Bison","sf107",119.60,599,(1,2)), ("T8","E. Honda","sf053",62.30,616,(1,3))]
TILE_CLIP_F, TILE_SPEED = 40, 0.4   # 40 master frames at 0.4x = 0.64 s of source, then freeze

def src_out(sid, a, n, sp):
    b = round(a + n / FPS * sp, 3); s = lib[sid]
    assert s["in"] - 1e-3 <= a and b <= s["out"] + 1e-3, (sid, a, b, s["in"], s["out"])
    return b

shots = []
for (i, layer, fi, fo, sid, a, sp, cw, ch, gr, note) in SHOTS:
    n = fo - fi
    shots.append({"id": i, "layer": layer, "f_in": fi, "f_out": fo, "frames": n, "lib": sid, "src_in": a,
                  "src_out": src_out(sid, a, n, sp), "speed": sp, "crop": crop(sid, cw), "characters": ch,
                  "grade": gr, "hue": HUES[ch[0]][1] if gr.startswith("duo") else None, "note": note,
                  "lib_quality": lib[sid]["quality"]})
tiles = []
for (i, c, sid, a, f, slot) in TILES:
    x0 = 80 + slot[1] * (482 + 24); y0 = 2300 + slot[0] * (430 + 24)
    tiles.append({"id": i, "character": c, "hue": HUES[c][1], "hue_name": HUES[c][0], "lib": sid, "src_in": a,
                  "src_out": src_out(sid, a, TILE_CLIP_F, TILE_SPEED), "speed": TILE_SPEED, "clip_frames": TILE_CLIP_F,
                  "arrive_f": f, "freeze_from_f": f + TILE_CLIP_F, "crop": crop(sid, 600), "rect_4k": [x0, y0, 482, 430]})

beats = {
 "S1_117.5bpm_12.77f": [6,19,33,46,59,71,84,96,109,121,134,145,158,171,183,197,210,223,236],
 "S2_86.1bpm_17.4f": [237,245,263,280,298,316,336],
 "S3_136bpm_11.03f": [365,376,387,398,409,420,430,441,451,463,474],
 "S4_172.3bpm_8.7f": [486,494,503,512,521,529,538,547,555,564,573,582,590,599,608,616,625,634,643,651,660,669,677,686,695,703,712,721,730,738]}

cues = {
 "project": "vinay-30s", "title": "SPECTRUM", "fps": FPS, "frames": N, "duration_s": 30.0, "size": "2160x3840",
 "deliver": "deliver/Vinay_Krishan_Rohilla_StreetFighter_SrMatchmove_30s_4K.mp4",
 "music": {"source": "source/trailer.mp4 (audio)", "bed": "shots/sh010/director/v001/audio/bed_vinay30_v001.wav",
   "builder": "shots/sh010/director/v001/audio/make_bed.py", "segments": json.load(open(os.path.join(HERE, "audio/bed_segments.json"))),
   "splices": "6 ms equal-power crossfades; in-points ~15 ms before the onset; 4 ms head fade; 0.6 s equal-power tail fade",
   "whisper_vad_off": ["audio/whisper_bed_vadoff.json", "audio/whisper_bed_strict_small.json", "audio/whisper_bed_strict_medium.json"]},
 "beats_f": beats,
 "events": {
   "cold_open": {"f": [0, 18]},
   "S2_entry_hit": {"f": 237, "src_s": 122.84, "note": "splice S1->S2 lands on the explosion hit (+15 dB)"},
   "lyric_im_a_street_fighter": {"f": [320, 356], "src_s": [126.16, 127.58], "note": "sung line; the charge"},
   "SILENCE": {"f": [357, 364], "src_s": [104.88, 105.20], "note": "-43 dBFS: the only still moment"},
   "HIT": {"f": 365, "src_s": 105.21, "note": "biggest hit of the trailer (onset 14.594 s in the bed). NAME STRIKE + GLOVE CONTACT"},
   "role_line_in": {"f": 387}, "split_to_wall": {"f": 485, "note": "S3->S4 splice, chant begins"},
   "TITLE_STINGER": {"f": 686, "src_s": 153.97, "note": "SF title-card hit: logo slam + roster unlock to true colour"},
   "tail_fade": {"f": [735, 749]}},
 "layout_4k": {"safe": {"top": 420, "bottom_critical_text": 3140},
   "act1_window": [0, 1048, 2160, 904], "act2_window": [0, 897, 2160, 1206], "act3_window": [0, 2280, 2160, 904],
   "name_block": [0, 1150, 2160, 800], "role_lines_y": [2030, 2160], "logo_box": [380, 420, 1400, 600],
   "wall_rect": [80, 2300, 2000, 884]},
 "shots": shots, "tiles": tiles,
 "palette": {"Ink": "#07060A", "Ink Raised": "#13111A", "Smoke": "#2B2632", "White Hot": "#FFF8EC", "Bone": "#E6DED2",
   "Champion Gold": "#FFC94D", "Gold Deep": "#C7851E", "fighters": {k: v[1] for k, v in HUES.items()}},
 "fonts": {"name": "Unbounded 900", "role": "Unbounded 500", "hud": "Space Mono 700", "dir": "shots/sh010/director/v001/fonts/"},
}
json.dump(cues, open(os.path.join(HERE, "cues.json"), "w"), indent=1)
print("shots", len(shots), "tiles", len(tiles), "frames covered by plates/graphics ok")
for s in shots: print(s["id"], s["f_in"], s["f_out"], s["lib"], s["src_in"], s["src_out"], s["crop"], s["characters"])
for t in tiles: print(t["id"], t["character"], t["lib"], t["src_in"], t["src_out"], t["crop"], t["rect_4k"])
