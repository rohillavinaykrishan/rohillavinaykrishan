#!/usr/bin/env python3
"""Generate stills with FLUX and audio-synced clips with MiniMax-H3 via Hugging Face Spaces.

Reads HF_TOKEN from the environment (ZeroGPU quota is billed to that account).

  python tools/hf_media.py image "neon city at dusk" -o media/frame.png --size 544x960
  python tools/hf_media.py video "she sings to camera" --image media/frame.png \
      --audio song_clip.wav -o media/clip.mp4 --canvas "544x960 · 9:16 fast"
"""
import argparse
import os
import shutil
import sys

from gradio_client import Client, handle_file

FLUX_SPACE = "black-forest-labs/FLUX.1-schnell"
MINIMAX_SPACE = "multimodalart/minimax-h3-audio-to-video"
CANVASES = [
    "960x544 · 16:9 fast", "1024x576 · 16:9 fast", "1152x640 · 16:9", "1280x704 · 16:9",
    "1344x768 · 16:9 full", "544x960 · 9:16 fast", "640x1152 · 9:16", "768x1344 · 9:16 full",
    "544x544 · 1:1 fast", "768x768 · 1:1 full", "1024x1024 · 1:1 max", "768x576 · 4:3 fast",
    "1024x768 · 4:3 full", "576x768 · 3:4 fast", "768x1024 · 3:4 full",
    "1152x512 · 21:9 fast", "1536x672 · 21:9 full",
]


def client(space):
    token = os.environ.get("HF_TOKEN")
    if not token:
        sys.exit("HF_TOKEN is not set")
    return Client(space, token=token, verbose=False)


def save(src, out):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    shutil.copy(src, out)
    print(out)


def image(args):
    w, h = (int(x) for x in args.size.lower().split("x"))
    result, seed = client(FLUX_SPACE).predict(
        prompt=args.prompt, seed=args.seed or 0, randomize_seed=args.seed is None,
        width=w, height=h, num_inference_steps=args.steps, api_name="/infer",
    )
    print(f"seed={seed}", file=sys.stderr)
    save(result, args.output)


def video(args):
    c = client(MINIMAX_SPACE)
    duration = args.duration
    if duration is None and args.audio:
        duration = c.predict(audio_path=handle_file(args.audio), current=6, api_name="/audio_duration")
    result = c.predict(
        prompt=args.prompt,
        image_path=handle_file(args.image) if args.image else None,
        audio_path=handle_file(args.audio) if args.audio else None,
        canvas=args.canvas, duration=duration or 6, steps=args.steps,
        seed=args.seed, upsample=args.upsample, api_name="/generate",
    )
    vid = result[0] if isinstance(result, (list, tuple)) else result
    if isinstance(vid, dict):
        vid = vid.get("video") or vid.get("path")
    save(vid, args.output)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("image", help="FLUX.1-schnell text-to-image")
    i.add_argument("prompt")
    i.add_argument("-o", "--output", default="media/flux.webp")
    i.add_argument("--size", default="1024x1024", help="WxH, 256-2048")
    i.add_argument("--steps", type=int, default=4)
    i.add_argument("--seed", type=int)
    i.set_defaults(func=image)

    v = sub.add_parser("video", help="MiniMax-H3 first frame + soundtrack to video")
    v.add_argument("prompt")
    v.add_argument("--image", help="first frame (optional)")
    v.add_argument("--audio", help="soundtrack to drive the video (optional)")
    v.add_argument("-o", "--output", default="media/minimax.mp4")
    v.add_argument("--canvas", default=CANVASES[0], choices=CANVASES)
    v.add_argument("--duration", type=float, help="seconds; defaults to the audio length")
    v.add_argument("--steps", type=int, default=7)
    v.add_argument("--seed", type=int, default=42)
    v.add_argument("--upsample", action="store_true", help="let the Space expand the prompt")
    v.set_defaults(func=video)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
