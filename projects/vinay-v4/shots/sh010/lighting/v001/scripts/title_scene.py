# Title monument scene (treatment 9.3 "Title monument", 8 title layout).
# usage: blender -b -P title_scene.py -- MODE OUT.png RES_X SAMPLES [save.blend]
#   MODE: beauty (all in one, for lookdev) | fg (monument + contact shadow, RGBA) | bg (sky + ground + long shadow)
import bpy, math, mathutils, sys, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import monument as M

argv = sys.argv[sys.argv.index('--') + 1:]
MODE, OUT, RX, SAMP = argv[0], argv[1], int(argv[2]), int(argv[3])
SAVE = argv[4] if len(argv) > 4 else None

# ---------------- tweakables ----------------
CAM_LOC = (-3.6, -9.6, 0.55)
CAM_TGT = (0.15, 0.0, 1.75)
LENS = 30.0
SHIFT_Y = 0.0
SUN_EL, SUN_AZ_OFF = 24.0, -32.0     # sun direction = camera bearing rotated by AZ_OFF deg (neg = to the left)
SUN_E, SUN_COL = 5.2, (1.0, 0.86, 0.68)
RIM_E, RIM_COL, RIM_EL, RIM_AZ = 2.2, (1.0, 0.62, 0.42), 12.0, 150.0
FILL_COL, FILL_E = (0.62, 0.50, 0.42), 0.32
# sky ramp on sin(elevation) of camera rays (linear RGB)
SKY = [(0.000, (0.80, 0.52, 0.28)),
       (0.035, (0.42, 0.24, 0.12)),
       (0.12, (0.090, 0.058, 0.036)),
       (0.30, (0.030, 0.022, 0.016)),
       (0.62, (0.0065, 0.0052, 0.0042))]
HAZE_START, HAZE_END = 12.0, 160.0
EXPOSURE = 0.0
LOOK = 'AgX - Medium High Contrast'
# --------------------------------------------

for o in list(bpy.data.objects): bpy.data.objects.remove(o)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMP
sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.02
sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPENIMAGEDENOISE'
sc.cycles.max_bounces = 6; sc.cycles.diffuse_bounces = 3; sc.cycles.glossy_bounces = 2
sc.cycles.transmission_bounces = 0; sc.cycles.volume_bounces = 0; sc.cycles.transparent_max_bounces = 4
sc.render.resolution_x = RX; sc.render.resolution_y = RX * 16 // 9; sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_depth = '16'
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = LOOK; sc.view_settings.exposure = EXPOSURE
sc.render.film_transparent = (MODE == 'fg')
sc.render.image_settings.color_mode = 'RGBA' if MODE == 'fg' else 'RGB'

root, txt, plinth, dims = M.build(sc)
mon_objs = [txt, plinth]
mc = bpy.data.collections.new('MONUMENT_C'); sc.collection.children.link(mc)
for o in mon_objs:
    for c in list(o.users_collection): c.objects.unlink(o)
    mc.objects.link(o)

# ground: sand with grazing-sun noise bump, distance haze to the horizon colour
bpy.ops.mesh.primitive_plane_add(size=4000, location=(0, 0, 0)); g = bpy.context.active_object; g.name = 'ground'
gm = bpy.data.materials.new('sand'); gm.use_nodes = True; nt = gm.node_tree; N = nt.nodes; L = nt.links
bs = N['Principled BSDF']; bs.inputs['Roughness'].default_value = 0.95
tc = N.new('ShaderNodeTexCoord')
n1 = N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 3.0; n1.inputs['Detail'].default_value = 4
n2 = N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 90.0; n2.inputs['Detail'].default_value = 8
L.new(tc.outputs['Object'], n1.inputs['Vector']); L.new(tc.outputs['Object'], n2.inputs['Vector'])
cm = N.new('ShaderNodeMix'); cm.data_type = 'RGBA'
cm.inputs['A'].default_value = M.hexlin('#B89A74'); cm.inputs['B'].default_value = M.hexlin('#CDB08A')
L.new(n1.outputs['Fac'], cm.inputs['Factor'])
L.new(cm.outputs['Result'], bs.inputs['Base Color'])
ad = N.new('ShaderNodeMath'); ad.operation = 'MULTIPLY_ADD'; ad.inputs[1].default_value = 0.35
L.new(n1.outputs['Fac'], ad.inputs[0]); L.new(n2.outputs['Fac'], ad.inputs[2])
bm = N.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.35; bm.inputs['Distance'].default_value = 0.02
L.new(ad.outputs[0], bm.inputs['Height']); L.new(bm.outputs['Normal'], bs.inputs['Normal'])
cd_ = N.new('ShaderNodeCameraData')
hz = N.new('ShaderNodeMapRange'); hz.inputs['From Min'].default_value = HAZE_START; hz.inputs['From Max'].default_value = HAZE_END
L.new(cd_.outputs['View Distance'], hz.inputs['Value'])
hp = N.new('ShaderNodeMath'); hp.operation = 'POWER'; hp.inputs[1].default_value = 0.7; L.new(hz.outputs[0], hp.inputs[0])
em = N.new('ShaderNodeEmission'); em.inputs['Color'].default_value = SKY[0][1] + (1,); em.inputs['Strength'].default_value = 1.0
lp = N.new('ShaderNodeLightPath')
gate = N.new('ShaderNodeMath'); gate.operation = 'MULTIPLY'
L.new(hp.outputs[0], gate.inputs[0]); L.new(lp.outputs['Is Camera Ray'], gate.inputs[1])
ms = N.new('ShaderNodeMixShader'); L.new(gate.outputs[0], ms.inputs[0]); L.new(bs.outputs[0], ms.inputs[1]); L.new(em.outputs[0], ms.inputs[2])
L.new(ms.outputs[0], N['Material Output'].inputs['Surface'])
g.data.materials.append(gm)
if MODE == 'fg':
    g.is_shadow_catcher = True

