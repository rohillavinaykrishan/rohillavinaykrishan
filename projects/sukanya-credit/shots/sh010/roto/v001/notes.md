# sh010 roto/depth v001 (build plan task 2)

## p4_parallax.mp4 (P4, 4.60-6.04)
- still: trailer 112.80 s, `crop=1280:536:0:92,crop=302:536:509:0,scale=1080:1920:flags=lanczos` (CX 660) -> p4_still.png (ungraded colour; the colorist's silver chain still applies)
- `depth.py parallax p4_still.png p4_parallax.mp4 --move dolly-in --dur 1.44 --fps 25 --amount 0.8 --size 1080x1920`
- verified: h264 yuv420p 1080x1920, 25/1, 36 frames. Frames 0/18/35 checked, no edge tearing.
- Note: at CX 660 the leaping fighter's (Blanka) head is cut by the left frame edge; it is the director's CX, unchanged.

## hero_1080.png / hero_depth.png
- trailer 151.90 s, CX 770 (cues.json `hero_pointcloud_frame` says cx 760; brief and treatment say 770, used 770). Ungraded colour.
- `depth.py map hero_1080.png hero_depth.png` -> 16-bit, 1080x1920, white = near.

## points.json (make_points.py; rerun: `vfx-python make_points.py 2600 800`)
Treatment section 7 gives no exact JSON layout, so this schema is used:
```
{"w":2160,"h":3840,"f":2600,"cx":1080,"cy":1920,"z_near":2700,"z_far":5200,
 "n_edge":2600,"n_fill":800,"src":"...","points":[[x,y,z,l],...]}
```
- x,y: px in the 2160x3840 frame (= where the point reprojects at the solved pose)
- z: camera-space depth Zc at the solved pose (camera z=2600, f=2600), 2700 (near) .. 5200 (far), so the cloud sits behind the names (Zc 2600)
- l: display luminance 0..1 (draw alpha = l*0.8, per section 7)
- unproject: Xw=(x-1080)*z/2600, Yw=(y-1920)*z/2600, Zw=2600-z
- z = 2700 + (1-depth)*2500

Sampling: 3,400 points = 2,600 edge (76 %) + 800 luma-weighted fill.
- The plate is lit in blue; Rec.709 luma left her face as dark as the blue wall, so the B&W mix is red-weighted (0.55R 0.35G 0.10B) + CLAHE.
- Edges: Sobel on that luma (blur 1.6), top 10 % (6 % starved the soft eyes/nose/mouth), weight sqrt(gradient).
- All weights x depth subject mask x a soft hand-placed face ellipse (centre 680,690, radii 400x440 at 1080) so most dots land on the face, not the hair/collar.
- l = (0.25 + 0.75*luma)^0.7 (floor + lift) so dots stay visible at alpha l*0.8.

## review/points_preview.png
Left: solved pose (1080x1920, 4 px dots at 4K scale). Right: 25 deg yaw orbit around the face depth.
The face (eyes, nose, mouth, jaw line, buns/hair) reads frontally; in the orbit the face compresses and the chest/collar comes forward, so the depth reads as relief.
Known: the face relief from Depth Anything is shallow (about 550 units of Zc across the face); mograph can scale (z - 3600) for more relief before unprojecting; points stay on their own pixels at the solved pose because they move along their camera rays.
