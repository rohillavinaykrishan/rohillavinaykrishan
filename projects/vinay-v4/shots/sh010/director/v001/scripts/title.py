import bpy, math, mathutils, sys, time
argv=sys.argv[sys.argv.index('--')+1:]; OUT=argv[0]; RX=int(argv[1]); SAMP=int(argv[2])
D='/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/director/v001/'
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=SAMP; sc.cycles.use_denoising=True
sc.render.resolution_x=RX; sc.render.resolution_y=RX*16//9; sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - Base Contrast' if False else 'None'
fnt=bpy.data.fonts.load(D+'fonts/Unbounded-900.ttf')
td=bpy.data.curves.new('n','FONT'); td.body='VINAY\nKRISHAN\nROHILLA'; td.font=fnt; td.align_x='CENTER'; td.align_y='BOTTOM'; td.space_line=0.70; td.extrude=0.35; td.bevel_depth=0.03; td.bevel_resolution=3
to=bpy.data.objects.new('n',td); sc.collection.objects.link(to); bpy.context.view_layer.update()
bb=[mathutils.Vector(c) for c in to.bound_box]; wd=max(v.x for v in bb)-min(v.x for v in bb); s=7.2/wd
to.scale=(s,s,s); to.rotation_euler=(math.radians(90),0,0); to.location=(0,0,0.35*s)
bpy.context.view_layer.update(); bb=[to.matrix_world@mathutils.Vector(c) for c in to.bound_box]; to.location.z+=0.24-min(v.z for v in bb)
m=bpy.data.materials.new('bone'); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(0.80,0.74,0.64,1); b.inputs['Roughness'].default_value=0.5; to.data.materials.append(m)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0.0,0.12)); pb=bpy.context.active_object; pb.scale=(7.8,1.0,0.24); pb.data.materials.append(m)
bpy.ops.mesh.primitive_plane_add(size=400,location=(0,0,0)); g=bpy.context.active_object
gm=bpy.data.materials.new('sand'); gm.use_nodes=True; nt=gm.node_tree; bs=nt.nodes['Principled BSDF']; bs.inputs['Base Color'].default_value=(0.55,0.42,0.28,1); bs.inputs['Roughness'].default_value=0.95
nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=60; nz.inputs['Detail'].default_value=8; bm=nt.nodes.new('ShaderNodeBump'); bm.inputs['Strength'].default_value=0.25
nt.links.new(nz.outputs['Fac'],bm.inputs['Height']); nt.links.new(bm.outputs['Normal'],bs.inputs['Normal']); g.data.materials.append(gm)
sd=bpy.data.lights.new('sun','SUN'); sd.energy=5.0; sd.angle=math.radians(1.2); sd.color=(1.0,0.93,0.82); so=bpy.data.objects.new('sun',sd); sc.collection.objects.link(so)
az=math.radians(160); el=math.radians(24)
dirv=mathutils.Vector((-math.sin(az)*math.cos(el),-math.cos(az)*math.cos(el),-math.sin(el))); so.rotation_euler=dirv.to_track_quat('-Z','Y').to_euler()
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; bg=w.node_tree.nodes['Background']; bg.inputs['Color'].default_value=(0.86,0.80,0.70,1); bg.inputs['Strength'].default_value=0.30
nt=w.node_tree; tc=nt.nodes.new('ShaderNodeTexCoord'); sx=nt.nodes.new('ShaderNodeSeparateXYZ'); cr=nt.nodes.new('ShaderNodeValToRGB')
cr.color_ramp.elements[0].position=0.0; cr.color_ramp.elements[0].color=(0.62,0.45,0.28,1); cr.color_ramp.elements[1].position=0.45; cr.color_ramp.elements[1].color=(0.035,0.024,0.017,1)
lp=nt.nodes.new('ShaderNodeLightPath'); bg2=nt.nodes.new('ShaderNodeBackground'); mx=nt.nodes.new('ShaderNodeMixShader'); out=nt.nodes['World Output']
nt.links.new(tc.outputs['Generated'],sx.inputs[0]); nt.links.new(sx.outputs['Z'],cr.inputs[0]); nt.links.new(cr.outputs['Color'],bg2.inputs['Color'])
nt.links.new(bg.outputs[0],mx.inputs[1]); nt.links.new(bg2.outputs[0],mx.inputs[2]); nt.links.new(lp.outputs['Is Camera Ray'],mx.inputs[0]); nt.links.new(mx.outputs[0],out.inputs['Surface'])
w.mist_settings.start=10; 
cd=bpy.data.cameras.new('c'); cd.lens=30; cd.sensor_fit='VERTICAL'; cd.sensor_height=36; co=bpy.data.objects.new('c',cd); sc.collection.objects.link(co); sc.camera=co
co.location=(-1.8,-10.8,0.55); tgt=mathutils.Vector((0,0,2.5)); co.rotation_euler=(tgt-co.location).to_track_quat('-Z','Y').to_euler()
cd.shift_y=-0.05
sc.render.filepath=OUT; t0=time.time(); bpy.ops.render.render(write_still=True); print('RENDER_SECONDS',round(time.time()-t0,1),sc.render.resolution_x,sc.render.resolution_y)
bpy.ops.wm.save_as_mainfile(filepath=OUT.replace('.png','.blend'))
