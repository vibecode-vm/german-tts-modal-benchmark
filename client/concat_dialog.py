"""Concatenate the 11 dialog lines per model into one continuous MP3.

Inserts 250 ms silence between turns. Output: audio_mp3/dialog_full_{model}.mp3.
"""

import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
WAV = ROOT / "audio_out"
MP3 = ROOT / "audio_mp3"
MP3.mkdir(exist_ok=True)

MODELS = ["piper", "thorsten", "mms", "xtts"]
DIALOG_ORDER = [
    "00_agent", "01_agent", "02_user", "03_agent", "04_user",
    "05_agent", "06_agent", "07_user", "08_agent", "09_user", "10_agent",
]
GAP_MS = 250


def main():
    for model in MODELS:
        parts = []
        missing = []
        for sid in DIALOG_ORDER:
            f = WAV / f"{model}__dialog__{sid}.wav"
            if not f.exists():
                missing.append(sid); continue
            parts.append(f)
        if missing:
            print(f"  {model}: skip ({len(missing)} missing samples)")
            continue
        out_wav = WAV / f"dialog_full_{model}.wav"
        out_mp3 = MP3 / f"dialog_full_{model}.mp3"

        # Build a concat filter with silence between segments
        n = len(parts)
        inputs = []
        for p in parts:
            inputs += ["-i", str(p)]
        # Silence generator
        inputs += ["-f", "lavfi", "-i", f"anullsrc=channel_layout=mono:sample_rate=22050"]

        # filter_complex: interleave audio with silence
        chunks = []
        labels = []
        for i in range(n):
            chunks.append(f"[{i}:a]aresample=22050[a{i}]")
            labels.append(f"[a{i}]")
            if i < n - 1:
                chunks.append(f"[{n}:a]atrim=0:{GAP_MS/1000.0}[s{i}]")
                labels.append(f"[s{i}]")
        filter_chain = ";".join(chunks) + ";" + "".join(labels) + f"concat=n={2*n-1}:v=0:a=1[out]"

        # WAV first
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
        cmd += inputs
        cmd += ["-filter_complex", filter_chain, "-map", "[out]", str(out_wav)]
        subprocess.run(cmd, check=True)

        # Then MP3
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(out_wav), "-codec:a", "libmp3lame", "-b:a", "128k", str(out_mp3),
        ], check=True)

        # Duration
        d = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(out_mp3)],
            capture_output=True, text=True, check=True,
        )
        sec = float(d.stdout.strip())
        size_kb = out_mp3.stat().st_size // 1024
        print(f"  {model:<10}  {sec:.1f}s  {size_kb}KB  -> {out_mp3.name}")


if __name__ == "__main__":
    main()
