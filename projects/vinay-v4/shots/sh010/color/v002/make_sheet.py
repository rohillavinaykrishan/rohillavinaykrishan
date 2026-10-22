import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont
F = "../../director/v001/fonts/JetBrainsMono-600.ttf"
f = ImageFont.truetype(F, 26); fs = ImageFont.truetype(F, 20)
INK = (0x12, 0x10, 0x0D); BONE = (0xF2, 0xEB, 0xDF); SAND = (0xCD, 0xB0, 0x8A)
Wl = np.array([.2126, .7152, .0722])
cols = [("SOURCE", "../v001/plate_src"), ("v001", "../v001/plate_graded"), ("v002", "plate_graded")]
w, h = 960, 402
W = 40 + 3 * (w + 40); rows = [0, 25, 51]
H = 90 + 3 * (h + 60) + 40 + 640 + 40
S = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(S)
d.text((40, 30), "sh010 colour v002 (note 13): source | v001 | v002   sat 1.00, greens 0.85 / shift 50%, skin+red 1.08, toe 0.10->0.07, mid-slope 1.08", font=fs, fill=BONE)
y = 90
for i in rows:
    ys = None
    for k, (name, p) in enumerate(cols):
        im = Image.open(f"{p}/plate.{i:04d}.png").convert("RGB"); A = np.asarray(im, float)
        Y = (A @ Wl).mean(); m = A.reshape(-1, 3).mean(0); ys = ys or Y
        x = 40 + k * (w + 40)
        S.paste(im.resize((w, h), Image.LANCZOS), (x, y + 34))
        lab = f"s{i:02d} {name}  Y {Y:.1f}" + ("" if k == 0 else f" ({(Y/ys-1)*100:+.1f}%)  RGB {m[0]:.0f}/{m[1]:.0f}/{m[2]:.0f} {'B<=G<=R OK' if m[2]<=m[1]<=m[0] else 'FAIL'}")
        d.text((x, y + 6), lab, font=fs, fill=SAND)
    y += h + 60
y += 20
d.text((40, y), "CREDITS 69.20 s (note 14): source | v001 Ink/Bone | v002 Umber #2A211A / Bone, text Y>=220 100%", font=fs, fill=SAND)
for k, p in enumerate(["qc/crsrc_1.8.png", "../v001/qc/credits_g_69.png", "qc/cr_1.8.png"]):
    S.paste(Image.open(p).convert("RGB").resize((338, 600), Image.LANCZOS), (40 + k * 378, y + 34))
S.save(sys.argv[1]); print(S.size)
