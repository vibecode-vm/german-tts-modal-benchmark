"""Minimal Modal deployment of NVIDIA Magpie-TTS Multilingual 357M for German.

Goal: cheapest end-to-end German voice test on Modal. L4 GPU, scale-to-zero,
no min_containers idle burn. One HTTP POST endpoint returns WAV bytes.

Deploy: modal deploy app/magpie_tts_de.py
Tear down: modal app stop magpie-de-tts -y
"""

import io
import time
import wave

import modal

APP_NAME = "magpie-de-tts"
MODEL_ID = "nvidia/magpie_tts_multilingual_357m"
SAMPLE_RATE = 22000
SPEAKERS = {"john": 0, "sofia": 1, "aria": 2, "jason": 3, "leo": 4}
LANGUAGES = {"de", "en", "es", "fr", "it", "vi", "zh"}

app = modal.App(APP_NAME)
model_cache = modal.Volume.from_name("magpie-de-cache", create_if_missing=True)
CACHE_PATH = "/cache"

image = (
    modal.Image.from_registry(
        "nvidia/cuda:13.0.1-cudnn-devel-ubuntu22.04", add_python="3.12"
    )
    .env({
        "HF_HUB_ENABLE_HF_TRANSFER": "1",
        "HF_HOME": CACHE_PATH,
        "TORCH_HOME": CACHE_PATH,
    })
    .apt_install("git", "libsndfile1", "ffmpeg", "cmake", "clang")
    .uv_pip_install(
        "hf_transfer==0.1.9",
        "huggingface_hub[hf-xet]==0.31.2",
        "fastapi[standard]",
        "pydantic",
        "loguru",
        "numpy<2.0.0",
        "omegaconf",
        "hydra-core",
    )
    .uv_pip_install(
        "nemo_toolkit[tts]@git+https://github.com/NVIDIA-NeMo/NeMo.git"
        "@78694d56d262",
        extra_options="--no-cache",
    )
)

with image.imports():
    import numpy as np
    import torch
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import Response
    from loguru import logger
    from nemo.collections.tts.models import MagpieTTSModel
    from pydantic import BaseModel

    class TTSRequest(BaseModel):
        text: str
        voice: str = "sofia"
        language: str = "de"


def _pcm_to_wav(pcm_int16_bytes: bytes, sample_rate: int) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(pcm_int16_bytes)
    return buf.getvalue()


@app.cls(
    image=image,
    volumes={CACHE_PATH: model_cache},
    gpu="L4",
    timeout=600,
    scaledown_window=20,
)
class MagpieDE:
    @modal.enter()
    def load(self):
        logger.info(f"Loading {MODEL_ID} ...")
        t0 = time.perf_counter()
        self.model = MagpieTTSModel.from_pretrained(MODEL_ID).cuda().eval()
        logger.info(f"Loaded in {time.perf_counter() - t0:.1f}s. Warming up (German)...")
        with torch.no_grad():
            self.model.do_tts(
                "Guten Tag, das ist ein Test der deutschen Sprache.",
                language="de", speaker_index=1, apply_TN=False,
            )
            torch.cuda.synchronize()
            torch.cuda.empty_cache()
        logger.info(f"Ready in {time.perf_counter() - t0:.1f}s")

    def _synth(self, text: str, voice: str, language: str) -> tuple[bytes, float, float]:
        if language not in LANGUAGES:
            raise HTTPException(400, f"language must be one of {sorted(LANGUAGES)}")
        speaker_idx = SPEAKERS.get(voice.lower(), 1)
        t0 = time.perf_counter()
        with torch.no_grad():
            audio, _ = self.model.do_tts(
                text, language=language, speaker_index=speaker_idx, apply_TN=False,
            )
        torch.cuda.synchronize()
        synth_s = time.perf_counter() - t0
        a = audio.cpu().float().numpy()
        if a.ndim == 2: a = a.squeeze(0)
        elif a.ndim == 3: a = a.squeeze()
        peak = float(np.abs(a).max() or 1.0)
        if peak > 1.0: a = a / peak
        pcm = (a * 32767).astype(np.int16).tobytes()
        audio_s = len(a) / SAMPLE_RATE
        return pcm, synth_s, audio_s

    @modal.asgi_app()
    def web(self):
        api = FastAPI(title="Magpie TTS DE")

        @api.get("/health")
        def health(): return {"ok": True, "model": MODEL_ID, "voices": list(SPEAKERS), "langs": sorted(LANGUAGES)}

        @api.post("/tts")
        def tts(req: TTSRequest):
            pcm, synth_s, audio_s = self._synth(req.text, req.voice, req.language)
            wav = _pcm_to_wav(pcm, SAMPLE_RATE)
            rtf = synth_s / audio_s if audio_s > 0 else 0.0
            return Response(
                content=wav,
                media_type="audio/wav",
                headers={
                    "X-Synth-Seconds": f"{synth_s:.3f}",
                    "X-Audio-Seconds": f"{audio_s:.3f}",
                    "X-RTF": f"{rtf:.3f}",
                    "X-Voice": req.voice,
                    "X-Language": req.language,
                },
            )

        return api
