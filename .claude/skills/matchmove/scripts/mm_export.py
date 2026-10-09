"""Build the matchmove scene in Blender from a solve and export it.

blender -b --factory-startup --python mm_export.py -- SOLVE_JSON OUT_DIR

SOLVE_JSON (written by matchmove.py) holds: resolution, fps, sensor_mm,
focal_mm, first frame, per-frame 4x4 camera-to-world matrices in Blender's
camera convention (Z-up world, camera looking down -Z), points_ply and plate.
Writes OUT_DIR/matchmove.blend, camera.fbx, camera_nuke.chan, camera_nuke.nk.
"""
import bpy, sys, os, json, math
from mathutils import Matrix

solve_path, out = sys.argv[sys.argv.index("--") + 1:]
s = json.load(open(solve_path))
W, H = s["resolution"]
frames = sorted(int(f) for f in s["camera_world"])
first, last = frames[0], frames[-1]

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
scn.render.resolution_x, scn.render.resolution_y = W, H
scn.render.fps = int(round(s["fps"]))
scn.frame_start, scn.frame_end = first, last

cam_data = bpy.data.cameras.new("MatchmoveCam")
cam_data.sensor_fit = "HORIZONTAL"
cam_data.sensor_width = s["sensor_mm"]
cam_data.sensor_height = s["sensor_mm"] * H / W
cam_data.lens = s["focal_mm"]
cam = bpy.data.objects.new("MatchmoveCam", cam_data)
scn.collection.objects.link(cam)
scn.camera = cam

mats = {int(f): Matrix(m) for f, m in s["camera_world"].items()}
for f in frames:
    cam.matrix_world = mats[f]
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_euler", frame=f)
for fc in cam.animation_data.action.fcurves:
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"

# Plate as camera background, for checking the solve in the viewport.
plate = s.get("plate_first_frame")
if plate and os.path.exists(plate):
    clip = bpy.data.movieclips.load(plate)
    clip.frame_start = first
    cam_data.show_background_images = True
    bg = cam_data.background_images.new()
    bg.source = "MOVIE_CLIP"
    bg.clip = clip
    bg.alpha = 1.0

# Point cloud as a mesh of vertices.
pts = []
ply = s.get("points_ply")
if ply and os.path.exists(ply):
    with open(ply) as fh:
        header = True
        for line in fh:
            if header:
                header = line.strip() != "end_header"
                continue
            v = line.split()
            pts.append(tuple(map(float, v[:3])))
if pts:
    me = bpy.data.meshes.new("SolvePoints")
    me.from_pydata(pts, [], [])
    scn.collection.objects.link(bpy.data.objects.new("SolvePoints", me))

os.makedirs(out, exist_ok=True)
bpy.ops.object.select_all(action="DESELECT")
cam.select_set(True)
bpy.context.view_layer.objects.active = cam
bpy.ops.export_scene.fbx(filepath=os.path.join(out, "camera.fbx"), use_selection=True,
                         object_types={"CAMERA"}, bake_anim=True, bake_anim_use_all_actions=False,
                         bake_anim_simplify_factor=0.0)

# Nuke: Y-up world, Camera rot_order ZXY, degrees.
to_yup = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))
rows = []
for f in frames:
    my = to_yup @ mats[f]
    e = my.to_euler("ZXY")
    t = my.translation
    rows.append((f, t.x, t.y, t.z, math.degrees(e.x), math.degrees(e.y), math.degrees(e.z)))
with open(os.path.join(out, "camera_nuke.chan"), "w") as fh:
    for r in rows:
        fh.write(f"{r[0]} " + " ".join(f"{v:.6f}" for v in r[1:]) + "\n")

def curve(i):
    return "{curve x%d %s}" % (first, " ".join(f"{r[i]:.6f}" for r in rows))

hap = s["sensor_mm"]
vap = s["sensor_mm"] * H / W
nk = f"""Camera2 {{
 inputs 0
 rot_order ZXY
 translate {{{curve(1)} {curve(2)} {curve(3)}}}
 rotate {{{curve(4)} {curve(5)} {curve(6)}}}
 focal {s['focal_mm']:.4f}
 haperture {hap:.4f}
 vaperture {vap:.4f}
 name MatchmoveCam
 label "solve {s.get('reprojection_error_px', '?')}px"
}}
"""
open(os.path.join(out, "camera_nuke.nk"), "w").write(nk)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "matchmove.blend"))
print(f"EXPORT OK frames={first}-{last} points={len(pts)}")
