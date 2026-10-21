# build_blend.py : solve_cam.blend + anchor.json from cams.json
# blender -b -P build_blend.py -- [anchor_x anchor_y rotz_deg]
import bpy, json, math, sys, numpy as np, mathutils
L = '/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/layout/v001/'
D = '/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/director/v001/'
argv = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
AX, AY, AR = (float(argv[0]), float(argv[1]), float(argv[2])) if len(argv) >= 3 else (1.5, 12.5, -12.0)
cj = json.load(open(L+'cams.json')); W, H, f, cx, cy, k1 = cj['width'], cj['height'], cj['f'], cj['cx'], cj['cy'], cj['k1']

for o in list(bpy.data.objects): bpy.data.objects.remove(o)
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 0, 51
sc.render.fps, sc.render.fps_base = 24000, 1001
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 8; sc.render.film_transparent = True
sc.view_settings.view_transform = 'Standard'
# ---- camera, 52 keys (scene frame N = plate frame sN = plate.%04d N)
cd = bpy.data.cameras.new('SOLVE_CAM'); cd.sensor_fit = 'HORIZONTAL'; cd.sensor_width = 36; cd.lens = cj['lens_mm']
cd.clip_start = 0.05; cd.clip_end = 500
co = bpy.data.objects.new('SOLVE_CAM', cd); sc.collection.objects.link(co); sc.camera = co
co.rotation_mode = 'QUATERNION'
for c in cj['frames']:
    mw = mathutils.Matrix(c['blender_matrix_world'])
    co.matrix_world = mw
    co.keyframe_insert('location', frame=c['frame']); co.keyframe_insert('rotation_quaternion', frame=c['frame'])
# make quaternion keys continuous + linear interpolation (one key per frame anyway)
ad = co.animation_data.action
try:
    fcs = ad.fcurves
except AttributeError:
    fcs = [fc for layer in ad.layers for strip in layer.strips for cb in strip.channelbags for fc in cb.fcurves]
for fc in fcs:
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
# plate as camera background (viewport reference)
try:
    img = bpy.data.images.load(L+'plate/plate.0001.png'); img.source = 'SEQUENCE'
    cd.show_background_images = True; bg = cd.background_images.new(); bg.image = img
    bg.image_user.frame_start = 0; bg.image_user.frame_duration = 52; bg.image_user.frame_offset = 0; bg.alpha = 1.0
