# render_check.py : blender -b solve_cam.blend -P render_check.py -- OS frames...
# renders the placeholder monument (Cycles 8 spp, pinhole, overscan OS at plate res) into scratch/render_check/
import bpy, sys
L = '/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/layout/v001/'
a = sys.argv[sys.argv.index('--')+1:]; OS = float(a[0]); FR = [int(x) for x in a[1:]]
sc = bpy.context.scene; cam = sc.camera.data
W, H = sc.render.resolution_x, sc.render.resolution_y
RW, RH = round(OS*W), round(OS*H)
sc.render.resolution_x, sc.render.resolution_y = RW, RH
cam.sensor_width = 36*RW/W          # keeps the px focal length: same lens, wider sensor
sc.cycles.samples = 8; sc.cycles.use_denoising = False; sc.render.film_transparent = True
sc.render.threads_mode = 'FIXED'; sc.render.threads = 2
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
for f in FR:
    sc.frame_set(f); sc.render.filepath = L+'scratch/render_check/pin.%04d.png' % f
    bpy.ops.render.render(write_still=True)
