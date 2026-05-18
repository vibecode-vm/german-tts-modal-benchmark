"""Piper TTS — German, CPU-only. The cheapest, fastest cold-start option.

Voice: `de_DE-thorsten-medium` (clean male voice, well-known German Piper voice).
"""
import io
import time
import wave

import modal

APP_NAME = "piper-de-tts"
SAMPLE_RATE = 22050  # Piper voices typically 22050

app = modal.App(APP_NAME)
voice_cache = modal.Volume.from_name("piper-voices", create_if_missing=True)
CACHE = "/voices"

image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("wget", "ca-certificates")
    .pip_install("piper-tts==1.3.0", "fastapi[standard]", "pydantic")
    .env({"PIPER_VOICES_DIR": CACHE})
)

with image.imports():
    import subprocess
    from pathlib import Path
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import Response
    from pydantic import BaseModel

    class TTSReq(BaseModel):
        text: str
        voice: str = "de_DE-thorsten-medium"   # also: de_DE-eva_k-x_low, de_DE-kerstin-low, de_DE-pavoque-low


VOICES = {
    "de_DE-thorsten-medium": ("https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx",
                              "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx.json"),
    "de_DE-eva_k-x_low":     ("https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/eva_k/x_low/de_DE-eva_k-x_low.onnx",
                              "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/eva_k/x_low/de_DE-eva_k-x_low.onnx.json"),
    "de_DE-kerstin-low":     ("https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/kerstin/low/de_DE-kerstin-low.onnx",
                              "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/kerstin/low/de_DE-kerstin-low.onnx.json"),
    "de_DE-pavoque-low":     ("https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/pavoque/low/de_DE-pavoque-low.onnx",
                              "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/pavoque/low/de_DE-pavoque-low.onnx.json"),
}


def _download_voice(voice: str) -> Path:
    cache = Path(CACHE) / voice
    cache.mkdir(parents=True, exist_ok=True)
    onnx = cache / f"{voice}.onnx"
    cfg  = cache / f"{voice}.onnx.json"
    if not onnx.exists() or not cfg.exists():
        if voice not in VOICES:
            raise ValueError(f"unknown voice: {voice}")
        u_onnx, u_cfg = VOICES[voice]
        subprocess.run(["wget", "-q", "-O", str(onnx), u_onnx], check=True)
        subprocess.run(["wget", "-q", "-O", str(cfg), u_cfg], check=True)
    return onnx


@app.cls(
    image=image,
    volumes={CACHE: voice_cache},
    cpu=2.0,
    memory=4096,
    timeout=300,
    scaledown_window=20,
)
class PiperDE:
    @modal.enter()
    def setup(self):
        # Pre-download default voice on container start
        for v in ["de_DE-thorsten-medium"]:
            try:
                _download_voice(v)
            except Exception as e:
                print(f"voice {v} download failed: {e}")

    def _synth(self, text: str, voice: str) -> tuple[bytes, float, float]:
        onnx = _download_voice(voice)
        t0 = time.perf_counter()
        proc = subprocess.run(
            ["piper", "--model", str(onnx), "--output-raw"],
            input=text.encode("utf-8"),
            capture_output=True, check=True,
        )
        synth_s = time.perf_counter() - t0
        pcm = proc.stdout
        audio_s = len(pcm) / 2 / SAMPLE_RATE
        return pcm, synth_s, audio_s

    @modal.asgi_app()
    def web(self):
        api = FastAPI(title="Piper DE TTS")

        @api.get("/health")
        def health(): return {"ok": True, "voices": list(VOICES)}

        @api.post("/tts")
        def tts(req: TTSReq):
            if req.voice not in VOICES:
                raise HTTPException(400, f"voice must be one of {list(VOICES)}")
            pcm, synth_s, audio_s = self._synth(req.text, req.voice)
            buf = io.BytesIO()
            with wave.open(buf, "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(SAMPLE_RATE)
                w.writeframes(pcm)
            return Response(
                content=buf.getvalue(), media_type="audio/wav",
                headers={
                    "X-Synth-Seconds": f"{synth_s:.4f}",
                    "X-Audio-Seconds": f"{audio_s:.4f}",
                    "X-RTF": f"{(synth_s/audio_s):.4f}" if audio_s > 0 else "0",
                    "X-Voice": req.voice, "X-Model": "piper-tts",
                },
            )
        return api