except Exception as e: print('bg image skipped', e)
# ---- ground (shadow catcher) 80 m
me = bpy.data.meshes.new('GROUND'); me.from_pydata([(-40, -25, 0), (40, -25, 0), (40, 55, 0), (-40, 55, 0)], [], [(0, 1, 2, 3)])
gr = bpy.data.objects.new('GROUND', me); sc.collection.objects.link(gr); gr.is_shadow_catcher = True
gm = bpy.data.materials.new('sand_placeholder'); gm.use_nodes = True
gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.62, 0.50, 0.36, 1); me.materials.append(gm)
# ---- anchor + placeholder monument
an = bpy.data.objects.new('MONUMENT_ANCHOR', None); an.empty_display_type = 'ARROWS'; an.empty_display_size = 1.0
sc.collection.objects.link(an); an.location = (AX, AY, 0); an.rotation_euler = (0, 0, math.radians(AR))
mon = bpy.data.objects.new('MONUMENT_PLACEHOLDER', None); sc.collection.objects.link(mon); mon.parent = an
# plinth 7.8 x 1.0 x 0.24
bpy.ops.mesh.primitive_cube_add(size=1); pl = bpy.context.active_object; pl.name = 'PLINTH_PLACEHOLDER'
pl.scale = (7.8, 1.0, 0.24); pl.location = (0, 0, 0.12); bpy.ops.object.transform_apply(scale=True, location=True)
pl.parent = mon
# name text (Unbounded 900, space_line 0.70, extrude 0.30, bevel 0.02) scaled to 7.2 m wide, standing on the plinth
fnt = bpy.data.fonts.load(D+'fonts/Unbounded-900.ttf')
td = bpy.data.curves.new('NAME_PLACEHOLDER', 'FONT'); td.body = 'VINAY\nKRISHAN\nROHILLA'; td.font = fnt
td.align_x = 'CENTER'; td.space_line = 0.70; td.extrude = 0.30; td.bevel_depth = 0.02; td.bevel_resolution = 3; td.size = 1.0
to = bpy.data.objects.new('NAME_PLACEHOLDER', td); sc.collection.objects.link(to)
bpy.context.view_layer.objects.active = to; to.select_set(True)
bpy.ops.object.convert(target='MESH'); to = bpy.context.active_object
vs = np.array([v.co[:] for v in to.data.vertices]); wd = vs[:, 0].ptp() if hasattr(vs[:, 0], 'ptp') else np.ptp(vs[:, 0])
sz = 7.2/wd
M = mathutils.Matrix.Rotation(math.radians(90), 4, 'X') @ mathutils.Matrix.Scale(sz, 4)
to.data.transform(M); vs = np.array([v.co[:] for v in to.data.vertices])
to.data.transform(mathutils.Matrix.Translation((-(vs[:, 0].min()+vs[:, 0].max())/2, -(vs[:, 1].min()+vs[:, 1].max())/2, 0.24-vs[:, 2].min())))
to.parent = mon
mat = bpy.data.materials.new('bone_placeholder'); mat.use_nodes = True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.82, 0.77, 0.69, 1)
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.55
to.data.materials.append(mat); pl.data.materials.append(mat)
# fall animation on the placeholder (anchor stays at rest): z = 5*(1-(i/4)^2), i=0..4, then 0
for i in range(0, 6):
    mon.location = (0, 0, 5*(1-(i/4)**2) if i <= 4 else 0); mon.keyframe_insert('location', index=2, frame=i)
# sun (lookdev values: backlight, az 40 deg right of view axis, elev 35)
sd = bpy.data.lights.new('SUN', 'SUN'); sd.energy = 4.5; sd.angle = math.radians(1.5); sd.color = (1.0, 0.95, 0.86)
so = bpy.data.objects.new('SUN', sd); sc.collection.objects.link(so)
az, el = math.radians(40), math.radians(35)
dv = mathutils.Vector((-math.sin(az)*math.cos(el), -math.cos(az)*math.cos(el), -math.sin(el)))
so.rotation_euler = dv.to_track_quat('-Z', 'Y').to_euler()
wo = bpy.data.worlds.new('WORLD'); sc.world = wo; wo.use_nodes = True
wo.node_tree.nodes['Background'].inputs['Color'].default_value = (0.80, 0.76, 0.70, 1); wo.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.5
sc.frame_set(10); bpy.context.view_layer.update()

# ---- anchor.json : projections at REST (anchor transform, no fall)
A = np.array(an.matrix_world)
def wpts(obj):  # world coords at rest: anchor @ local(obj relative to placeholder)
    loc = np.array(mon.matrix_parent_inverse) if False else np.eye(4)
    v = np.array([vv.co[:] for vv in obj.data.vertices]); v = np.c_[v, np.ones(len(v))]
    return (A @ v.T).T[:, :3]
allv = np.vstack([wpts(to), wpts(pl)])
corners_l = {'front_left': (-3.9, -0.5), 'front_right': (3.9, -0.5), 'back_right': (3.9, 0.5), 'back_left': (-3.9, 0.5)}
corners_w = {k: (A @ np.array([x, y, 0, 1]))[:3] for k, (x, y) in corners_l.items()}
bmin, bmax = allv.min(0), allv.max(0)
centre_w = (A @ np.array([0, 0, (allv[:, 2].max())/2, 1]))[:3]
def project(c, Xs):
    R = np.array(c['R']); t = np.array(c['t']); Xc = Xs @ R.T + t
    x, y = Xc[:, 0]/Xc[:, 2], Xc[:, 1]/Xc[:, 2]; r2 = x*x+y*y
    return np.c_[f*x*(1+k1*r2)+cx, f*y*(1+k1*r2)+cy], Xc[:, 2]
