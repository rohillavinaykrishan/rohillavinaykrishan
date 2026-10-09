---
name: matchmove
description: Camera tracking / matchmove / 3D camera solve of raw footage, including bluescreen and greenscreen plates. Use whenever Vinay says "matchmove", "track this shot", "camera track", "camera solve", "3D track" or hands over raw footage for tracking. Produces a solved camera (FBX, Nuke .nk/.chan, Blender .blend), a point cloud, a QC overlay video and a solve report.
---

# Matchmove

Vinay is a senior matchmove/compositing artist. When he says "matchmove", run the
pipeline straight away; don't ask for settings he didn't give. Use what he says
about the camera (sensor/back width, focal length, set measurements) and default
the rest. Judge the result by the QC numbers and overlay, and tell him plainly
where it's solid and where it isn't. Never call a solve "perfect"; give the numbers.

## Run it

```bash
python3 .claude/skills/matchmove/scripts/matchmove.py PLATE OUT_DIR \
    [--sensor 36] [--focal 35] [--screen blue|green] [--mask-dir DIR] \
    [--first-frame 1001] [--cam-height 1.6] [--max-size 1920] [--tracker auto|sift|klt]
```

- `PLATE`: a video file, a folder of frames, or the first frame of a sequence
  (PNG/JPG/TIF/EXR/DPX; non-PNG frames are converted for detection).
- `--sensor`: film back width in mm. Ask yourself what camera it is: if Vinay
  named one, use its sensor width (ARRI Alexa 35 open gate 27.99, Alexa Mini LF
  36.70, Sony FX3/A7 35.6, RED Komodo 27.03, Super35 generic 24.89; look up
  anything else rather than guessing). Unknown → 36, and say the solved focal
  is in full-frame-equivalent mm.
- `--focal`: only if known; it's a prior and still gets refined.
- `--screen blue|green`: for chroma plates. Builds feature masks that keep the
  screen and its tape markers (small non-screen blobs) and drop talent, props
  and off-screen areas (large blobs). It also switches the tracker to KLT.
- `--mask-dir`: Vinay's own roto/garbage mattes (`<frame>.png.png`, white =
  trackable static scenery). Use for moving cars, crowds, water, reflections.
- `--cam-height`: real camera height in metres for scale. Without it scale is
  set to a 1.6 m camera height and the report says ASSUMED.
- 4K plates: `--max-size 1920` (default) detects on a downscaled copy; raise to
  3200 for more precision on slow, detailed shots.
- `--tracker`: `auto` (default) uses KLT for screen plates and SIFT otherwise,
  and retries with the other tracker if frames are left unsolved. SIFT matches
  features by appearance (robust to fast motion and cuts in coverage); KLT
  follows each point frame to frame (needed when markers all look alike, as on
  bluescreen).

Runtime on the cloud CPU: roughly 5 s per frame at 720p (72 frames ≈ 6 min).
For long shots, run it in the background.

## What it does

1. Frames → `OUT/work/frames/<frame>.png`, numbered from `--first-frame`.
2. Optional screen/user masks.
3. 2D tracking: SIFT + sequential matching with quadratic overlap, or KLT
   (pyramidal Lucas-Kanade, forward-backward checked, tracks shorter than 6
   frames dropped) imported into COLMAP.
4. COLMAP incremental SfM, one camera with a RADIAL lens (f, k1, k2).
5. Levels the scene: dominant plane (usually the floor) → z = 0, Z up,
   origin on the plane, scale from camera height.
6. Per-frame reprojection error, QC overlay video, Blender export.

## Deliverables (in OUT_DIR)

| File | What |
|---|---|
| `camera.fbx` | Baked camera, Z-up (Maya/Houdini/Unreal/C4D import) |
| `camera_nuke.nk` | Nuke Camera2 node, Y-up, rot_order ZXY, focal/aperture set |
| `camera_nuke.chan` | Nuke/Maya .chan: frame tx ty tz rx ry rz |
| `matchmove.blend` | Camera with the plate as background + point cloud |
| `points.ply` | Solved 3D point cloud (leveled, same space as camera) |
| `qc_overlay.mp4` | Plate with reprojected points (green < 1 px, orange < 2 px, red ≥ 2 px) and a 1 m ground grid |
| `solve.json` | Lens (focal mm/px, k1, k2), errors, worst frames, missing frames, scale note, per-frame matrices |

Lens distortion: the solve uses k1/k2 on the original plate, so the camera
matches the **distorted** plate when you apply the same distortion. Give Vinay
k1/k2 and offer undistorted plates (`colmap image_undistorter`) if he wants to
work undistorted.

## QC before reporting

Always open the overlay (grab frames with ffmpeg, look at them) and check:

- `reprojection_error_px`: < 0.5 excellent, 0.5–1 good, > 1 investigate.
- `frames_missing` must be empty. If not, say which frames and why.
- Grid stays glued to the floor through the whole shot; no sliding or popping.
- Focal length is plausible for the camera; k1 small (|k1| < 0.2).
- `ground_plane_inliers` low (< 0.1) means leveling may have picked a wall:
  say so and check the grid.

Validated on synthetic plates with known cameras (errors after aligning to the
true camera):

| Shot | Tracker | Error | Focal | Rotation | Position (of path) |
|---|---|---|---|---|---|
| Textured set, dolly + pan, 72 fr | SIFT | 0.70 px | 34.7 / 35 mm | 0.02° | 0.05% |
| Same shot | KLT | 0.56 px | 34.9 / 35 mm | 0.03° | 0.15% |
| Bluescreen, tape markers, moving actor, 60 fr | KLT + mask | 0.42 px | 28.1 / 28 mm | 0.11° | 0.3% |

Real footage adds motion blur, grain, rolling shutter and lens breathing, so
expect higher errors; judge every shot by its own QC.

## Shots that fail, and what to do

- **Nodal pans / tripod shots (no parallax)**: SfM can't triangulate. Tell Vinay
  it's nodal; solve rotation-only (Blender tripod solver, or homographies) and
  deliver a nodal camera.
- **Zooms / focus breathing**: single fixed focal fails; split the shot or
  solve per-frame focal.
- **Heavy motion blur, low texture, rolling shutter, big moving objects
  without masks**: expect missing or noisy frames; mask the movers, or ask for
  set measurements / more markers.
- **Bluescreen with no markers**: nothing to track on the screen; the solve
  relies on whatever set is visible. Say so.

## Delivery

Files over 30 MB can't be sent in chat. Use a connected Google Drive/Dropbox if
available; otherwise send the small files (fbx, nk, chan, json, ply) and a
compressed QC overlay, and offer to split larger ones.
