"""Unified benchmark runner: hits all 4 TTS endpoints with the same dialogue.

Generates one WAV per (model, line). Measures wall latency, RTF, and saves
metadata JSON for the report.

Usage:
    python3 client/run_benchmark.py            # all models
    python3 client/run_benchmark.py piper      # only piper
"""

import json
import sys
import time
from pathlib import Path

import httpx

from dialog import DIALOG, SHORT_TESTS

MODELS = {
    "piper":    ("https://martin-hausleitner--piper-de-tts-piperde-web.modal.run",       "de_DE-thorsten-medium"),
    "mms":      ("https://martin-hausleitner--mms-de-tts-mmsde-web.modal.run",           "default"),
    "xtts":     ("https://martin-hausleitner--xtts-de-tts-xttsde-web.modal.run",         "female"),
    "thorsten": ("https://martin-hausleitner--thorsten-de-tts-thorstende-web.modal.run", "default"),
    "orpheus":  ("https://martin-hausleitner--orpheus-de-tts-orpheusde-web.modal.run",   "Jakob"),
}

OUT = Path(__file__).parent.parent / "audio_out"
REPORTS = Path(__file__).parent.parent / "reports"
OUT.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)


def call(url: str, text: str, voice: str, timeout: float = 600) -> tuple[bytes, dict, float]:
    t0 = time.perf_counter()
    r = httpx.post(
        f"{url}/tts",
        json={"text": text, "voice": voice, "language": "de"},
        timeout=timeout,
        follow_redirects=True,
        # Modal long-polling can redirect many times during cold-start
    )
    wall = time.perf_counter() - t0
    if r.status_code >= 400:
        raise RuntimeError(f"{r.status_code}: {r.text[:300]}")
    return r.content, dict(r.headers), wall


def test_model(name: str) -> list[dict]:
    url, default_voice = MODELS[name]
    print(f"\n========== {name.upper()} ==========")
    print(f"URL: {url}")
    results = []
    cold_start = True
    for sample_id, text in SHORT_TESTS:
        out_path = OUT / f"{name}__short__{sample_id}.wav"
        try:
            wav, hdr, wall = call(url, text, default_voice,
                                  timeout=900 if cold_start else 120)
        except Exception as e:
            print(f"  ❌ {sample_id}: {e}")
            results.append({"model": name, "sample": sample_id, "text": text,
                            "error": str(e), "phase": "short", "cold": cold_start})
            cold_start = False
            continue
        out_path.write_bytes(wav)
        m = {
            "model": name, "sample": sample_id, "text": text,
            "voice": default_voice, "wall_s": wall, "cold": cold_start,
            "synth_s": float(hdr.get("x-synth-seconds", 0)),
            "audio_s": float(hdr.get("x-audio-seconds", 0)),
            "rtf":     float(hdr.get("x-rtf", 0)),
            "file": str(out_path.relative_to(OUT.parent)), "phase": "short",
        }
        results.append(m)
        print(f"  ✅ {sample_id:<10} wall={wall:.2f}s synth={m['synth_s']:.2f}s "
              f"audio={m['audio_s']:.2f}s RTF={m['rtf']:.3f}")
        cold_start = False

    # Dialog
    print(f"  --- Dialogue ---")
    for i, (spk, text) in enumerate(DIALOG):
        sid = f"{i:02d}_{spk}"
        out_path = OUT / f"{name}__dialog__{sid}.wav"
        voice = default_voice
        # For models with male/female mapping, alternate
        if name == "xtts":
            voice = "female" if spk == "agent" else "male"
        elif name == "piper":
            voice = "de_DE-thorsten-medium" if spk == "user" else "de_DE-kerstin-low"
        elif name == "orpheus":
            voice = "Julia" if spk == "agent" else "Jakob"
        try:
            wav, hdr, wall = call(url, text, voice, timeout=180)
        except Exception as e:
            print(f"  ❌ {sid}: {e}")
            results.append({"model": name, "sample": sid, "text": text,
                            "voice": voice, "error": str(e), "phase": "dialog"})
            continue
        out_path.write_bytes(wav)
        m = {
            "model": name, "sample": sid, "text": text, "voice": voice,
            "wall_s": wall, "cold": False,
            "synth_s": float(hdr.get("x-synth-seconds", 0)),
            "audio_s": float(hdr.get("x-audio-seconds", 0)),
            "rtf":     float(hdr.get("x-rtf", 0)),
            "file": str(out_path.relative_to(OUT.parent)), "phase": "dialog",
        }
        results.append(m)
        print(f"  ✅ {sid:<14} ({voice[:15]:<15}) wall={wall:.2f}s "
              f"synth={m['synth_s']:.2f}s RTF={m['rtf']:.3f}")
    return results


def main():
    models = sys.argv[1:] or list(MODELS)
    out = REPORTS / "benchmark_results.json"
    existing = []
    if out.exists():
        try: existing = json.loads(out.read_text())
        except Exception: existing = []
    keep = [r for r in existing if r.get("model") not in models]
    new_results = []
    for m in models:
        if m not in MODELS:
            print(f"unknown model: {m}; available: {list(MODELS)}")
            sys.exit(1)
        try:
            new_results.extend(test_model(m))
        except Exception as e:
            print(f"\n❌ {m} fatal: {e}")
    merged = keep + new_results
    out.write_text(json.dumps(merged, indent=2, ensure_ascii=False))
    print(f"\nSaved {len(new_results)} new + {len(keep)} kept = {len(merged)} total -> {out}")


if __name__ == "__main__":
    main()