HALF = 2160/(2808/W)/2   # FINAL window half-width in plate px (= 492.3)
fr_out = []; cxr = []
for c in cj['frames']:
    uv, z = project(c, allv); cu, _ = project(c, centre_w[None]); cxr.append(cu[0, 0])
    fall = []
    fr_out.append(dict(frame=c['frame'],
                       corners={k: [round(float(v), 2) for v in project(c, p[None])[0][0]] for k, p in corners_w.items()},
                       centre=[round(float(v), 2) for v in cu[0]],
                       bbox=[round(float(uv[:, 0].min()), 1), round(float(uv[:, 1].min()), 1), round(float(uv[:, 0].max()), 1), round(float(uv[:, 1].max()), 1)],
                       min_depth_m=round(float(z.min()), 2)))
cxr = np.array(cxr); k = np.exp(-0.5*(np.arange(-12, 13)/6.0)**2); k /= k.sum()
pad = np.r_[np.full(12, cxr[0]), cxr, np.full(12, cxr[-1])]; cxs = np.convolve(pad, k, 'valid')
cxs = np.clip(cxs, 493, 787)
checks = []
for i, fo in enumerate(fr_out):
    x0, y0, x1, y1 = fo['bbox']; CX = float(cxs[i])
    fo['crop_cx'] = round(CX, 1); fo['crop_cx_raw'] = round(float(cxr[i]), 1)
    fo['inside_final_window'] = bool(x0 >= CX-HALF and x1 <= CX+HALF and y1 <= H and y0 >= 0)
    fo['top_margin_pct'] = round(100*y0/H, 2)
    fo['ok'] = bool(fo['inside_final_window'] and y0 >= 0.06*H)
# fall frames: centre projection while falling (for the f169-173 crop, if the comp wants it)
for i in range(5):
    zf = 5*(1-(i/4)**2); cw = centre_w + np.array([0, 0, zf]); cf, _ = project(cj['frames'][i], cw[None])
    fr_out[i]['centre_falling'] = [round(float(v), 2) for v in cf[0]]; fr_out[i]['fall_z_m'] = round(zf, 3)
res = dict(convention=('Plate px (1280x536, lens-distorted with SIMPLE_RADIAL from cams.json) of MONUMENT_ANCHOR at rest (after landing). '
                       'corners = plinth base corners (7.8 x 1.0 m, front = toward camera); centre = monument centre (half height above anchor); '
                       'bbox = projected bounds of the placeholder text+plinth mesh [x0,y0,x1,y1]. crop_cx = FINAL window centre x in plate px '
                       '(Gaussian sigma 6 frames on crop_cx_raw, clamped 493-787); window = crop_cx +- %.1f px (2160 of 2808 at x1.30). '
                       'ok = inside window and top >= 6%% below frame top. centre_falling = s0-s4 with the fall z offset.') % HALF,
           anchor=dict(location=[AX, AY, 0], rot_z_deg=AR), monument_bounds_world=dict(min=bmin.round(3).tolist(), max=bmax.round(3).tolist()),
           window_half_width_px=round(HALF, 2), all_ok=all(fo['ok'] for fo in fr_out), frames=fr_out)
json.dump(res, open(L+'anchor.json', 'w'), indent=1)
bad = [fo['frame'] for fo in fr_out if not fo['ok']]
print('ANCHOR', AX, AY, AR, 'all_ok', res['all_ok'], 'bad', bad, 'height', round(float(bmax[2]), 2),
      'min top%', min(fo['top_margin_pct'] for fo in fr_out), 'cx range', round(float(cxr.min()), 1), round(float(cxr.max()), 1))
for i in (0, 25, 51): print(i, fr_out[i]['bbox'], fr_out[i]['crop_cx'], fr_out[i]['top_margin_pct'])
sc.frame_set(0)
bpy.ops.wm.save_as_mainfile(filepath=L+'solve_cam.blend')
