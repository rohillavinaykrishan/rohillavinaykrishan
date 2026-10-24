#!/usr/bin/env python3
"""vinay-30s sh010 comp v001: assemble the master HyperFrames composition from the MG sub-comps.

Re-run any time an upstream part changes (./comp.sh build). It:
  * finds each MG's scene file (mograph/v001/<mg>/compositions/*.html with a <template>, or converts
    the MG's root index.html into a template scene), copies it into master/compositions/<id>.html with
    asset paths namespaced (assets/x -> assets/<id>/x, compositions/x -> compositions/<id>__x) and
    symlinks master/assets/<id> -> the MG's assets dir (so plate updates flow through);
  * writes a labelled placeholder scene for any part that has not landed yet;
  * writes three roots, identical except for the frame window:
      master/index.html  f0-749   (preview, proxy)
      half_a/index.html  f0-364   (4K half A; compositions/ and assets/ symlink to master/)
      half_b/index.html  f365-749 (4K half B: parts that started earlier are mounted at 0 with
                              data-media-start = the frames already played; verified to offset both
                              GSAP timelines and nested <video> clips)
  * writes ../status.json.
Frame windows come from cues.json-derived task ranges (MG1 f0-356, MG2 f336-386, MG3 f387-749).
"""
import json, os, re, sys, shutil

PRJ = "/home/user/rohillavinaykrishan/projects/vinay-30s"
SH = f"{PRJ}/shots/sh010"
V = f"{SH}/comp/v001"
M = f"{V}/master"
FPS = 25
W, H = 2160, 3840
TOTAL = 750
INK = "#07060A"

# id, upstream project dir, master frame in, frame out (exclusive), z-index (paint order)
PARTS = [
    ("mg1", f"{SH}/mograph/v001/mg1", 0, 357, 2),
    ("mg3", f"{SH}/mograph/v001/mg3", 387, 750, 3),
    ("mg2", f"{SH}/mograph/v001/mg2", 336, 387, 4),  # strike sits over MG1's charge tail
]
# timeline clock of each sub-comp: "local" (t=0 at its first frame) or "master" (t = master seconds;
# mounted at its first frame with data-media-start = that frame, so local time == master time)
CLOCK = {"mg1": "master", "mg2": "master", "mg3": "master"}
AUDIO = f"{SH}/sound/v001/master.wav"
AUDIO_FALLBACK = f"{SH}/director/v001/audio/bed_vinay30_v001.wav"
HALVES = {f"{M}/index.html": (0, 750), f"{V}/half_a/index.html": (0, 365), f"{V}/half_b/index.html": (365, 750)}

# comp-lead patches applied to the master COPY only: {id: [(old, new), ...]}, each must match exactly once
PATCHES = {}
pf = f"{V}/tools/patches.json"
if os.path.exists(pf):
    PATCHES = {k: [tuple(x) for x in v] for k, v in json.load(open(pf)).items()}


def find_scene(d, cid):
    """Return (path, kind) of the MG's mountable scene: 'template' or 'root'."""
    if not os.path.isdir(d):
        return None, None
    cdir = f"{d}/compositions"
    has_index = os.path.exists(f"{d}/index.html")
    if os.path.isdir(cdir):
        cands = sorted(f for f in os.listdir(cdir) if f.endswith(".html"))
        tmpl = [f for f in cands if "<template" in open(f"{cdir}/{f}").read()]
        # a single scene (or one named after the MG) is mounted directly when the MG root only hosts it
        pref = [f for f in tmpl if f.startswith(cid)]
        if pref:
            return f"{cdir}/{pref[0]}", "template"
        if len(tmpl) == 1 and not has_index:
            return f"{cdir}/{tmpl[0]}", "template"
    if has_index:
        return f"{d}/index.html", "root"
    return None, None


def namespace(html, ns):
    html = re.sub(r'(["\'(])assets/', r"\1assets/%s/" % ns, html)
    html = re.sub(r'(data-composition-src=["\'])compositions/', r"\1compositions/%s__" % ns, html)
    return html


def root_to_template(html, cid):
    """Convert an MG root index.html into a template scene with composition id `cid`."""
    head = re.search(r"<head[^>]*>(.*?)</head>", html, re.S | re.I)
    head = head.group(1) if head else ""
    styles = "\n".join(re.findall(r"<style[^>]*>.*?</style>", head, re.S | re.I))
    links = "\n".join(l for l in re.findall(r"<link[^>]*>", head, re.I) if "stylesheet" in l)
    hscripts = [s for s in re.findall(r"<script[^>]*>.*?</script>", head, re.S | re.I) if "gsap" not in s]
    body = re.search(r"<body[^>]*>(.*)</body>", html, re.S | re.I).group(1)
    m = re.search(r'data-composition-id="([^"]+)"', body)
    old = m.group(1)
    body = body.replace(f'data-composition-id="{old}"', f'data-composition-id="{cid}"', 1)
    body = body.replace(f'__timelines["{old}"]', f'__timelines["{cid}"]').replace(f"__timelines['{old}']", f'__timelines["{cid}"]')
    return f"<template>\n{links}\n{styles}\n{''.join(hscripts)}\n{body}\n</template>\n"


def comp_id(html):
    m = re.search(r'data-composition-id="([^"]+)"', html)
    return m.group(1) if m else None


