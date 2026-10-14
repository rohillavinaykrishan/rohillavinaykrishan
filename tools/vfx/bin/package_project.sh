#!/bin/bash
# Delivery: zip a whole studio project - every working file EXCEPT rendered video.
#
#   package_project.sh projects/<name> [out.zip] [--with-caches] [--full]
#
# Included: brief/treatment/shot list/EDL, notes and reviews, all scripts (.py/.sh/.html),
# packed .blend files (textures embedded, opens on any computer with Blender 5.2+),
# source images and audio, stems/SFX/masters, subtitles, thumbnails, storyboards, stills.
# Excluded: video files (.mp4 .mov .webm .mkv .avi .m4v), rendered frame sequences
# (name.0001.png ...), Blender .blend1 backups, simulation caches (unless --with-caches).
# Working stills over 2 MB (QC frames, contact sheets) become high-quality JPGs to keep the zip
# phone-friendly; source/ and deliver/ are never touched. --full keeps every file original.
# Default output: projects/<name>/deliver/<name>_project_files.zip
set -euo pipefail

proj="${1:-}"
[ -d "$proj" ] || { sed -n '2,14p' "$0"; exit 2; }
proj="$(realpath "$proj")"; name="$(basename "$proj")"
out="$proj/deliver/${name}_project_files.zip"; caches=0; full=0
for a in "${@:2}"; do
  case "$a" in --with-caches) caches=1 ;; --full) full=1 ;; *.zip) out="$(realpath -m "$a")" ;; esac
done

stage="$(mktemp -d)/$name"; mkdir -p "$stage"
trap 'rm -rf "$(dirname "$stage")"' EXIT

is_excluded() {
  local rel="$1" lower="${1,,}"
  case "$lower" in
    *.mp4|*.mov|*.webm|*.mkv|*.avi|*.m4v|*.blend1|*.blend2) return 0 ;;
    */__pycache__/*|*/.html2png_*|*.pyc) return 0 ;;
  esac
  [[ "$lower" =~ \.[0-9]{3,6}\.(png|jpg|jpeg|exr|tif|tiff)$ ]] && return 0      # render frame sequences
  [ $caches = 0 ] && [[ "$lower" =~ (^|/)(cache|caches|bake|blendcache_[^/]*)/ ]] && return 0
  return 1
}

kept=0; skipped=0; skipped_bytes=0
while IFS= read -r -d '' f; do
  rel="${f#$proj/}"
  case "$rel" in *_project_files.zip) continue ;; esac  # earlier packages of this project
  if is_excluded "$rel"; then
    skipped=$((skipped + 1)); skipped_bytes=$((skipped_bytes + $(stat -c%s "$f")))
  else
    mkdir -p "$stage/$(dirname "$rel")"; cp -p "$f" "$stage/$rel"; kept=$((kept + 1))
  fi
done < <(find "$proj" -type f -print0)

# Shrink big working stills (not source/ or deliver/) to JPG q92 unless --full.
shrunk=0
if [ $full = 0 ]; then
  while IFS= read -r -d '' f; do
    rel="${f#$stage/}"
    case "$rel" in source/*|deliver/*) continue ;; esac
    if [ "$(stat -c%s "$f")" -gt 2097152 ]; then
      convert "$f" -quality 92 "${f%.*}.jpg" && rm -f "$f" && shrunk=$((shrunk + 1))
    fi
  done < <(find "$stage" -type f \( -iname '*.png' -o -iname '*.tif' -o -iname '*.tiff' \) -print0)
fi

# Pack every .blend so textures/images travel inside it and paths don't break.
blends=0
while IFS= read -r -d '' b; do
  blender -b "$b" --python-expr '
import bpy
try:
    bpy.ops.file.make_paths_relative()
    bpy.ops.file.pack_all()
except Exception as e:
    print("pack warning:", e)
bpy.ops.wm.save_mainfile(compress=True)' >/dev/null 2>&1 && blends=$((blends + 1)) || echo "WARNING: could not pack $b"
  rm -f "$b"1
done < <(find "$stage" -name '*.blend' -print0)

cat > "$stage/README.md" <<EOF
# $name - project files

Everything the AI studio made for this job, except rendered video
(the finished videos are delivered separately).

| Folder / file | What it is |
|---|---|
| brief.md, treatment.md, shotlist.md, cg_plan.md, spec.json | the plan: your brief, the director's treatment, shot list, specs |
| source/ | your original song and images (restored versions are under shots/source/) |
| shots/<shot>/<department>/v###/ | each artist's work per version: notes.md, scripts, .blend files, stills, audio |
| shots/edit/ | editor (edl.json), sound designer, storyboard and release-package work |
| review/ | team-lead QC reports, supervisor and director notes, contact sheets |
| deliver/ | delivery extras that are not video: thumbnails, subtitles (.srt), audio masters, YouTube text |

- .blend files are packed (textures inside). Open them with Blender 5.2 or newer (free, blender.org) on a computer.
- Scripts (.py/.sh) rebuild each step; notes.md in every folder lists the exact commands used.
- Not included: video files, rendered frame sequences$( [ $caches = 0 ] && echo ", simulation caches (re-bake in Blender)").

- Working stills over 2 MB were saved as high-quality JPG ($shrunk file(s)) to keep this zip small.

Packaged $(date -u +%Y-%m-%d): $kept files, $blends .blend file(s).
EOF

mkdir -p "$(dirname "$out")"; rm -f "$out"
(cd "$(dirname "$stage")" && zip -qr -9 "$out" "$name")
unzip -tq "$out" >/dev/null
echo "wrote $out ($(du -h "$out" | cut -f1), $((kept + 1)) files incl. README, $blends packed .blend, $shrunk stills to JPG; skipped $skipped render/video files = $((skipped_bytes / 1048576)) MB)"
