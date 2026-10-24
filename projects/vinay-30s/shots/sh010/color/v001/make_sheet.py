#!/usr/bin/env python3
"""Grade test sheet: ungraded | graded (mid frame) per plate, plus the C6 drain ramp. make_sheet.py SRC_DIR GRADED_DIR OUT.png [IDs]"""
import os, subprocess, sys, io
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = ImageFont.truetype(os.path.join(HERE, "../../director/v001/fonts/SpaceMono-700.ttf"), 18)
H = 180
def grab(f, idx):
    n = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
    i = {"mid": n // 2, "first": 0, "last": n - 1}.get(idx, idx)
    png = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-vf", f"select=eq(n\\,{i}),scale=-2:{H}:in_color_matrix=bt709:flags=lanczos,format=rgb24", "-frames:v", "1", "-f", "image2pipe", "-c:v", "png", "-"], capture_output=True).stdout
    return Image.open(io.BytesIO(png)).convert("RGB")
def label(im, t):
    d = ImageDraw.Draw(im); d.rectangle([0, 0, len(t) * 11 + 8, 24], fill=(7, 6, 10)); d.text((4, 1), t, font=FONT, fill=(255, 248, 236)); return im
src, gdir, out = sys.argv[1:4]; ids = sys.argv[4:]
cells = []
for i in ids:
    for suffix in ([""] if not i.startswith("T") else ["_duo", "_true"]):
        g = os.path.join(gdir, i + suffix + ".mp4")
        if not os.path.exists(g): continue
        a = label(grab(os.path.join(src, i + ".mp4"), "mid"), f"{i} src"); b = label(grab(g, "mid"), f"{i}{suffix or ''} graded")
        c = Image.new("RGB", (a.width + b.width + 4, H), (19, 17, 26)); c.paste(a, (0, 0)); c.paste(b, (a.width + 4, 0)); cells.append(c)
if os.path.exists(os.path.join(gdir, "C6.mp4")):
    fr = [label(grab(os.path.join(gdir, "C6.mp4"), k), f"C6 drain {k}") for k in ("first", "mid", "last")]
    c = Image.new("RGB", (sum(f.width for f in fr) + 8, H), (19, 17, 26)); x = 0
    for f in fr: c.paste(f, (x, 0)); x += f.width + 4
    cells.append(c)
cols = 2; W = max(c.width for c in cells); rows = (len(cells) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (W + 10) + 10, rows * (H + 10) + 10), (7, 6, 10))
for k, c in enumerate(cells): sheet.paste(c, (10 + (k % cols) * (W + 10), 10 + (k // cols) * (H + 10)))
sheet.save(out); print(out, sheet.size)
