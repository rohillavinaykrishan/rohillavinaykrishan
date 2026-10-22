# Monument asset builder (treatment 9.3): Unbounded 900 "VINAY/KRISHAN/ROHILLA", stacked,
# extrude 0.30 m, bevel 0.02 m (res 3), converted to mesh, on a 7.8 x 1.0 x 0.24 m plinth.
# Local frame: plinth centred at origin, base on z=0, letters face -Y. Parent = empty "MONUMENT".
import bpy, math, mathutils

FONT = '/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/director/v001/fonts/Unbounded-900.ttf'
TEXT = 'VINAY\nKRISHAN\nROHILLA'
WIDTH = 7.2
DEPTH = 0.30
BEVEL = 0.02
PLINTH = (7.8, 1.0, 0.24)
SPACE_LINE = 0.64
ROUGH = 0.55
COAT = 0.0


def srgb2lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hexlin(h):
    h = h.lstrip('#')
    return tuple(srgb2lin(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (1.0,)


def bone_material(name='bone', text_base=0.24, bump=0.05):
    """Principled bone plaster + sand dust on the lower 15 cm (world Z) + noise bump."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    b = N['Principled BSDF']
    b.inputs['Roughness'].default_value = ROUGH
    b.inputs['Coat Weight'].default_value = COAT; b.inputs['Coat Roughness'].default_value = 0.35
    geo = N.new('ShaderNodeNewGeometry')
    sep = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'], sep.inputs[0])
    # dust mask: 1 at z_base, 0 at z_base+0.15 (two bases: plinth foot and letter foot)
    def ramp(base):
        mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = base
        mr.inputs['From Max'].default_value = base + 0.15; mr.inputs['To Min'].default_value = 1.0
        mr.inputs['To Max'].default_value = 0.0; mr.clamp = True
        L.new(sep.outputs['Z'], mr.inputs['Value']); return mr
    r1 = ramp(0.0); r2 = ramp(text_base)
    # only below the letter foot band counts for r2 (z>=text_base) - fine because r2=1 for z<text_base
    # and the plinth body is already covered; use max of r1 and r2 restricted
    mx = N.new('ShaderNodeMath'); mx.operation = 'MAXIMUM'
    # r2 on plinth (z < text_base) would dust the whole plinth: gate it with z >= text_base - 0.001
    gt = N.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = text_base - 0.002
    L.new(sep.outputs['Z'], gt.inputs[0])
    g2 = N.new('ShaderNodeMath'); g2.operation = 'MULTIPLY'
    L.new(r2.outputs[0], g2.inputs[0]); L.new(gt.outputs[0], g2.inputs[1])
    L.new(r1.outputs[0], mx.inputs[0]); L.new(g2.outputs[0], mx.inputs[1])
    # break the gradient with noise
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 9.0; nz.inputs['Detail'].default_value = 6
    pw = N.new('ShaderNodeMath'); pw.operation = 'MULTIPLY_ADD'
    L.new(nz.outputs['Fac'], pw.inputs[0]); pw.inputs[1].default_value = 0.6; pw.inputs[2].default_value = -0.3
    ad = N.new('ShaderNodeMath'); ad.operation = 'ADD'; ad.use_clamp = True
    L.new(mx.outputs[0], ad.inputs[0]); L.new(pw.outputs[0], ad.inputs[1])
    sm = N.new('ShaderNodeMath'); sm.operation = 'POWER'; sm.inputs[1].default_value = 1.4
    L.new(ad.outputs[0], sm.inputs[0])
    col = N.new('ShaderNodeMix'); col.data_type = 'RGBA'
    col.inputs['A'].default_value = hexlin('#E9E1D3'); col.inputs['B'].default_value = hexlin('#CDB08A')
    L.new(sm.outputs[0], col.inputs['Factor'])
    L.new(col.outputs['Result'], b.inputs['Base Color'])
    rg = N.new('ShaderNodeMapRange'); rg.inputs['To Min'].default_value = ROUGH; rg.inputs['To Max'].default_value = 0.9
    L.new(sm.outputs[0], rg.inputs['Value']); L.new(rg.outputs[0], b.inputs['Roughness'])
    # subtle plaster bump
    nz2 = N.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 40.0; nz2.inputs['Detail'].default_value = 10
    bm = N.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = bump; bm.inputs['Distance'].default_value = 0.01
    L.new(nz2.outputs['Fac'], bm.inputs['Height']); L.new(bm.outputs['Normal'], b.inputs['Normal'])
    return m


def build(scene, name='MONUMENT'):
    coll = scene.collection
    root = bpy.data.objects.new(name, None); coll.objects.link(root)
    fnt = bpy.data.fonts.load(FONT, check_existing=True)
    td = bpy.data.curves.new('name_txt', 'FONT'); td.body = TEXT; td.font = fnt
    td.align_x = 'CENTER'; td.align_y = 'BOTTOM'; td.space_line = SPACE_LINE; td.size = 1.0
    to = bpy.data.objects.new('name_txt', td); coll.objects.link(to)
    bpy.context.view_layer.update()
    bb = [mathutils.Vector(c) for c in to.bound_box]
    wd = max(v.x for v in bb) - min(v.x for v in bb)
    td.size = WIDTH / wd
    td.extrude = DEPTH / 2 - BEVEL; td.bevel_depth = BEVEL; td.bevel_resolution = 3
    bpy.context.view_layer.update()
    # convert to mesh
    for o in bpy.context.view_layer.objects: o.select_set(False)
    bpy.context.view_layer.objects.active = to; to.select_set(True)
    bpy.ops.object.convert(target='MESH')
    to = bpy.context.view_layer.objects.active; to.name = 'name_mesh'
    to.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.view_layer.update()
    bb = [to.matrix_world @ mathutils.Vector(c) for c in to.bound_box]
    cxm = (max(v.x for v in bb) + min(v.x for v in bb)) / 2
    to.location = (-cxm, 0, PLINTH[2] - min(v.z for v in bb))
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for p in to.data.polygons: p.use_smooth = False
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, PLINTH[2] / 2))
    pb = bpy.context.active_object; pb.name = 'plinth'; pb.scale = PLINTH
    bpy.ops.object.transform_apply(scale=True)
    bv = pb.modifiers.new('bev', 'BEVEL'); bv.width = 0.012; bv.segments = 2
    mt = bone_material('bone_text', PLINTH[2]); mp = bone_material('bone_plinth', PLINTH[2])
    to.data.materials.append(mt); pb.data.materials.append(mp)
    for o in (to, pb):
        o.parent = root
        if o.name not in coll.objects: pass
    bpy.context.view_layer.update()
    bb = [to.matrix_world @ mathutils.Vector(c) for c in to.bound_box]
    dims = dict(width=max(v.x for v in bb) - min(v.x for v in bb), height=max(v.z for v in bb),
                depth=max(v.y for v in bb) - min(v.y for v in bb))
    print('MONUMENT_DIMS', dims)
    return root, to, pb, dims
