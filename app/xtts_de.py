"""Coqui XTTS-v2 — multilingual voice cloning, supports German.

Note: CPML license = non-commercial. Use this only for evaluation here.
"""
import io
import time
import wave

import modal

APP_NAME = "xtts-de-tts"
SAMPLE_RATE = 24000  # XTTS-v2 default

app = modal.App(APP_NAME)
hf_cache = modal.Volume.from_name("xtts-hf-cache", create_if_missing=True)
CACHE = "/cache"

image = (
    modal.Image.from_registry("nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04", add_python="3.11")
    .apt_install("libsndfile1", "ffmpeg", "espeak-ng", "git")
    .env({
        "HF_HOME": CACHE,
        "TRANSFORMERS_CACHE": CACHE,
        "TORCH_HOME": CACHE,
        "HF_HUB_ENABLE_HF_TRANSFER": "1",
        "COQUI_TOS_AGREED": "1",
    })
    .pip_install(
        "torch==2.3.1", "torchaudio==2.3.1", "numpy<2.0",
        "TTS==0.22.0", "hf_transfer", "fastapi[standard]", "pydantic", "loguru",
        "deepspeed==0.14.4",
    )
)

with image.imports():
    import os
    import numpy as np
    import torch
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import Response
    from loguru import logger
    from pydantic import BaseModel
    from TTS.api import TTS

    class TTSReq(BaseModel):
        text: str
        voice: str = "default"   # XTTS uses speaker reference; we map names to internal speakers


# XTTS-v2 ships with multiple internal speakers
SPEAKERS = [
    "Claribel Dervla", "Daisy Studious", "Gracie Wise",     # female (en/multi)
    "Tammie Ema", "Sofia Hellen", "Tammy Grit",
    "Damien Black", "Viktor Eka",                            # male
    "Andrew Chipper", "Filip Traverse",
]
DEFAULT_F = "Sofia Hellen"
DEFAULT_M = "Damien Black"

VOICE_MAP = {
    "default": DEFAULT_F,
    "female":  DEFAULT_F,
    "male":    DEFAULT_M,
}


@app.cls(
    image=image,
    volumes={CACHE: hf_cache},
    gpu="L4",
    timeout=600,
    scaledown_window=20,
)
class XttsDE:
    @modal.enter()
    def load(self):
        logger.info("Loading XTTS-v2 ...")
        t0 = time.perf_counter()
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")
        logger.info(f"Loaded in {time.perf_counter() - t0:.1f}s; warmup DE...")
        # Warmup German
        _ = self.tts.tts(text="Guten Tag, das ist ein Test.", language="de", speaker=DEFAULT_F)
        torch.cuda.synchronize()
        torch.cuda.empty_cache()
        logger.info(f"Ready in {time.perf_counter() - t0:.1f}s")

    def _synth(self, text: str, voice: str) -> tuple[bytes, float, float]:
        speaker = VOICE_MAP.get(voice, voice)
        if speaker not in SPEAKERS and voice not in VOICE_MAP:
            raise HTTPException(400, f"voice must be one of {list(VOICE_MAP)} or {SPEAKERS}")
        t0 = time.perf_counter()
        with torch.no_grad():
            wav = self.tts.tts(text=text, language="de", speaker=speaker)
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
        api = FastAPI(title="XTTS-v2 DE")

        @api.get("/health")
        def health(): return {"ok": True, "voices": list(VOICE_MAP) + SPEAKERS}

        @api.post("/tts")
        def tts(req: TTSReq):
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
                    "X-Voice": req.voice, "X-Model": "xtts-v2",
                },
            )
        return api
