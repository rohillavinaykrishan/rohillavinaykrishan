"""Multi-object SAM 2 tracker with keyframe prompts (based on tools/vfx/bin/sam_roto.py).
usage: vfx-python sam_multi.py plate_dir prompts.json out_dir
prompts.json: {"obj_name": {"frame": [[x,y,label], ...], ...}, ...}  label 1=pos 0=neg
Writes out_dir/<obj>/m.%04d.png (binary 0/255, from SAM logits>0)."""
import json, sys, tempfile, subprocess
from pathlib import Path
import numpy as np, torch, cv2
from sam2.build_sam import build_sam2_video_predictor

plate, prompts, out = Path(sys.argv[1]), json.load(open(sys.argv[2])), Path(sys.argv[3])
ckpt = Path.home() / ".cache/vfx-studio/sam2.1_hiera_tiny.pt"
pred = build_sam2_video_predictor("configs/sam2.1/sam2.1_hiera_t.yaml", str(ckpt), device="cpu")
names = list(prompts)
files = sorted(plate.glob("plate.*.png"))
with tempfile.TemporaryDirectory() as tmp:
    for i, f in enumerate(files):
        cv2.imwrite(f"{tmp}/{i:05d}.jpg", cv2.imread(str(f)), [cv2.IMWRITE_JPEG_QUALITY, 95])
    with torch.inference_mode():
        st = pred.init_state(video_path=tmp)
        first = {}
        for oid, n in enumerate(names, 1):
            for fr, pts in prompts[n].items():
                pts = np.array(pts, dtype=np.float32)
                pred.add_new_points_or_box(st, frame_idx=int(fr), obj_id=oid,
                                           points=pts[:, :2], labels=pts[:, 2].astype(np.int32))
        masks = {}
        for rev in (False, True):
            for idx, oids, logits in pred.propagate_in_video(st, reverse=rev):
                for k, oid in enumerate(oids):
                    m = (logits[k, 0] > 0).numpy()
                    key = (idx, oid)
                    masks[key] = m if key not in masks else (masks[key] | m)
                if idx % 10 == 0:
                    print("rev" if rev else "fwd", idx, flush=True)
for oid, n in enumerate(names, 1):
    d = out / n; d.mkdir(parents=True, exist_ok=True)
    for i in range(len(files)):
        m = masks.get((i, oid))
        img = np.zeros((536, 1280), np.uint8) if m is None else (m.astype(np.uint8) * 255)
        cv2.imwrite(str(d / f"m.{i:04d}.png"), img)
print("done", names)
