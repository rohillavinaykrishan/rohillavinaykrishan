"""v2: trailer action montage opener, then the credit reveal.

0.0-4.3  trailer fight montage (vertical crops, flash cuts)
4.3-5.5  credits opening: characters fly in, logo slam
5.5-7.0  crew credits scrolling, push toward the name
7.0-11.0 freeze + flash, push-in on the name, rest dims, gold glow
11.0-15  title card: logo, name, "Street Fighter - DNEG crew"
"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

P = "projects/vinay-credit"
W, H, FPS, DUR = 1080, 1920, 25, 15.0
N = int(DUR * FPS)
SRC = f"{P}/source/movie.mp4"
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-{}.otf"
GOLD = np.array([255, 196, 92], np.float32)


def decode(ss, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ss), "-t", str(t), "-i", SRC,
                          "-vf", f"scale={W}:{H}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3



# ---------- trailer montage: (start, length) in the trailer, vertical crop centre x in the 1280 frame
TR = f"{P}/source/trailer.mp4"
SHOTS = [(94.3, 0.60, 640), (39.9, 0.40, 640), (41.1, 0.40, 640), (123.9, 0.40, 600),
         (135.9, 0.50, 640), (51.9, 0.40, 640), (142.8, 0.55, 540), (125.9, 0.45, 640), (119.4, 0.60, 640)]


def trailer_clip(ss, dur, cx):
    cw = 302
    x = int(min(max(cx - cw / 2, 0), 1280 - cw))
    vf = (f"crop={cw}:536:{x}:92,fps={FPS},scale={W}:{H}:flags=lanczos,unsharp=5:5:0.8,"
          f"eq=contrast=1.12:saturation=1.2")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ss), "-t", str(dur + 0.1), "-i", TR, "-vf", vf,
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


MONTAGE, CUTS = [], []
acc = 0.0
for ss, d, cx in SHOTS:
    CUTS.append(acc)
    MONTAGE.append(trailer_clip(ss, d, cx))
    acc += d
assert abs(acc - 4.3) < 1e-6, acc

opening = decode(1.2, 1.2)
scroll = decode(66.56, 1.5)
freeze = Image.open(f"{P}/review/freeze_x4.png").convert("RGB")     # 2880x5120
FW, FH = freeze.size
S = FW / 720.0                                                        # source px -> freeze px
NAME = (376, 735, 556, 754)                                           # name box in 720x1280 source
NC = ((NAME[0] + NAME[2]) / 2, (NAME[1] + NAME[3]) / 2)

# vignette
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIG = (1 - 0.45 * np.clip(r - 0.55, 0, 1) ** 1.4)[..., None]
rng = np.random.default_rng(7)


def finish(f, grain=6.0):
    f = f.astype(np.float32) * VIG
    f += rng.normal(0, grain, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1)
    return np.clip(f, 0, 255).astype(np.uint8)


def camera(img, z, cx, cy):
    """Crop a W/H window at zoom z centred (clamped) on (cx, cy) in source-720 coords."""
    iw, ih = img.size
    s = iw / 720.0
    cw, ch = 720 / z, 1280 / z
    x0 = min(max(cx - cw / 2, 0), 720 - cw)
    y0 = min(max(cy - ch / 2, 0), 1280 - ch)
    box = (x0 * s, y0 * s, (x0 + cw) * s, (y0 + ch) * s)
    out = img.resize((W, H), Image.LANCZOS, box=box)
    return out, (x0, y0, W / cw)                                     # mapping for overlays


def cam_at(t):
    """Shared camera for scroll (2.4-6.0) and freeze (6.0-10.5)."""
    if t < 7.0:
        p = ease((t - 5.5) / 1.5)
        z = 1.0 + 0.10 * p
        k = 0.25 * p
    else:
        p = ease((t - 7.15) / 2.3)
        z = 1.10 + 1.75 * p + 0.06 * max(t - 9.45, 0)                # slow drift after landing
        k = 0.25 + 0.75 * ease((t - 7.0) / 2.45)
    return z, 360 + (NC[0] - 360) * k, 640 + (NC[1] - 640) * k


# ---------- title card background: logo frame with the half-drawn "thanks" line painted out
card = Image.open(f"{P}/review/logo_x4.png").convert("RGB")
cs = card.size[0] / 720
patch = card.crop((0, int(290 * cs), card.size[0], int(340 * cs)))
card.paste(patch, (0, int(232 * cs)))
names = card.crop((int(215 * cs), int(946 * cs), int(515 * cs), int(960 * cs)))   # paint out stray crew names
card.paste(names, (int(215 * cs), int(959 * cs)))
card.paste(names.resize((names.size[0], names.size[1] // 2)), (int(215 * cs), int(972 * cs)))
card = card.resize((W, H), Image.LANCZOS)
card_np = np.asarray(card, np.float32)
mid = np.clip(1 - np.abs(yy - 900) / 520, 0, 1)[..., None]           # darken the text zone
card_np = card_np * (1 - 0.55 * mid)


def text_layer(t):
    """Title-card typography as an RGBA image."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    def spaced(y, s, font, fill, track, alpha, rise=0):
        if alpha <= 0:
            return
        widths = [font.getlength(c) for c in s]
        total = sum(widths) + track * (len(s) - 1)
        x = (W - total) / 2
        col = fill + (int(255 * alpha),)
        for c, w in zip(s, widths):
            d.text((x, y + rise), c, font=font, fill=col)
            x += w + track

    t0 = 11.4
    a1 = ease_out((t - t0) / 0.6)
    spaced(640, "FILMOGRAPHY", ImageFont.truetype(FONT.format("Medium"), 34), (255, 196, 92), 14 + 6 * a1, a1, 20 * (1 - a1))
    a2 = ease_out((t - t0 - 0.35) / 0.8)
    big = ImageFont.truetype(FONT.format("SemiBold"), 104)
    spaced(730, "VINAY KRISHAN", big, (255, 255, 255), 6 + 6 * a2, a2, 30 * (1 - a2))
    spaced(850, "ROHILLA", big, (255, 255, 255), 6 + 6 * a2, a2, 30 * (1 - a2))
    a3 = ease_out((t - t0 - 0.9) / 0.9)
    if a3 > 0:
        half = 300 * a3
        d.rectangle((W / 2 - half, 1006, W / 2 + half, 1009), fill=(255, 196, 92, int(230 * a3)))
    a4 = ease_out((t - t0 - 1.3) / 0.8)
    spaced(1050, "STREET FIGHTER", ImageFont.truetype(FONT.format("Medium"), 44), (255, 255, 255), 16, a4, 16 * (1 - a4))
    spaced(1118, "SR. MATCHMOVE ARTIST", ImageFont.truetype(FONT.format("SemiBold"), 38), (255, 196, 92), 10, a4, 16 * (1 - a4))
    a5 = ease_out((t - t0 - 1.7) / 0.8)
    spaced(1182, "DNEG", ImageFont.truetype(FONT.format("Light"), 32), (230, 230, 230), 22, a5 * 0.9, 12 * (1 - a5))
    return layer


