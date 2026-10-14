"""Voice department: free offline text-to-speech (Piper).

  vfx-python tts.py "Welcome to the show" vo.wav
  vfx-python tts.py script.txt vo.wav --voice en_GB-alan-medium
  vfx-python tts.py "नमस्ते दोस्तों" vo.wav --voice hi_IN-pratham-medium
Voices: https://huggingface.co/rhasspy/piper-voices (name = <lang>_<REGION>-<name>-<quality>)
"""
import argparse
import wave
from pathlib import Path

from huggingface_hub import hf_hub_download
from piper import PiperVoice, SynthesisConfig

CACHE = Path.home() / ".cache" / "vfx-studio" / "piper"


def voice_files(name):
    lang_region, speaker, quality = name.split("-")
    lang = lang_region.split("_")[0]
    base = f"{lang}/{lang_region}/{speaker}/{quality}/{name}.onnx"
    onnx = hf_hub_download("rhasspy/piper-voices", base, cache_dir=CACHE)
    hf_hub_download("rhasspy/piper-voices", base + ".json", cache_dir=CACHE)
    return onnx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text", help="text, or a path to a .txt file")
    ap.add_argument("output", help=".wav")
    ap.add_argument("--voice", default="en_US-lessac-medium")
    ap.add_argument("--speed", type=float, default=1.0, help=">1 faster, <1 slower")
    args = ap.parse_args()

    text = Path(args.text).read_text(encoding="utf-8") if Path(args.text).is_file() else args.text
    voice = PiperVoice.load(voice_files(args.voice))
    with wave.open(args.output, "wb") as wav:
        voice.synthesize_wav(text, wav, syn_config=SynthesisConfig(length_scale=1 / args.speed))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
