"""Coqui Thorsten-VITS — pure German VITS, MIT-license, gateless.

Replaces gated Orpheus as the 4th model. Native German speaker (Thorsten Müller).
"""
from __future__ import annotations

import io
import time
import wave

import modal

APP_NAME = "thorsten-de-tts"
SAMPLE_RATE = 22050

app = modal.App(APP_NAME)
hf_cache = modal.Volume.from_name("thorsten-tts-cache", create_if_missing=True)
CACHE = "/cache"

image = (
    modal.Image.from_registry("nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04", add_python="3.11")
    .apt_install("libsndfile1", "ffmpeg", "espeak-ng", "git")
    .env({
        "HF_HOME": CACHE, "TRANSFORMERS_CACHE": CACHE, "TORCH_HOME": CACHE,
        "TTS_HOME": CACHE,
        "HF_HUB_ENABLE_HF_TRANSFER": "1",
        "COQUI_TOS_AGREED": "1",
    })
    .pip_install(
        "torch==2.1.2", "torchaudio==2.1.2", "numpy<2.0",
        "transformers==4.40.2",
        "TTS==0.22.0", "hf_transfer", "fastapi[standard]", "pydantic", "loguru",
    )
)

with image.imports():
    import numpy as np
    import torch
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import Response
    from loguru import logger
    from pydantic import BaseModel
    from TTS.api import TTS

    class TTSReq(BaseModel):
        text: str
        voice: str = "default"
        language: str = "de"


MODEL_NAME = "tts_models/de/thorsten/vits"


@app.cls(
    image=image,
    volumes={CACHE: hf_cache},
    gpu="L4",
    timeout=600,
    scaledown_window=20,
)
class ThorstenDE:
    @modal.enter()
    def load(self):
        logger.info(f"Loading {MODEL_NAME} ...")
        t0 = time.perf_counter()
        self.tts = TTS(MODEL_NAME).to("cuda")
        logger.info(f"Loaded in {time.perf_counter() - t0:.1f}s; warmup...")
        _ = self.tts.tts(text="Guten Tag, das ist ein kurzer Test.")
        torch.cuda.synchronize()
        torch.cuda.empty_cache()
        logger.info(f"Ready in {time.perf_counter() - t0:.1f}s")

    def _synth(self, text: str) -> tuple[bytes, float, float]:
        t0 = time.perf_counter()
        with torch.no_grad():
            wav = self.tts.tts(text=text)
        torch.cuda.synchronize()
        synth_s = time.perf_counter() - t0
        a = np.asarray(wav, dtype=np.float32)
        peak = float(np.abs(a).max() or 1.0)
        if peak > 1.0: a = a / peak
        pcm = (a * 32767).astype(np.int16).tobytes()
        audio_s = len(a) / SAMPLE_RATE
        return pcm, synth_s, audio_s

    @modal.asgi_app()
    def web(self):
        api = FastAPI(title="Thorsten DE")

        @api.get("/health")
        def health(): return {"ok": True, "model": MODEL_NAME}

        @api.post("/tts")
        def tts(req: TTSReq):
            pcm, synth_s, audio_s = self._synth(req.text)
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
                    "X-Voice": req.voice, "X-Model": "thorsten-vits",
                },
            )
        return api