def placeholder(cid, f0, f1):
    dur = (f1 - f0) / FPS
    return f"""<template>
  <style>
    #{cid}-ph {{ position: absolute; left: 160px; top: 2300px; width: 1840px; height: 840px; border: 6px dashed #FFC94D;
      color: #FFF8EC; font: 700 96px/1.3 sans-serif; text-align: center; padding-top: 200px; box-sizing: border-box; }}
    #{cid}-phf {{ position: absolute; left: 0; top: 3200px; width: 2160px; text-align: center; color: #E6DED2; font: 500 64px monospace; }}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}">
    <div id="{cid}-ph">PLACEHOLDER {cid.upper()}<br>f{f0}-f{f1 - 1}</div>
    <div id="{cid}-phf">0</div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      const o = {{ f: 0 }}, el = document.getElementById("{cid}-phf");
      tl.to(o, {{ f: {f1 - f0 - 1}, duration: {dur - 1 / FPS:.4f}, ease: "none",
        onUpdate: () => {{ el.textContent = "{cid} master f" + Math.round({f0} + o.f); }} }}, {(f0 / FPS if CLOCK.get(cid) == "master" else 0):.2f});
      window.__timelines["{cid}"] = tl;
    }})();
  </script>
</template>
"""


def apply_patches(cid, html):
    for old, new in PATCHES.get(cid, []):
        n = html.count(old)
        if n != 1:
            sys.exit(f"PATCH FAILED for {cid}: {n} matches for {old!r}")
        html = html.replace(old, new)
    return html


def relink(dst, src):
    if os.path.islink(dst):
        os.unlink(dst)
    elif os.path.isdir(dst):
        shutil.rmtree(dst)
    elif os.path.exists(dst):
        os.unlink(dst)
    os.symlink(src, dst)


def write_root(name, a, b, hosts, audio_rel):
    dur = (b - a) / FPS
    lines = []
    for cid, f0, f1, z in hosts:
        s, e = max(f0, a), min(f1, b)
        if s >= e:
            continue
        off = s - f0 + (f0 if CLOCK.get(cid) == "master" else 0)
        ms = f' data-media-start="{off / FPS:.2f}"' if off else ""
        lines.append(
            f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" '
            f'data-start="{(s - a) / FPS:.2f}"{ms} data-duration="{(e - s) / FPS:.2f}" data-track-index="{z}" '
            f'data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:{z}"></div>'
            f"  <!-- master f{s}-f{e - 1} -->")
    aud = ""
    if a == 0 and b == TOTAL:
        aud = (f'      <audio id="master-audio" class="clip" src="{audio_rel}" data-start="0" data-duration="{dur:.2f}" '
               f'data-track-index="9" data-volume="1"></audio>\n')
    html = f"""<!doctype html>
<!-- sh010 MASTER (comp lead). GENERATED by ../tools/build_master.py: edit the builder, then rebuild.
     2160x3840, 25 fps. This root = master f{a}-f{b - 1} ({b - a} frames). -->
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: {INK}; }}</style>
  </head>
  <body>
    <div id="main" data-composition-id="main" data-start="0" data-duration="{dur:.2f}" data-fps="{FPS}" data-width="{W}" data-height="{H}">
      <div id="master-bg" style="position:absolute;inset:0;background:{INK};z-index:0"></div>
{chr(10).join(lines)}
{aud}    </div>
    <script>window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
  </body>
</html>
"""
    d = os.path.dirname(name)
    os.makedirs(d, exist_ok=True)
    if d != M:
        for sub in ("compositions", "assets"):
            if not os.path.islink(f"{d}/{sub}"):
                os.symlink(f"{M}/{sub}", f"{d}/{sub}")
    open(name, "w").write(html)


def main():
    os.makedirs(f"{M}/compositions", exist_ok=True)
    os.makedirs(f"{M}/assets", exist_ok=True)
    for f in os.listdir(f"{M}/compositions"):
        os.unlink(f"{M}/compositions/{f}")
    status = {}
    hosts = []
    for cid, d, f0, f1, z in PARTS:
        src, kind = find_scene(d, cid)
        real = src is not None
        if real:
            html = open(src).read()
            if kind == "root":
                html = root_to_template(html, cid)
            else:
                ucid = comp_id(html)
                if ucid and ucid != cid:
                    html = html.replace(f'data-composition-id="{ucid}"', f'data-composition-id="{cid}"', 1)
                    html = html.replace(f'__timelines["{ucid}"]', f'__timelines["{cid}"]')
            html = namespace(html, cid)
            html = apply_patches(cid, html)
            # nested sub-comps of the MG come along, namespaced
            sdir = os.path.dirname(src) if kind == "template" else f"{d}/compositions"
            for n in re.findall(r'data-composition-src=["\']compositions/%s__([^"\']+)' % cid, html):
                sub = open(f"{d}/compositions/{n}").read()
                open(f"{M}/compositions/{cid}__{n}", "w").write(namespace(sub, cid))
            if os.path.isdir(f"{d}/assets"):
                relink(f"{M}/assets/{cid}", f"{d}/assets")
        else:
            html = placeholder(cid, f0, f1)
        open(f"{M}/compositions/{cid}.html", "w").write(html)
        status[cid] = {"src": src, "kind": kind, "real": real, "f_in": f0, "f_out_excl": f1,
                       "mtime": os.path.getmtime(src) if real else None}
        hosts.append((cid, f0, f1, z))

    os.makedirs(f"{M}/assets/audio", exist_ok=True)
    real_audio = os.path.exists(AUDIO)
    relink(f"{M}/assets/audio/master.wav", AUDIO if real_audio else AUDIO_FALLBACK)
    status["audio"] = {"src": AUDIO if real_audio else AUDIO_FALLBACK, "real": real_audio}

    for name, (a, b) in HALVES.items():
        write_root(name, a, b, hosts, "assets/audio/master.wav")

    json.dump(status, open(f"{V}/status.json", "w"), indent=1)
    for k, v in status.items():
        print(f"{k:6s} {'REAL' if v['real'] else 'placeholder'}  {v.get('src')}")


if __name__ == "__main__":
    main()
