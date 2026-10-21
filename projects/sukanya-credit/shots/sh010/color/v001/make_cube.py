# silver.cube: silver-gelatin B&W, crushed toe, soft shoulder, warm-ivory top end.
# Output is a pure function of Rec.709 luma, so input colour (blue/neon/red scenes) cannot survive.
# Toning is weighted to highlights only and always B <= G <= R (never cool).
import sys, numpy as np
from scipy.interpolate import PchipInterpolator
N = 65
out = sys.argv[1]
xs = [0.0, 0.06, 0.12, 0.30, 0.50, 0.70, 0.85, 1.0]
ys = [0.0, 0.012, 0.038, 0.262, 0.500, 0.735, 0.900, 0.970]
curve = PchipInterpolator(xs, ys)
ivory = np.array([1.0, 0.980, 0.943])           # #F4EFE6 ratios
def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)
g = np.linspace(0, 1, N)
with open(out, "w") as f:
    f.write('TITLE "silver-gelatin ivory (sukanya-credit sh010 color v001)"\n')
    f.write(f"LUT_3D_SIZE {N}\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n")
    for b in g:              # .cube: R fastest, then G, then B
        for gg in g:
            for r in g:
                # panchromatic mix: 45% Rec.709 luma + 55% max(RGB) so blue/neon light still reads as light
                y = 0.45 * (0.2126 * r + 0.7152 * gg + 0.0722 * b) + 0.55 * max(r, gg, b)
                v = float(curve(y))
                w = smoothstep(0.35, 1.0, v)
                rgb = v * (1 - w + w * ivory)
                f.write("%.6f %.6f %.6f\n" % tuple(np.clip(rgb, 0, 1)))
print("wrote", out)
