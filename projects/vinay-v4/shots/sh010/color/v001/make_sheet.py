import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont
F = "../../director/v001/fonts/JetBrainsMono-600.ttf"
f = ImageFont.truetype(F, 26); fs = ImageFont.truetype(F, 20)
INK = (0x12, 0x10, 0x0D); BONE = (0xF2, 0xEB, 0xDF); SAND = (0xCD, 0xB0, 0x8A); PINK = (0xFF, 0x2E, 0x88)
W = 3 * 40 + 2 * 1280
rows = [0, 25, 51]
H = 90 + 3 * (536 + 60) + 40 + 900 + 40
S = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(S)
d.text((40, 30), "sh010 colour v001  SUN-BLEACHED  |  left: source  right: sunbleach.cube + grain", font=f, fill=BONE)
Wl = np.array([.2126, .7152, .0722]); y = 90
for i in rows:
    a = Image.open(f"plate_src/plate.{i:04d}.png").convert("RGB"); b = Image.open(f"plate_graded/plate.{i:04d}.png").convert("RGB")
    A = np.asarray(a, float); B = np.asarray(b, float)
    ya, yb = (A @ Wl).mean(), (B @ Wl).mean(); m = B.reshape(-1, 3).mean(0)
    S.paste(a, (40, y + 40)); S.paste(b, (80 + 1280, y + 40))
    d.text((40, y + 6), f"s{i:02d} SOURCE  Y {ya:.1f}", font=fs, fill=SAND)
    d.text((80 + 1280, y + 6), f"s{i:02d} GRADED  Y {yb:.1f} ({(yb/ya-1)*100:+.1f}%)  RGB {m[0]:.0f}/{m[1]:.0f}/{m[2]:.0f}  B<=G<=R {'OK' if m[2]<=m[1]<=m[0] else 'FAIL'}", font=fs, fill=SAND)
    y += 536 + 60
y += 20
cs = Image.open("qc/credits_src_69.png").convert("RGB").resize((450, 800), Image.LANCZOS)
cg = Image.open("qc/credits_g_69.png").convert("RGB").resize((450, 800), Image.LANCZOS)
d.text((40, y), "CREDITS 69.20s  source | Ink/Bone duotone", font=fs, fill=SAND)
S.paste(cs, (40, y + 40)); S.paste(cg, (530, y + 40))
logo = Image.open("sf_logo_bone.png"); lw = 1500; lg = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
d.text((1060, y), "sf_logo_bone.png (2160 px) over Ink | over Sand", font=fs, fill=SAND)
bg1 = Image.new("RGB", (lw, lg.height // 2 + 20), INK); bg2 = Image.new("RGB", (lw, lg.height // 2 + 20), SAND)
half = lg.resize((lw // 2, lg.height // 2), Image.LANCZOS)
bg1.paste(half, (0, 10), half); bg2.paste(half, (0, 10), half)
S.paste(bg1.crop((0, 0, lw // 2 + 20, bg1.height)), (1060, y + 40)); S.paste(bg2.crop((0, 0, lw // 2 + 20, bg2.height)), (1060 + lw // 2 + 40, y + 40))
sw_y = y + 40 + bg1.height + 40
for k, (n, c) in enumerate([("Ink", INK), ("Umber", (0x3A, 0x2E, 0x24)), ("Sand", SAND), ("Bone", BONE), ("Sage", (0x7D, 0x87, 0x5C)), ("Pink", PINK)]):
    d.rectangle([1060 + k * 200, sw_y, 1060 + k * 200 + 180, sw_y + 120], fill=c, outline=BONE if n == "Ink" else None)
    d.text((1060 + k * 200, sw_y + 130), n, font=fs, fill=BONE)
S.save(sys.argv[1]); print(S.size)
