"""Blender look library: one call restyles every mesh in a scene.

Use from your own bpy script:
    import sys; sys.path.append("/home/user/rohillavinaykrishan/tools/vfx/blender")
    import looks; looks.apply(bpy.context.scene, "toon")

Or render the demo scene in every look (contact sheet material):
    blender -b -P tools/vfx/blender/looks.py -- --demo OUT_DIR [--looks toon,neon] [--res 480x270]

Looks: realistic, toon, ink, sketch, neon, hologram, clay, xray, gold, glass, retro.
Toon needs Eevee (run Blender under `xvfb-run -a`); the rest render in Cycles.
Glow/pixel/scanline post looks are applied afterwards with tools/vfx/bin/post_look.sh.
"""
import math
import sys

import bpy

LOOKS = ["realistic", "toon", "ink", "sketch", "neon", "hologram", "clay", "xray", "gold", "glass", "retro"]
EEVEE_LOOKS = {"toon"}


def _mat(name):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    return m, nt, out


def _principled(name, color, metallic=0.0, rough=0.5, transmission=0.0, ior=1.45):
    m, nt, out = _mat(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    b.inputs["Transmission Weight"].default_value = transmission
    b.inputs["IOR"].default_value = ior
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    return m


def _toon(color):
    """Cel shading: diffuse -> Shader to RGB -> constant colour ramp (Eevee only)."""
    m, nt, out = _mat("toon")
    d = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = 0.0, (color[0] * .25, color[1] * .25, color[2] * .35, 1)
    els[1].position, els[1].color = 0.55, (*color, 1)
    mid = els.new(0.18)
    mid.color = (color[0] * .6, color[1] * .6, color[2] * .7, 1)
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(d.outputs[0], s2r.inputs[0])
    nt.links.new(s2r.outputs["Color"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


def _emission_fresnel(name, color, strength, edge_power=1.0, transparent=True):
    """Glowing edges, see-through centre (hologram / x-ray)."""
    m, nt, out = _mat(name)
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    pw = nt.nodes.new("ShaderNodeMath")
    pw.operation, pw.inputs[1].default_value = "POWER", edge_power
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    em.inputs["Strength"].default_value = strength
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lw.outputs["Facing"], pw.inputs[0])
    nt.links.new(pw.outputs[0], mix.inputs["Fac"])
    nt.links.new(tr.outputs[0] if transparent else em.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    m.surface_render_method = "BLENDED"
    return m


def _emission(name, color, strength):
    m, nt, out = _mat(name)
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


def _world(color, strength=1.0):
    w = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = w
    if w.node_tree is None:
        w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes.get("Background")
    if bg is None:
        nt.nodes.clear()
        bg = nt.nodes.new("ShaderNodeBackground")
        nt.links.new(bg.outputs[0], nt.nodes.new("ShaderNodeOutputWorld").inputs["Surface"])
    bg.inputs["Color"].default_value = (*color, 1)
    bg.inputs["Strength"].default_value = strength


def _freestyle(scene, thickness, color=(0, 0, 0)):
    scene.render.use_freestyle = True
    scene.render.line_thickness_mode = "ABSOLUTE"
    for vl in scene.view_layers:
        vl.use_freestyle = True
        fs = vl.freestyle_settings
        if not fs.linesets:
            fs.linesets.new("LineSet")
        for ls in fs.linesets:
            if ls.linestyle is None:
                ls.linestyle = bpy.data.linestyles.new("LineStyle")
            ls.linestyle.thickness = thickness
            ls.linestyle.color = color
            ls.select_by_visibility = True
            ls.select_crease = ls.select_silhouette = ls.select_border = True


def _set_all(mat_fn):
    for i, ob in enumerate(o for o in bpy.context.scene.objects if o.type == "MESH"):
        ob.data.materials.clear()
        ob.data.materials.append(mat_fn(i, ob))


def _wire():
    for ob in [o for o in bpy.context.scene.objects if o.type == "MESH"]:
        if "is_ground" in ob:
            continue
        w = ob.modifiers.new("neon_wire", "WIREFRAME")
        w.thickness, w.use_replace = 0.02, True
        ob.modifiers.move(len(ob.modifiers) - 1, 0)  # wire the base mesh, not the subdivided one


PALETTE = [(.9, .25, .2), (.2, .55, .95), (.95, .75, .15), (.3, .85, .45), (.75, .35, .9)]


def apply(scene, look):
    """Restyles every mesh in `scene`. Objects with a custom property
    "is_ground" are treated as floor/backdrop."""
    if look not in LOOKS:
        raise ValueError(f"unknown look {look!r}; choose from {LOOKS}")
    scene.render.engine = "BLENDER_EEVEE" if look in EEVEE_LOOKS else "CYCLES"
    if scene.render.engine == "CYCLES":
        scene.cycles.device = "CPU"
        scene.cycles.use_denoising = True
        scene.cycles.samples = scene.cycles.samples if scene.cycles.samples <= 128 else 64
    scene.render.use_freestyle = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "None"
    ground = lambda ob: "is_ground" in ob  # noqa: E731

    if look == "realistic":
        _world((.05, .06, .08), 1)
        _set_all(lambda i, ob: _principled("real", (.6, .6, .6) if ground(ob) else PALETTE[i % 5], rough=.4))
    elif look == "toon":
        _world((.85, .9, 1.0), 1)
        scene.view_settings.view_transform = "Standard"
        _freestyle(scene, 2.5)
        _set_all(lambda i, ob: _toon((.95, .95, .9) if ground(ob) else PALETTE[i % 5]))
    elif look == "ink":
        _world((1, 1, 1), 1)
        scene.view_settings.view_transform = "Standard"
        _freestyle(scene, 3.0)
        _set_all(lambda i, ob: _emission("paper", (1, 1, 1) if ground(ob) else (.97, .95, .9), 1))
    elif look == "sketch":
        _world((.93, .9, .82), 1)
        scene.view_settings.view_transform = "Standard"
        _freestyle(scene, 1.5, (.2, .17, .14))
        for vl in scene.view_layers:
            ls = vl.freestyle_settings.linesets[0].linestyle
            ls.chaining = "SKETCHY"
            ls.rounds = 3
        _set_all(lambda i, ob: _emission("paper", (.93, .9, .82), 1))
    elif look == "neon":
        _world((0, 0, 0), 0)
        _wire()
        neon = [(1, .1, .6), (.1, .9, 1), (.6, .2, 1), (1, .5, .05)]
        _set_all(lambda i, ob: _principled("floor", (.01, .01, .015), rough=.15) if ground(ob)
                 else _emission("neon", neon[i % 4], 5))
    elif look == "hologram":
        _world((0, .005, .01), 1)
        _set_all(lambda i, ob: _principled("floor", (.01, .02, .03), rough=.2) if ground(ob)
                 else _emission_fresnel("holo", (.1, .8, 1), 6, 1.5))
    elif look == "xray":
        _world((0, 0, 0), 0)
        _set_all(lambda i, ob: _emission("void", (0, 0, 0), 0) if ground(ob)
                 else _emission_fresnel("xray", (.85, .95, 1), 3, 2.5))
    elif look == "clay":
        _world((.8, .8, .8), .6)
        _set_all(lambda i, ob: _principled("clay", (.75, .72, .68), rough=.9))
    elif look == "gold":
        _world((.03, .03, .03), 1)
        _set_all(lambda i, ob: _principled("floor", (.02, .02, .02), rough=.1) if ground(ob)
                 else _principled("gold", (1, .7, .25), metallic=1, rough=.2))
    elif look == "glass":
        _world((.6, .7, .8), 1)
        _set_all(lambda i, ob: _principled("floor", (.9, .9, .9), rough=.6) if ground(ob)
                 else _principled("glass", (.9, .97, 1), rough=0, transmission=1))
    elif look == "retro":
        _world((.15, .05, .25), 1)
        retro = [(1, .3, .5), (.3, .9, .9), (1, .85, .3)]
        _set_all(lambda i, ob: _emission("grid", (.15, .02, .3), 1) if ground(ob)
                 else _principled("retro", retro[i % 3], rough=.35))
        scene.view_settings.look = "AgX - Punchy"


def demo_scene():
    s = bpy.context.scene
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    bpy.ops.mesh.primitive_plane_add(size=40)
    bpy.context.object["is_ground"] = True
    bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 1.05), rotation=(0, 0, -0.35))
    ob = bpy.context.object
    ob.modifiers.new("s", "SUBSURF").levels = 2
    bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_torus_add(location=(-2.3, .8, .55), rotation=(1.1, 0, .4), major_radius=.75, minor_radius=.28)
    bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=.6, location=(2.2, .6, .6))
    bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_cube_add(size=.8, location=(1.2, -1.2, .4), rotation=(0, 0, .6))
    bpy.ops.object.light_add(type="AREA", location=(3, -3, 5))
    bpy.context.object.data.energy, bpy.context.object.data.size = 900, 3
    bpy.ops.object.light_add(type="AREA", location=(-4, 1, 3))
    bpy.context.object.data.energy, bpy.context.object.data.size = 300, 4
    bpy.ops.object.camera_add(location=(0, -7.2, 2.6), rotation=(math.radians(76), 0, 0))
    s.camera = bpy.context.object
    s.cycles.samples = 32


def _main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--demo" not in argv:
        return
    out = argv[argv.index("--demo") + 1]
    looks = argv[argv.index("--looks") + 1].split(",") if "--looks" in argv else LOOKS
    w, h = (argv[argv.index("--res") + 1] if "--res" in argv else "480x270").split("x")
    for look in looks:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        demo_scene()
        s = bpy.context.scene
        s.render.resolution_x, s.render.resolution_y = int(w), int(h)
        apply(s, look)
        s.render.filepath = f"{out}/look_{look}.png"
        bpy.ops.render.render(write_still=True)
        print(f"LOOK_DONE {look}", flush=True)


if __name__ == "__main__":
    _main()
