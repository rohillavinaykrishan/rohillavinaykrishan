# sh010 roto/depth v002: point cloud re-registered to solve frame 271

Why: v001 used trailer 151.90 s (appears on frame 273); the plate shows 151.818 on frame 271 and her head moves ~100 px at 4K between them.

- hero_1080.png = copy of shots/sh010/edit/v001/hero_f271_1080.png (editor's exact frame 271, CX 769, crop x 618), 1080x1920.
- `depth.py map hero_1080.png hero_depth.png` (16-bit, white = near).
- `vfx-python make_points.py 2600 800` -> points.json, review/points_preview.png. Same schema as v001 (see ../v001/notes.md):
  {"w":2160,"h":3840,"f":2600,"cx":1080,"cy":1920,"z_near":2700,"z_far":5200,"n_edge","n_fill","src","points":[[x,y,z,l],...]}
  x,y frame px at 2160x3840; z = camera depth Zc at solved pose (2700 near .. 5200 far); l = display luma (alpha l*0.8).
  Unproject: Xw=(x-1080)*z/2600, Yw=(y-1920)*z/2600, Zw=2600-z.

Changes vs v001 method (needed for this frame, everything else identical):
- Face-prior ellipse centre moved 680,690 -> 720,690 (her head is ~40 px right at 1080 on frame 271).
- Frame 271 is softer (motion blur on the cut, heavier compression); Sobel blur 1.6 picked up block noise and the
  eyes/nose/mouth turned to mush, so the Sobel pre-blur is 2.5 (feature-scale contours) and fill points are weighted
  luma^3 (was ^1.5) so the dark features stay as gaps.
- 3,400 points: 2,600 edge (76 %) + 800 fill.

Checked: overlay of the points on hero_1080.png sits on the face; frontal preview reads as her face (brows, eyes, nose, mouth, jaw, earring line);
25 deg yaw view shows the face compressing and the chest/collar coming forward.
