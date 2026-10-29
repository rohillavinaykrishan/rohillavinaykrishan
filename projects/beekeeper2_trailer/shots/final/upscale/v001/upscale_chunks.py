"""AI-upscale the trailer picture (2.39 crop) with Real-ESRGAN general-x4v3, in resumable 240-frame chunks.
Output: chunks/c###.mp4 at 3840x1608, 24000/1001 fps, source frames 0..1807 (source t 0-75.38)."""
import subprocess, sys, os, numpy as np, torch
from spandrel import ModelLoader
SRC = sys.argv[1]; OUT = 'chunks'; os.makedirs(OUT, exist_ok=True)
W, H, N, CH = 1280, 536, 1808, 240
torch.set_num_threads(4)
m = ModelLoader().load_from_file('/root/.cache/vfx-studio/realesr-general-x4v3.pth').eval()
for c in range(0, N, CH):
    dst = f'{OUT}/c{c//CH:03d}.mp4'
    if os.path.exists(dst): continue
    n = min(CH, N - c)
    rd = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', SRC, '-vf', f"select='between(n,{c},{c+n-1})',crop={W}:{H}:0:92",
        '-vsync', '0', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    wr = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '5120x2144',
        '-r', '24000/1001', '-i', '-', '-vf', 'scale=3840:1608:flags=area', '-c:v', 'libx264', '-preset', 'fast',
        '-crf', '10', '-pix_fmt', 'yuv420p', dst + '.part.mp4'], stdin=subprocess.PIPE)
    for i in range(n):
        f = np.frombuffer(rd.stdout.read(W * H * 3), np.uint8).reshape(H, W, 3)
        if f.max() < 12:  # black frame: skip the model
            y = np.zeros((H * 4, W * 4, 3), np.uint8)
        else:
            x = torch.from_numpy(f.copy()).permute(2, 0, 1).float().div(255).unsqueeze(0)
            with torch.inference_mode():
                y = m(x)[0].permute(1, 2, 0).clamp(0, 1).mul(255).round().byte().numpy()
        wr.stdin.write(y.tobytes())
        print(f'chunk {c//CH} frame {c+i}/{N}', flush=True)
    wr.stdin.close(); wr.wait(); rd.wait()
    os.rename(dst + '.part.mp4', dst)
print('DONE')
