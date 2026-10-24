#!/usr/bin/env python3
"""MG4 title card (master f350-449) asset build. Re-run any time.
  assets/lineup.png   assets_prev/lineup_restored_2160_r470.png -> Colorist's title_lineup() tritone + Saffron rim light (alpha kept)
  assets/logo.png     assets_prev/sf_logo_alpha.png -> Colorist's logo_gold() map (burnt saffron -> Saffron -> Ki White) + 6% bloom
  assets/band_B08.png last frame of the band plate B08 (graded) for the collapse f350-355
  assets/echo_u.jpg / echo_d.jpg  the echo-band afterimages of B07 at f349 (copied from MG3's sync)
The Colorist's make_luts.py is imported read-only; nothing is written outside mg4_title/.
"""
import os, sys, subprocess, importlib.util, shutil
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
MG = os.path.dirname(HERE)
PROJ = os.path.abspath(os.path.join(MG, "../../../../.."))
SH = os.path.join(PROJ, "shots/sh010")
A = os.path.join(MG, "assets")
spec = importlib.util.spec_from_file_location("colorist_luts", os.path.join(SH, "color/v001/make_luts.py"))
CL = importlib.util.module_from_spec(spec); spec.loader.exec_module(CL)
SAF = np.array([255, 177, 42]) / 255.0


def graded(img, fn):
    a = np.asarray(img.convert("RGBA")).astype(np.float64) / 255
    rgb = fn(a[..., :3].reshape(-1, 3)).reshape(a.shape[0], a.shape[1], 3)
    return np.clip(rgb, 0, 1), a[..., 3]


# line-up + logo: the Colorist's finished title assets (graded line-up, gold logo with alpha) are used as-is
for src, dst in (("color/v001/title/lineup_tritone.png", "lineup.png"), ("color/v001/title/sf_logo_gold.png", "logo.png")):
    shutil.copy(os.path.join(SH, src), os.path.join(A, dst))

# collapse sources (from MG3's synced assets: same grade as the band chain)
MG3 = os.path.join(os.path.dirname(MG), "mg3_band/assets")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-sseof", "-0.04", "-i", os.path.join(MG3, "plates/B08.mp4"),
                "-frames:v", "1", "-update", "1", os.path.join(A, "band_B08.png")], check=True)
Image.open(os.path.join(A, "band_B08.png")).convert("RGB").save(os.path.join(A, "band_B08.jpg"), quality=92)
os.remove(os.path.join(A, "band_B08.png"))
shutil.copy(os.path.join(MG3, "echo/B07.jpg"), os.path.join(A, "echo_u.jpg"))
shutil.copy(os.path.join(MG3, "echo/B07_mid.jpg"), os.path.join(A, "echo_d.jpg"))
print("ok")
