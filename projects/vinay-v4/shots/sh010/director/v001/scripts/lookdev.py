import bpy, numpy as np, json, sys, time, math, mathutils
argv=sys.argv[sys.argv.index('--')+1:]
D='/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/director/v001/'
M=D+'cm3_beach/sparse_relax/0/'; FR=argv[0]; OUT=argv[1]; RX=int(argv[2]); SAMP=int(argv[3])
cam=[l.split() for l in open(M+'cameras.txt') if not l.startswith('#')][0]
w,h,f,cx,cy,k=int(cam[2]),int(cam[3]),*map(float,cam[4:8])
L=[l for l in open(M+'images.txt') if not l.startswith('#')]; imgs={}
for i in range(0,len(L),2):
    a=L[i].split(); imgs[a[9]]=(np.array(list(map(float,a[1:5]))),np.array(list(map(float,a[5:8]))))
def R(q):
    w_,x,y,z=q; return np.array([[1-2*(y*y+z*z),2*(x*y-z*w_),2*(x*z+y*w_)],[2*(x*y+z*w_),1-2*(x*x+z*z),2*(y*z-x*w_)],[2*(x*z-y*w_),2*(y*z+x*w_),1-2*(x*x+y*y)]])
gp=json.load(open(D+'ground_plane_beach.json')); n=np.array(gp['normal']); d=gp['d']; s=gp['scale_m_per_unit']
names=sorted(imgs); q,t=imgs[names[18]]; Rm=R(q); C18=-Rm.T@t
fwd=Rm.T@np.array([0,0,1.]); fwd=fwd-(fwd@n)*n; fwd/=np.linalg.norm(fwd); right=np.cross(fwd,n)
O=C18-(C18@n+d)*n
A=np.vstack([right,fwd,n])*s   # colmap world -> metres, ground z=0, cam18 at origin looking +y
def to_new(X): return A@(X-O)
# scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=SAMP; sc.cycles.use_denoising=True
sc.render.resolution_x=RX; sc.render.resolution_y=round(RX*h/w); sc.render.film_transparent=True
sc.view_settings.view_transform='Standard'
camd=bpy.data.cameras.new('cam'); camd.sensor_fit='HORIZONTAL'; camd.sensor_width=36; camd.lens=f/w*36
co=bpy.data.objects.new('cam',camd); sc.collection.objects.link(co); sc.camera=co
q,t=imgs[FR]; Rm=R(q); Cw=-Rm.T@t
Rn=A/s@Rm.T@np.diag([1,-1,-1])
mw=mathutils.Matrix.Identity(4)
for i in range(3):
    for j in range(3): mw[i][j]=Rn[i][j]
loc=to_new(Cw); mw[0][3],mw[1][3],mw[2][3]=loc
co.matrix_world=mw
# text
fnt=bpy.data.fonts.load(D+'fonts/Unbounded-900.ttf')
td=bpy.data.curves.new('name','FONT'); td.body='VINAY\nKRISHAN\nROHILLA'; td.space_line=0.92; td.font=fnt; td.align_x='CENTER'; td.extrude=0.30; td.bevel_depth=0.02; td.bevel_resolution=2; td.size=1.0
to=bpy.data.objects.new('name',td); sc.collection.objects.link(to)
bpy.context.view_layer.update()
bb=[to.matrix_world@mathutils.Vector(c) for c in to.bound_box]; wd=max(v.x for v in bb)-min(v.x for v in bb)
sz=7.2/wd; to.scale=(sz,sz,sz); to.rotation_euler=(math.radians(90),0,math.radians(-12)); bpy.context.view_layer.update(); bb=[to.matrix_world@mathutils.Vector(c) for c in to.bound_box]; to.location=(1.5,12.5,-min(v.z for v in bb))
mat=bpy.data.materials.new('bone'); mat.use_nodes=True; b=mat.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value=(0.83,0.78,0.70,1); b.inputs['Roughness'].default_value=0.55
to.data.materials.append(mat)
# shadow catcher
bpy.ops.mesh.primitive_plane_add(size=80,location=(0,15,0)); pl=bpy.context.active_object; pl.is_shadow_catcher=True
pm=bpy.data.materials.new('sand'); pm.use_nodes=True; pm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.62,0.50,0.36,1); pl.data.materials.append(pm)
# sun: backlight from front-right, elev 35
sd=bpy.data.lights.new('sun','SUN'); sd.energy=4.5; sd.angle=math.radians(1.5); sd.color=(1.0,0.95,0.86)
so=bpy.data.objects.new('sun',sd); sc.collection.objects.link(so)
az=math.radians(40); el=math.radians(35)
dirv=mathutils.Vector((-math.sin(az)*math.cos(el), -math.cos(az)*math.cos(el), -math.sin(el)))  # light travels toward camera-left & down
so.rotation_euler=dirv.to_track_quat('-Z','Y').to_euler()
wo=bpy.data.worlds.new('w'); sc.world=wo; wo.use_nodes=True; wo.node_tree.nodes['Background'].inputs['Color'].default_value=(0.80,0.76,0.70,1); wo.node_tree.nodes['Background'].inputs['Strength'].default_value=0.5
sc.render.filepath=OUT; t0=time.time(); bpy.ops.render.render(write_still=True); print('RENDER_SECONDS',round(time.time()-t0,1), sc.render.resolution_x, sc.render.resolution_y)
bpy.ops.wm.save_as_mainfile(filepath=OUT.replace('.png','.blend'))