# world: camera rays see the dusk ramp, everything else sees a constant warm fill
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; wn = w.node_tree; WN = wn.nodes; WL = wn.links
bg = WN['Background']; bg.inputs['Color'].default_value = FILL_COL + (1,); bg.inputs['Strength'].default_value = FILL_E
wtc = WN.new('ShaderNodeTexCoord'); wsx = WN.new('ShaderNodeSeparateXYZ'); WL.new(wtc.outputs['Generated'], wsx.inputs[0])
cr = WN.new('ShaderNodeValToRGB'); ramp = cr.color_ramp; ramp.interpolation = 'B_SPLINE'
while len(ramp.elements) < len(SKY): ramp.elements.new(0.5)
for e, (p, c) in zip(ramp.elements, SKY): e.position = p; e.color = c + (1,)
WL.new(wsx.outputs['Z'], cr.inputs[0])
bg2 = WN.new('ShaderNodeBackground'); WL.new(cr.outputs['Color'], bg2.inputs['Color'])
wlp = WN.new('ShaderNodeLightPath'); wmx = WN.new('ShaderNodeMixShader')
WL.new(wlp.outputs['Is Camera Ray'], wmx.inputs[0]); WL.new(bg.outputs[0], wmx.inputs[1]); WL.new(bg2.outputs[0], wmx.inputs[2])
WL.new(wmx.outputs[0], WN['World Output'].inputs['Surface'])

# camera
cdat = bpy.data.cameras.new('cam'); cdat.sensor_fit = 'HORIZONTAL'; cdat.sensor_width = 36; cdat.lens = LENS; cdat.shift_y = SHIFT_Y
cdat.clip_end = 5000
co = bpy.data.objects.new('cam', cdat); sc.collection.objects.link(co); sc.camera = co
co.location = CAM_LOC
co.rotation_euler = (mathutils.Vector(CAM_TGT) - mathutils.Vector(CAM_LOC)).to_track_quat('-Z', 'Y').to_euler()

# lights
def sun(name, energy, col, el, az_deg, angle):
    """az_deg: bearing of the light's position, measured in the ground plane from -Y (front) toward -X (left) positive."""
    ld = bpy.data.lights.new(name, 'SUN'); ld.energy = energy; ld.color = col; ld.angle = math.radians(angle)
    ob = bpy.data.objects.new(name, ld); sc.collection.objects.link(ob)
    a, e = math.radians(az_deg), math.radians(el)
    pos = mathutils.Vector((-math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    ob.rotation_euler = (-pos).to_track_quat('-Z', 'Y').to_euler()
    return ob
cam_bearing = math.degrees(math.atan2(-CAM_LOC[0], -CAM_LOC[1]))   # camera bearing in the same convention
key = sun('key_sun', SUN_E, SUN_COL, SUN_EL, cam_bearing - SUN_AZ_OFF, 1.2)
rim = sun('rim_sun', RIM_E, RIM_COL, RIM_EL, RIM_AZ, 4.0)
if MODE == 'fg':
    # sun shadows go into the bg plate; fg only keeps the soft contact (fill occlusion) on the catcher
    for l in (key, rim):
        l.light_linking.receiver_collection = mc
if MODE == 'bg':
    for o in mon_objs:
        o.visible_camera = False; o.visible_glossy = False

print('CAM_BEARING', round(cam_bearing, 1), 'SUN_BEARING', round(cam_bearing - SUN_AZ_OFF, 1))
sc.render.filepath = OUT
t0 = time.time(); bpy.ops.render.render(write_still=True)
print('RENDER_SECONDS', round(time.time() - t0, 1), MODE, sc.render.resolution_x, sc.render.resolution_y, SAMP)
if SAVE:
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=SAVE)
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_mainfile()
