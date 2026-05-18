"""End-to-end live test of Magpie TTS DE deployment on Modal.

Sends German test utterances, saves WAV files, measures latency, computes RTF.
Does NOT run Whisper/NISQA here — those come in a second pass.
"""

import json
import sys
import time
from pathlib import Path

import httpx

URL = "https://martin-hausleitner--magpie-de-tts-magpiede-web.modal.run"
OUT_DIR = Path(__file__).parent.parent / "audio_out"
OUT_DIR.mkdir(exist_ok=True)

# Real-world conversational German test script — Umlauts, numbers, prosody
SCRIPT = [
    ("01_greeting",   "Guten Morgen, Frau Schäfer! Wie geht es Ihnen heute?"),
    ("02_intro",      "Mein Name ist Jürgen Müller, und ich rufe aus München an."),
    ("03_order",      "Ihre Bestellung Nummer drei-vier-sieben-acht kostet einhundertneunundzwanzig Euro und fünfzig Cent."),
    ("04_date",       "Die Lieferung erfolgt am Dienstag, den dritten Juni zweitausendsechsundzwanzig."),
    ("05_phone",      "Bitte bestätigen Sie unter null-eins-fünf-eins, zwei-drei-vier-fünf, sechs-sieben-acht-neun."),
    ("06_closing",    "Großartig! Vielen Dank für Ihr Vertrauen. Auf Wiederhören und einen schönen Tag noch!"),
    ("07_long",       "Das schöne an der deutschen Sprache ist ihre Präzision: Donaudampfschifffahrtsgesellschaftskapitän klingt zwar lang, beschreibt aber genau einen Beruf."),
]

VOICES_TO_TEST = ["sofia", "aria", "leo"]  # 3 voices x 7 lines = 21 samples (sub-$1 cost)


def health(timeout: float = 600) -> dict:
    r = httpx.get(f"{URL}/health", timeout=timeout, follow_redirects=True)
    r.raise_for_status()
    return r.json()


def synth(voice: str, text: str, timeout: float = 120) -> tuple[bytes, dict]:
    t0 = time.perf_counter()
    r = httpx.post(
        f"{URL}/tts",
        json={"text": text, "voice": voice, "language": "de"},
        timeout=timeout,
        follow_redirects=True,
    )
    wall = time.perf_counter() - t0
    r.raise_for_status()
    meta = {
        "synth_s":  float(r.headers.get("X-Synth-Seconds", 0)),
        "audio_s":  float(r.headers.get("X-Audio-Seconds", 0)),
        "rtf":      float(r.headers.get("X-RTF", 0)),
        "wall_s":   wall,
        "bytes":    len(r.content),
    }
    return r.content, meta


def main():
    print("=== Health check (warms cold container) ===")
    t0 = time.perf_counter()
    print(json.dumps(health(), indent=2))
    print(f"health latency: {time.perf_counter() - t0:.2f}s\n")

    results = []
    for voice in VOICES_TO_TEST:
        print(f"\n=== Voice: {voice} ===")
        for sample_id, text in SCRIPT:
            wav, meta = synth(voice, text)
            out = OUT_DIR / f"{voice}__{sample_id}.wav"
            out.write_bytes(wav)
            meta.update({"voice": voice, "sample_id": sample_id, "text": text, "file": str(out)})
            results.append(meta)
            print(f"  {sample_id:<14} wall={meta['wall_s']:.2f}s "
                  f"synth={meta['synth_s']:.2f}s audio={meta['audio_s']:.2f}s "
                  f"RTF={meta['rtf']:.3f}  -> {out.name}")

    report = OUT_DIR.parent / "reports" / "magpie_latency.json"
    report.parent.mkdir(exist_ok=True)
    report.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nWrote latency report: {report}")

    # Summary
    rtfs = [r["rtf"] for r in results if r["rtf"] > 0]
    walls = [r["wall_s"] for r in results]
    print(f"\n=== SUMMARY ({len(results)} samples) ===")
    print(f"RTF: avg={sum(rtfs)/len(rtfs):.3f}  min={min(rtfs):.3f}  max={max(rtfs):.3f}")
    print(f"Wall latency: avg={sum(walls)/len(walls):.2f}s  min={min(walls):.2f}s  max={max(walls):.2f}s")


if __name__ == "__main__":
    main()
