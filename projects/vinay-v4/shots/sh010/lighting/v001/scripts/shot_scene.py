# sh010 shot CG (treatment 9.3): monument asset + plate-matched backlit sun + shadow catcher + fall + motion blur.
# usage: blender -b -P shot_scene.py -- OUTDIR WIDTH SAMPLES FRAMES [save.blend]
#   WIDTH = un-overscanned plate-aligned width (1080 proxy / 2808 final). Render res = round(1.16*W) x round(1.16*H)
#   FRAMES "0,25,51" or "0-51" ; "none" = build + save only
import bpy, math, mathutils, sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import monument as M

argv = sys.argv[sys.argv.index('--') + 1:]
OUTDIR, W, SAMP, FR = argv[0], int(argv[1]), int(argv[2]), argv[3]
SAVE = argv[4] if len(argv) > 4 else None
LAY = '/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/layout/v001/'
OS = 1.16
H = round(W * 536 / 1280)

# ---- plate-matched light (measured on s25: the fighters' shadows run toward world az -160 deg,
#      i.e. the sun sits in front of the camera, ~20 deg right of +Y, elevation ~35 deg)
SUN_AZ, SUN_EL = 20.0, 35.0          # bearing of the sun POSITION, deg from +Y toward +X
SUN_E, SUN_COL, SUN_ANGLE = 4.5, (1.0, 0.95, 0.86), 1.5
WORLD_COL, WORLD_E = (0.80, 0.76, 0.70), 0.48
exec(os.environ.get('TW', ''))

bpy.ops.wm.open_mainfile(filepath=LAY + 'solve_cam.blend')
sc = bpy.context.scene
for n in ('NAME_PLACEHOLDER', 'PLINTH_PLACEHOLDER'):
    o = bpy.data.objects.get(n)
    if o: bpy.data.objects.remove(o)
holder = bpy.data.objects['MONUMENT_PLACEHOLDER']; holder.name = 'MONUMENT_FALL'
root, txt, plinth, dims = M.build(sc, 'MONUMENT_ASSET')
for o in (txt, plinth):
    o.parent = holder; o.matrix_parent_inverse = mathutils.Matrix.Identity(4)
bpy.data.objects.remove(root)
txt.name = 'MONUMENT_NAME'; plinth.name = 'MONUMENT_PLINTH'
# fall keys -> linear (z = 5(1-(i/4)^2) on s0-s4, then 0)
ad = holder.animation_data.action
try:
    fcs = list(ad.fcurves)
except AttributeError:
    fcs = [fc for layer in ad.layers for strip in layer.strips for cb in strip.channelbags for fc in cb.fcurves]
for fc in fcs:
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    fc.extrapolation = 'CONSTANT'

# shadow catcher (layout's 80 m GROUND) - warm sand albedo so the bounce on the monument's shaded faces is right
g = bpy.data.objects['GROUND']; g.is_shadow_catcher = True
gm = g.data.materials[0]; gb = gm.node_tree.nodes['Principled BSDF']
gb.inputs['Base Color'].default_value = M.hexlin('#CDB08A'); gb.inputs['Roughness'].default_value = 0.95

# sun
so = bpy.data.objects['SUN']; sd = so.data
sd.energy = SUN_E; sd.color = SUN_COL; sd.angle = math.radians(SUN_ANGLE)
a, e = math.radians(SUN_AZ), math.radians(SUN_EL)
pos = mathutils.Vector((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e)))
so.rotation_euler = (-pos).to_track_quat('-Z', 'Y').to_euler()
wo = sc.world; bgn = wo.node_tree.nodes['Background']
bgn.inputs['Color'].default_value = WORLD_COL + (1,); bgn.inputs['Strength'].default_value = WORLD_E
wo.mist_settings.start = 8.0; wo.mist_settings.depth = 60.0; wo.mist_settings.falloff = 'LINEAR'

# camera: pinhole with overscan (same focal in px), see layout distort.py
cam = sc.camera; cam.data.sensor_width = 36 * OS
sc.render.resolution_x = round(OS * W); sc.render.resolution_y = round(OS * H); sc.render.resolution_percentage = 100
sc.render.use_border = False

# render settings
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMP
sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.03
sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPENIMAGEDENOISE'
sc.cycles.max_bounces = 4; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 1
sc.cycles.transmission_bounces = 0; sc.cycles.volume_bounces = 0
sc.render.film_transparent = True
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'; sc.view_settings.exposure = 0
vl = sc.view_layers[0]
vl.cycles.use_pass_shadow_catcher = True; vl.use_pass_mist = True
vl.use_pass_z = False
try:
    vl.use_pass_cryptomatte_object = True
except Exception: pass

# outputs: multilayer EXR (all passes, linear) + compositor PNGs (cg RGBA 16-bit sRGB, shadow 16-bit linear)
os.makedirs(OUTDIR, exist_ok=True)
sc.render.image_settings.media_type = 'MULTI_LAYER_IMAGE'; sc.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'; sc.render.image_settings.color_depth = '16'
sc.render.image_settings.exr_codec = 'ZIP'
sc.render.filepath = os.path.join(OUTDIR, 'exr', 'cg.####')
ng = bpy.data.node_groups.new('cg_comp', 'CompositorNodeTree'); sc.compositing_node_group = ng
rl = ng.nodes.new('CompositorNodeRLayers')
fo = ng.nodes.new('CompositorNodeOutputFile'); fo.directory = OUTDIR + '/'; fo.file_name = ''
fo.format.media_type = 'IMAGE'; fo.format.file_format = 'PNG'; fo.format.color_mode = 'RGBA'; fo.format.color_depth = '16'
fo.file_output_items.clear()
it1 = fo.file_output_items.new('RGBA', 'cg/cg.')
it2 = fo.file_output_items.new('RGBA', 'shadow/shadow.')
it3 = fo.file_output_items.new('RGBA', 'mist/mist.')
for it in (it2, it3):
    it.override_node_format = True
    it.format.media_type = 'IMAGE'; it.format.file_format = 'PNG'; it.format.color_mode = 'BW'; it.format.color_depth = '16'
    try:
        it.save_as_render = False
    except Exception: pass
outs = {o.name: o for o in rl.outputs}
ng.links.new(outs['Image'], fo.inputs[0])
ng.links.new(outs['Shadow Catcher'], fo.inputs[1])
ng.links.new(outs['Mist'], fo.inputs[2])
go = ng.nodes.new('NodeGroupOutput')
try:
    ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    ng.links.new(outs['Image'], go.inputs[0])
except Exception as ex: print('group output', ex)
print('RL outputs', list(outs))

if SAVE:
    try:
        bpy.ops.file.pack_all()
    except Exception as ex: print('pack', ex)
    bpy.ops.wm.save_as_mainfile(filepath=SAVE)
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_mainfile()

if FR != 'none':
    if '-' in FR:
        a_, b_ = map(int, FR.split('-')); frames = range(a_, b_ + 1)
    else:
        frames = [int(x) for x in FR.split(',')]
    for f in frames:
        sc.frame_set(f); t0 = time.time()
        bpy.ops.render.render(write_still=True)
        print('FRAME', f, 'RENDER_SECONDS', round(time.time() - t0, 1), sc.render.resolution_x, sc.render.resolution_y, SAMP, flush=True)