def glow(arr, t):
    """Dim everything but the name, then add a gold glow on its letters."""
    hl = ease((t - 9.2) / 0.6)
    if hl <= 0:
        return arr
    z, cx, cy = cam_at(t)
    x0, y0, sc = cam_box(z, cx, cy)
    bx = [(NAME[0] - 8 - x0) * sc, (NAME[1] - 6 - y0) * sc, (NAME[2] + 8 - x0) * sc, (NAME[3] + 6 - y0) * sc]
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle(bx, radius=20, fill=255)
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(28)), np.float32)[..., None] / 255
    out = arr * (1 - 0.6 * hl * (1 - m))
    lum = arr.mean(2)
    letters = np.clip((lum - 150) / 80, 0, 1) * m[..., 0]
    g = Image.fromarray((letters * 255).astype(np.uint8))
    halo = np.asarray(g.filter(ImageFilter.GaussianBlur(14)), np.float32)[..., None] / 255
    tight = np.asarray(g.filter(ImageFilter.GaussianBlur(3)), np.float32)[..., None] / 255
    pulse = 1 + 0.12 * np.sin((t - 9.2) * 3.0)
    out = out + GOLD * (halo * 1.6 + tight * 0.5) * hl * pulse
    out = out * (1 - letters[..., None] * 0.25 * hl) + np.array([255, 226, 160]) * letters[..., None] * 0.25 * hl
    # underline that draws left to right
    u = ease_out((t - 9.45) / 0.5)
    if u > 0:
        y = int((NAME[3] + 2.5 - y0) * sc)
        xa = int((NAME[0] - x0) * sc)
        xb = int(xa + (NAME[2] - NAME[0]) * sc * u)
        out[y:y + 4, max(xa, 0):min(xb, W)] = GOLD
    return out


def cam_box(z, cx, cy):
    cw, ch = 720 / z, 1280 / z
    x0 = min(max(cx - cw / 2, 0), 720 - cw)
    y0 = min(max(cy - ch / 2, 0), 1280 - ch)
    return x0, y0, W / cw


enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "14",
                        "-pix_fmt", "yuv420p", f"{P}/shots/sh010/edit/v001/video_1080_v2.mp4"], stdin=subprocess.PIPE)

for i in range(N):
    t = i / FPS
    if t < 4.3:
        k = max(j for j, c in enumerate(CUTS) if c <= t + 1e-6)
        clip = MONTAGE[k]
        f = clip[min(int(round((t - CUTS[k]) * FPS)), len(clip) - 1)].astype(np.float32)
        if t - CUTS[k] < 0.08 and k > 0:                               # 2-frame flash on every cut
            f = f + (255 - f) * 0.55
    elif t < 5.5:
        f = opening[min(int(round((t - 4.3) * FPS)), len(opening) - 1)].astype(np.float32)
        if t < 4.38:
            f = f + (255 - f) * 0.7
    elif t < 7.0:
        j = min(int(round((t - 5.5) * FPS)), len(scroll) - 1)
        z, cx, cy = cam_at(t)
        f = np.asarray(camera(Image.fromarray(scroll[j]), z, cx, cy)[0], np.float32)
        if t < 5.58:
            f *= 0.6
    elif t < 11.5:
        z, cx, cy = cam_at(min(t, 11.0))
        f = np.asarray(camera(freeze, z, cx, cy)[0], np.float32)
        f = glow(f, min(t, 11.0))
        flash = max(0.0, 1 - (t - 7.0) / 0.28)                         # freeze-frame hit
        f = f + (255 - f) * flash * 0.85
        if t >= 11.0:                                                  # dissolve into the card
            a = ease((t - 11.0) / 0.5)
            f = f * (1 - a) + card_np * a
    else:
        f = card_np.copy()
    if t >= 11.0:
        lay = np.asarray(text_layer(t), np.float32)
        a = lay[..., 3:] / 255
        f = f * (1 - a) + lay[..., :3] * a
    if t > 14.3:                                                       # fade out
        f *= 1 - ease((t - 14.3) / 0.7)
    enc.stdin.write(finish(f).tobytes())
    if i % 50 == 0:
        print(f"frame {i}/{N}", file=sys.stderr, flush=True)
enc.stdin.close()
enc.wait()
