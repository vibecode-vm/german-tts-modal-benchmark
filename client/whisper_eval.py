"""Whisper roundtrip evaluation: synthesize → transcribe → compare.

Loads all generated WAVs, transcribes each with Whisper-large-v3 (de),
computes Character Error Rate (CER) and Word Error Rate (WER) against the
original text. Lower = more intelligible synthesis.

Run: /tmp/wh/bin/python client/whisper_eval.py
"""

import json
import re
import time
import unicodedata
from pathlib import Path

from faster_whisper import WhisperModel

ROOT = Path(__file__).parent.parent
AUDIO = ROOT / "audio_out"
REPORTS = ROOT / "reports"
RESULTS = REPORTS / "benchmark_results.json"
OUT = REPORTS / "whisper_eval.json"


def normalize(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^\w\s]", " ", s.lower())
    s = re.sub(r"\s+", " ", s).strip()
    return s


def edit_distance(a, b):
    if len(a) < len(b):
        return edit_distance(b, a)
    if len(b) == 0:
        return len(a)
    prev = range(len(b) + 1)
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (ca != cb)))
        prev = curr
    return prev[-1]


def cer(ref: str, hyp: str) -> float:
    r = normalize(ref); h = normalize(hyp)
    if not r: return 1.0
    return edit_distance(r, h) / len(r)


def wer(ref: str, hyp: str) -> float:
    r = normalize(ref).split(); h = normalize(hyp).split()
    if not r: return 1.0
    return edit_distance(r, h) / len(r)


def main():
    print("Loading Whisper large-v3 (int8 CPU)...")
    t0 = time.perf_counter()
    model = WhisperModel("large-v3", device="cpu", compute_type="int8")
    print(f"Loaded in {time.perf_counter()-t0:.1f}s")

    results = json.loads(RESULTS.read_text())
    out_rows = []
    by_model = {}
    for r in results:
        if "error" in r: continue
        wav_rel = r.get("file")
        wav = ROOT / wav_rel
        if not wav.exists():
            print(f"  skip (missing): {wav_rel}")
            continue
        t1 = time.perf_counter()
        segs, info = model.transcribe(str(wav), language="de", beam_size=5, vad_filter=True)
        hyp = " ".join(s.text for s in segs).strip()
        dt = time.perf_counter() - t1
        c = cer(r["text"], hyp); w = wer(r["text"], hyp)
        row = {**r, "hyp": hyp, "cer": c, "wer": w, "whisper_s": dt}
        out_rows.append(row)
        by_model.setdefault(r["model"], []).append(row)
        print(f"  [{r['model']:>10}/{r['sample']:<14}] CER={c:.3f} WER={w:.3f}  ({dt:.1f}s)")

    # Per-model summary
    summary = {}
    for m, rs in by_model.items():
        if not rs: continue
        avg_cer = sum(r["cer"] for r in rs) / len(rs)
        avg_wer = sum(r["wer"] for r in rs) / len(rs)
        summary[m] = {"n": len(rs), "avg_cer": avg_cer, "avg_wer": avg_wer}

    print("\n=== SUMMARY ===")
    for m, s in sorted(summary.items(), key=lambda x: x[1]["avg_cer"]):
        print(f"  {m:<10}  n={s['n']:>2}  CER={s['avg_cer']:.3f}  WER={s['avg_wer']:.3f}")

    OUT.write_text(json.dumps({"rows": out_rows, "summary": summary}, indent=2, ensure_ascii=False))
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
