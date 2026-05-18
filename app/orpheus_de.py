"""Orpheus 3B German (Kartoffel) — SebastianBodza/Kartoffel_Orpheus-3B_german_natural-v0.1.

Llama-3.2-3B base + SNAC codec. ~6 GB FP16 weights, needs L40S or A100 80GB.
"""
from __future__ import annotations

import io
import time
import wave

import modal

APP_NAME = "orpheus-de-tts"
MODEL_ID = "SebastianBodza/Kartoffel_Orpheus-3B_german_natural-v0.1"
SNAC_ID = "hubertsiuzdak/snac_24khz"
SAMPLE_RATE = 24000

app = modal.App(APP_NAME)
hf_cache = modal.Volume.from_name("orpheus-de-hf-cache", create_if_missing=True)
CACHE = "/cache"

image = (
    modal.Image.from_registry("nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04", add_python="3.11")
    .apt_install("libsndfile1", "ffmpeg", "git")
    .env({
        "HF_HOME": CACHE, "TRANSFORMERS_CACHE": CACHE, "TORCH_HOME": CACHE,
        "HF_HUB_ENABLE_HF_TRANSFER": "1",
    })
    .pip_install(
        "torch==2.4.1", "torchaudio==2.4.1", "transformers==4.46.3",
        "snac==1.2.1", "accelerate==1.1.1", "hf_transfer",
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
    from snac import SNAC
    from transformers import AutoModelForCausalLM, AutoTokenizer

    class TTSReq(BaseModel):
        text: str
        voice: str = "Jakob"   # voices listed in Kartoffel-Orpheus card


# Kartoffel-Orpheus voices (per model card)
VOICES = ["Jakob", "Anton", "Julian", "Jan", "Alexander", "Adrian",
          "Julia", "Anna", "Katharina", "Clara", "Sophie", "Marie", "Mia"]


def _format_prompt(text: str, voice: str) -> str:
    # Orpheus-style prompt format
    return f"{voice}: {text}"


@app.cls(
    image=image,
    volumes={CACHE: hf_cache},
    gpu="L40S",
    timeout=900,
    scaledown_window=20,
)
class OrpheusDE:
    @modal.enter()
    def load(self):
        logger.info("Loading Orpheus 3B German + SNAC...")
        t0 = time.perf_counter()
        self.tok = AutoTokenizer.from_pretrained(MODEL_ID)
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID, torch_dtype=torch.bfloat16,
        ).to("cuda").eval()
        self.snac = SNAC.from_pretrained(SNAC_ID).to("cuda").eval()
        logger.info(f"Loaded in {time.perf_counter() - t0:.1f}s")
        # Warmup German
        try:
            _ = self._synth_internal("Guten Tag, ein kurzer Warmup.", "Jakob", max_new=200)
            logger.info("Warmup OK")
        except Exception as e:
            logger.warning(f"Warmup failed: {e}")

    def _synth_internal(self, text: str, voice: str, max_new: int = 4000):
        # Canonical Kartoffel-Orpheus protocol (per HF model card example)
        prompt = _format_prompt(text, voice)
        start_token = torch.tensor([[128259]], dtype=torch.int64, device="cuda")
        end_tokens  = torch.tensor([[128009, 128260]], dtype=torch.int64, device="cuda")
        input_ids = self.tok(prompt, return_tensors="pt").input_ids.to("cuda")
        ids = torch.cat([start_token, input_ids, end_tokens], dim=1)
        attn = torch.ones_like(ids)
        with torch.no_grad():
            generated = self.model.generate(
                input_ids=ids, attention_mask=attn,
                max_new_tokens=max_new,
                do_sample=True, temperature=0.6, top_p=0.95, repetition_penalty=1.1,
                num_return_sequences=1,
                eos_token_id=128258, use_cache=True,
            )
        token_to_find = 128257
        token_to_remove = 128258
        token_indices = (generated == token_to_find).nonzero(as_tuple=True)
        if len(token_indices[1]) > 0:
            last = token_indices[1][-1].item()
            cropped = generated[:, last + 1:]
        else:
            cropped = generated
        masked = cropped[0][cropped[0] != token_to_remove]
        n = (masked.size(0) // 7) * 7
        trimmed = masked[:n]
        if n == 0:
            raise RuntimeError("no audio tokens generated")
        code_list = [int(t.item()) - 128266 for t in trimmed]
        layer_1, layer_2, layer_3 = [], [], []
        for i in range(n // 7):
            layer_1.append(code_list[7*i])
            layer_2.append(code_list[7*i + 1] - 1 * 4096)
            layer_3.append(code_list[7*i + 2] - 2 * 4096)
            layer_3.append(code_list[7*i + 3] - 3 * 4096)
            layer_2.append(code_list[7*i + 4] - 4 * 4096)
            layer_3.append(code_list[7*i + 5] - 5 * 4096)
            layer_3.append(code_list[7*i + 6] - 6 * 4096)
        codes = [
            torch.tensor(layer_1, device="cuda").unsqueeze(0),
            torch.tensor(layer_2, device="cuda").unsqueeze(0),
            torch.tensor(layer_3, device="cuda").unsqueeze(0),
        ]
        with torch.no_grad():
            wav = self.snac.decode(codes).detach().squeeze().cpu().float().numpy()
        return wav

    def _synth(self, text: str, voice: str) -> tuple[bytes, float, float]:
        if voice not in VOICES:
            raise HTTPException(400, f"voice must be one of {VOICES}")
        t0 = time.perf_counter()
        a = self._synth_internal(text, voice)
        torch.cuda.synchronize()
        synth_s = time.perf_counter() - t0
        peak = float(np.abs(a).max() or 1.0)
        if peak > 1.0: a = a / peak
        pcm = (a * 32767).astype(np.int16).tobytes()
        audio_s = len(a) / SAMPLE_RATE
        return pcm, synth_s, audio_s

    @modal.asgi_app()
    def web(self):
        api = FastAPI(title="Orpheus DE TTS")

        @api.get("/health")
        def health(): return {"ok": True, "voices": VOICES, "model": MODEL_ID}

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
                    "X-Voice": req.voice, "X-Model": "orpheus-3b-de-kartoffel",
                },
            )
        return api
