"""MG1 TEMPORARY tritone / drain LUTs (stand-ins until the Colorist's color/v001/*.cube exist).
Implements treatment section 5: Rec.709 luma -> curves 0/0 .12/.06 .5/.45 .85/.85 1/1 ->
gradient map in OKLab: 0 #14080F, .25 #4A1838, .5 #7A2E5C, .78 #FFB12A, 1 #FFF3DC.
drain = the same at 35% chroma and -0.3 EV.
Usage: python3 make_luts.py <outdir>"""
import sys, os
import numpy as np

N = 33
STOPS = [(0.0, "#14080F"), (0.25, "#4A1838"), (0.5, "#7A2E5C"), (0.78, "#FFB12A"), (1.0, "#FFF3DC")]
CURVE = [(0, 0), (0.12, 0.06), (0.5, 0.45), (0.85, 0.85), (1, 1)]


def srgb_to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def lin_to_oklab(rgb):
    M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                   [0.2119034982, 0.6806995451, 0.1073969566],
                   [0.0883024619, 0.2817188376, 0.6299787005]])
    M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                   [1.9779984951, -2.4285922050, 0.4505937099],
                   [0.0259040371, 0.7827717662, -0.8086757660]])
    lms = rgb @ M1.T
    return np.cbrt(lms) @ M2.T


def oklab_to_lin(lab):
    M2i = np.array([[1, 0.3963377774, 0.2158037573],
                    [1, -0.1055613458, -0.0638541728],
                    [1, -0.0894841775, -1.2914855480]])
    M1i = np.array([[4.0767416621, -3.3077115913, 0.2309699292],
                    [-1.2684380046, 2.6097574011, -0.3413193965],
                    [-0.0041960863, -0.7034186147, 1.7076147010]])
    lms = (lab @ M2i.T) ** 3
    return lms @ M1i.T


def hex2rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


def build(chroma=1.0, ev=0.0):
    g = np.linspace(0, 1, N)
    b, gg, r = np.meshgrid(g, g, g, indexing="ij")  # cube order: R fastest
    rgb = np.stack([r, gg, b], -1).reshape(-1, 3)
    y = rgb @ np.array([0.2126, 0.7152, 0.0722])  # Rec.709 weights on encoded values (look, not physics)
    xs, ys = zip(*CURVE)
    y = np.interp(y, xs, ys)
    if ev:
        y = np.clip(lin_to_srgb(srgb_to_lin(y) * 2 ** ev), 0, 1)
    sx = np.array([s for s, _ in STOPS])
    labs = np.array([lin_to_oklab(srgb_to_lin(hex2rgb(c))[None])[0] for _, c in STOPS])
    lab = np.stack([np.interp(y, sx, labs[:, k]) for k in range(3)], -1)
    lab[:, 1:] *= chroma
    out = lin_to_srgb(oklab_to_lin(lab))
    return out


def write(path, data, title):
    with open(path, "w") as f:
        f.write(f'TITLE "{title}"\nLUT_3D_SIZE {N}\n')
        for v in data:
            f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    write(os.path.join(out, "mg1_temp_tritone.cube"), build(), "MG1 temp tritone (stand-in)")
    write(os.path.join(out, "mg1_temp_drain.cube"), build(0.35, -0.3), "MG1 temp drain (stand-in)")
    print("ok")
