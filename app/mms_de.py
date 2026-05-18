"""Meta MMS-TTS German — `facebook/mms-tts-deu`. Small VITS, native German.

Apache-2.0, ~36M params, CPU-feasible but faster on GPU.
"""
import io
import time
import wave

import modal

APP_NAME = "mms-de-tts"

app = modal.App(APP_NAME)
hf_cache = modal.Volume.from_name("mms-hf-cache", create_if_missing=True)
CACHE = "/cache"

image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("libsndfile1", "ffmpeg")
    .env({"HF_HOME": CACHE, "TRANSFORMERS_CACHE": CACHE, "HF_HUB_ENABLE_HF_TRANSFER": "1"})
    .pip_install(
        "torch==2.3.1", "torchaudio==2.3.1",
        "transformers==4.45.2", "hf_transfer",
        "fastapi[standard]", "pydantic", "loguru", "numpy<2.0",
    )
)

with image.imports():
    import numpy as np
    import torch
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import Response
    from loguru import logger
    from pydantic import BaseModel
    from transformers import VitsModel, AutoTokenizer

    class TTSReq(BaseModel):
        text: str
        voice: str = "default"   # MMS has only one voice per language


MODEL_ID = "facebook/mms-tts-deu"


@app.cls(
    image=image,
    volumes={CACHE: hf_cache},
    gpu="L4",
    timeout=300,
    scaledown_window=20,
)
class MmsDE:
    @modal.enter()
    def load(self):
        logger.info(f"Loading {MODEL_ID}...")
        t0 = time.perf_counter()
        self.tok = AutoTokenizer.from_pretrained(MODEL_ID)
        self.model = VitsModel.from_pretrained(MODEL_ID).to("cuda").eval()
        self.sr = self.model.config.sampling_rate
        logger.info(f"Loaded in {time.perf_counter() - t0:.1f}s, sr={self.sr}")
        # Warmup
        with torch.no_grad():
            x = self.tok("Guten Tag, das ist ein Test.", return_tensors="pt").to("cuda")
            _ = self.model(**x).waveform
        torch.cuda.synchronize()
        logger.info(f"Ready in {time.perf_counter() - t0:.1f}s")

    def _synth(self, text: str) -> tuple[bytes, float, float, int]:
        t0 = time.perf_counter()
        with torch.no_grad():
            x = self.tok(text, return_tensors="pt").to("cuda")
            out = self.model(**x).waveform
        torch.cuda.synchronize()
        synth_s = time.perf_counter() - t0
        a = out.cpu().float().numpy().squeeze()
        peak = float(np.abs(a).max() or 1.0)
        if peak > 1.0: a = a / peak
        pcm = (a * 32767).astype(np.int16).tobytes()
        audio_s = len(a) / self.sr
        return pcm, synth_s, audio_s, self.sr

    @modal.asgi_app()
    def web(self):
        api = FastAPI(title="MMS-TTS DE")

        @api.get("/health")
        def health(): return {"ok": True, "model": MODEL_ID}

        @api.post("/tts")
        def tts(req: TTSReq):
            pcm, synth_s, audio_s, sr = self._synth(req.text)
            buf = io.BytesIO()
            with wave.open(buf, "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
                w.writeframes(pcm)
            return Response(
                content=buf.getvalue(), media_type="audio/wav",
                headers={
                    "X-Synth-Seconds": f"{synth_s:.4f}",
                    "X-Audio-Seconds": f"{audio_s:.4f}",
                    "X-RTF": f"{(synth_s/audio_s):.4f}" if audio_s > 0 else "0",
                    "X-Voice": req.voice, "X-Model": "mms-tts-deu",
                    "X-Sample-Rate": str(sr),
                },
            )
        return api
