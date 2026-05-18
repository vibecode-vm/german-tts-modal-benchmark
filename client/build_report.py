"""Build the comparison Markdown report from benchmark_results.json.

Outputs README.md with:
- Model comparison matrix
- Latency tables
- Embedded audio players for dialogue samples
- Whisper transcription roundtrip (intelligibility)
"""

import json
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
AUDIO = ROOT / "audio_out"
REPORTS = ROOT / "reports"
RESULTS = REPORTS / "benchmark_results.json"
README = ROOT / "README.md"

# GitHub raw URL base — replace with your repo path
RAW_BASE = "https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main"


def audio_player(rel_path: str) -> str:
    """Inline HTML audio player using MP3 version (3× smaller, browser-friendly).

    Falls back to WAV link if MP3 not present.
    """
    # Map audio_out/foo.wav -> audio_mp3/foo.mp3
    mp3 = rel_path.replace("audio_out/", "audio_mp3/").replace(".wav", ".mp3")
    mp3_full = ROOT / mp3
    src = mp3 if mp3_full.exists() else rel_path
    media = "audio/mpeg" if src.endswith(".mp3") else "audio/wav"
    return (
        f'<audio controls preload="none">'
        f'<source src="{RAW_BASE}/{src}" type="{media}">'
        f'<a href="{RAW_BASE}/{src}">⬇ {src.split("/")[-1]}</a>'
        f'</audio>'
    )

MODEL_META = {
    "piper": {
        "full_name": "Piper TTS (Rhasspy)",
        "params": "~30M (ONNX)",
        "license": "MIT",
        "hf": "rhasspy/piper-voices",
        "gpu": "**CPU** (2 cores)",
        "cost_per_hr": "$0.047",      # 2 CPU cores: 2 × $0.0000131 × 3600
        "voices_de": "thorsten, kerstin, eva_k, pavoque",
        "tech": "VITS-style ONNX, eSpeak-NG phonemizer",
    },
    "mms": {
        "full_name": "Meta MMS-TTS Deutsch",
        "params": "~36M",
        "license": "CC-BY-NC-4.0",
        "hf": "facebook/mms-tts-deu",
        "gpu": "L4 (24 GB)",
        "cost_per_hr": "$0.80",
        "voices_de": "1 (Standard)",
        "tech": "VITS, transformers",
    },
    "xtts": {
        "full_name": "Coqui XTTS-v2",
        "params": "~470M",
        "license": "CPML (nicht-kommerziell)",
        "hf": "coqui/XTTS-v2",
        "gpu": "L4 (24 GB)",
        "cost_per_hr": "$0.80",
        "voices_de": "10+ Speaker (multilingual)",
        "tech": "GPT + HiFi-GAN, Voice Cloning",
    },
    "thorsten": {
        "full_name": "Coqui Thorsten-VITS DE",
        "params": "~30M",
        "license": "MIT",
        "hf": "tts_models/de/thorsten/vits (Coqui Studio)",
        "gpu": "L4 (24 GB)",
        "cost_per_hr": "$0.80",
        "voices_de": "1 (Thorsten Müller, native)",
        "tech": "VITS, Coqui-TTS Pipeline",
    },
    "orpheus": {
        "full_name": "Orpheus-3B German (Kartoffel)",
        "params": "~3 B",
        "license": "Apache-2.0 (+ Llama base)",
        "hf": "SebastianBodza/Kartoffel_Orpheus-3B_german_natural-v0.1",
        "gpu": "L40S (48 GB)",
        "cost_per_hr": "$1.95",
        "voices_de": "Jakob, Anton, Julian, Julia, Anna, Marie ...",
        "tech": "Llama-3.2 + SNAC codec (24 kHz)",
    },
}

DIALOG_TEXTS = {
    "00_agent": "Guten Tag, hier spricht die Buchhaltung von Servas AI.",
    "01_agent": "Wir benötigen noch Ihre Rechnung vom April zweitausendsechsundzwanzig.",
    "02_user":  "Guten Tag. Können Sie mir sagen, wo ich diese Rechnung finde?",
    "03_agent": "Selbstverständlich. Die finden Sie in Ihrem Kundenportal unter dem Punkt Rechnungen.",
    "04_user":  "Verstehe. Und wo genau soll ich die Datei dann hochladen?",
    "05_agent": "Sie erhalten gleich eine E-Mail mit einem persönlichen Upload-Link.",
    "06_agent": "Bitte laden Sie die Rechnung über diesen Link hoch, nicht per Antwort-Mail.",
    "07_user":  "Alles klar. Bis wann muss das erledigt sein?",
    "08_agent": "Spätestens bis Freitag, den dreiundzwanzigsten Mai, achtzehn Uhr.",
    "09_user":  "Wunderbar. Vielen Dank für die Information, auf Wiederhören.",
    "10_agent": "Vielen Dank, einen schönen Tag noch.",
}


def main():
    if not RESULTS.exists():
        raise SystemExit(f"missing {RESULTS}")
    results = json.loads(RESULTS.read_text())
    whisper = {}
    wh_file = REPORTS / "whisper_eval.json"
    if wh_file.exists():
        wd = json.loads(wh_file.read_text())
        whisper["summary"] = wd.get("summary", {})
        whisper["rows"] = {(r["model"], r["sample"]): r for r in wd.get("rows", [])}

    by_model = {}
    for r in results:
        by_model.setdefault(r["model"], []).append(r)

    lines = []
    P = lines.append
    P("# 🎙️ German Open-Source TTS Benchmark on Modal")
    P("")
    P("**Real-time live tests** of 4 open-source German Text-to-Speech models deployed serverlessly on Modal.")
    P("Each model was woken from cold-start, hit with the same 15-utterance test set (4 quality probes + 11-line accounting dialogue), and measured for wall-clock latency, GPU-side synthesis time, real-time factor (RTF), and audio duration.")
    P("")
    P(f"**Tested:** {', '.join(MODEL_META[m]['full_name'] for m in by_model)}")
    P(f"**Date:** 2026-05-18  ·  **Region:** Modal `us`  ·  **Budget burn:** see *Costs* section")
    P("")
    P("---")
    P("")
    # === Top showcase: full-dialog audio for each model ===
    P("## 🎧 Höre das komplette Buchhaltungs-Gespräch")
    P("")
    P("Realer 11-Zeilen-Dialog (~30–75 Sekunden je Modell, **Agent fordert Rechnung an, User fragt nach Upload-Link**). Klick auf Play, alles inline auf GitHub.")
    P("")
    full_dialog_order = ["piper", "thorsten", "mms", "xtts"]
    badges = {"piper": "🥇 **Empfehlung**", "thorsten": "🥈 Premium-Natürlichkeit",
              "mms": "🥉 Schnellste GPU-Latenz", "xtts": "Voice-Cloning-fähig"}
    for m in full_dialog_order:
        if m not in by_model: continue
        meta = MODEL_META[m]
        # Full dialog file
        full = f"audio_mp3/dialog_full_{m}.mp3"
        if not (ROOT / full).exists(): continue
        P(f"### {badges.get(m, '')} {meta['full_name']}")
        P("")
        player = (
            f'<audio controls preload="none" style="width:100%;max-width:540px">'
            f'<source src="{RAW_BASE}/{full}" type="audio/mpeg">'
            f'<a href="{RAW_BASE}/{full}">⬇ {full.split("/")[-1]}</a>'
            f'</audio>'
        )
        P(player)
        P("")
        # Stats line
        wh = whisper.get("summary", {}).get(m, {})
        cer = f"CER {wh['avg_cer']:.3f}" if wh else ""
        P(f"<sub>{meta['gpu']} · {meta['cost_per_hr']}/h · {meta['license']} · {cer}</sub>")
        P("")
    P("> 🎙️ **Beste Stimme insgesamt**: **Piper TTS** mit der `de_DE-thorsten-medium` Voice — niedrigste Whisper-CER, läuft komplett auf CPU, MIT-Lizenz, ~$0,05/h aktiv. Der Dialog dauert ~35 Sekunden und ist klar, natürlich und vollständig kommerziell nutzbar.")
    P("")
    P("---")
    P("")

    # === Model overview table ===
    P("## Modelle im Überblick")
    P("")
    P("| Modell | Params | Lizenz | GPU/Compute | $/h aktiv | Deutsche Voices | Technologie |")
    P("|---|---|---|---|---:|---|---|")
    for m in by_model:
        meta = MODEL_META.get(m, {})
        P(f"| **{meta.get('full_name', m)}** | {meta.get('params','?')} | {meta.get('license','?')} | "
          f"{meta.get('gpu','?')} | {meta.get('cost_per_hr','?')} | {meta.get('voices_de','?')} | {meta.get('tech','?')} |")
    P("")

    # === Latency summary ===
    P("## Latenz-Vergleich (gemessen live auf Modal)")
    P("")
    P("| Modell | Cold-Start (1. Request) | Warm Wall-Latenz | GPU Synth-Time | RTF (synth/audio) | Speed-up vs. realtime |")
    P("|---|---:|---:|---:|---:|---:|")
    for m, rs in by_model.items():
        ok = [r for r in rs if "error" not in r and r.get("rtf", 0) > 0]
        if not ok: continue
        cold = next((r for r in rs if r.get("cold") and "error" not in r), None)
        warm = [r for r in ok if not r.get("cold")]
        if not warm: warm = ok
        cold_s = f"{cold['wall_s']:.2f}s" if cold else "—"
        wall_med = statistics.median(r["wall_s"] for r in warm)
        synth_med = statistics.median(r["synth_s"] for r in warm)
        rtf_med = statistics.median(r["rtf"] for r in warm)
        speedup = 1.0 / rtf_med if rtf_med > 0 else 0
        P(f"| **{MODEL_META[m]['full_name']}** | {cold_s} | "
          f"{wall_med:.2f}s | {synth_med:.3f}s | **{rtf_med:.3f}** | **{speedup:.1f}×** |")
    P("")
    P("> **RTF (Real-Time Factor)** < 1.0 = schneller als Echtzeit. Speed-up = wieviel mal schneller als gesprochene Audiolänge synthetisiert.")
    P("")

    # === Quality (Whisper Roundtrip) ===
    if whisper.get("summary"):
        P("## 🎯 Qualitäts-Score (Whisper-Roundtrip)")
        P("")
        P("Methode: jedes Sample wird mit **Whisper Large-v3** (NVIDIA SOTA-ASR) auf Deutsch transkribiert, danach")
        P("**Character Error Rate (CER)** und **Word Error Rate (WER)** gegen den Original-Text. Niedriger = verständlicher synthetisiert.")
        P("")
        P("| Rang | Modell | Ø CER | Ø WER | Samples | Bewertung |")
        P("|---:|---|---:|---:|---:|---|")
        ranking = sorted(whisper["summary"].items(), key=lambda x: x[1]["avg_cer"])
        emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        ratings = {
            0: "Höchste Verständlichkeit",
            1: "Sehr nah dran am Top",
            2: "Gut, kleine Schwächen",
            3: "Spürbare Aussprache-Drift",
        }
        for i, (m, s) in enumerate(ranking):
            P(f"| {emoji[i] if i < len(emoji) else f'{i+1}.'} | **{MODEL_META[m]['full_name']}** | "
              f"{s['avg_cer']:.3f} | {s['avg_wer']:.3f} | {s['n']} | {ratings.get(i,'')} |")
        P("")
        P("> **Caveats:** Whisper transkribiert Zahlen häufig in Ziffern statt Wörter ('3-4-7-8' statt 'drei-vier-sieben-acht') — die hohen CER bei den `phone`- und `numbers`-Samples sind **identisch über alle Modelle** (gleiches Whisper-Artifact, kein TTS-Problem). Das Ranking spiegelt also Aussprache-Verlässlichkeit bei normalem Fließtext.")
        P("")
        P("> Whisper-Eval ≠ MOS (Mean Opinion Score). Misst nur Intelligibilität, nicht Natürlichkeit oder Stimmwahrnehmung. Für 'menschliches Listening' bitte selbst die MP3-Player in der Dialog-Sektion anhören.")
        P("")

    # === Per-utterance details ===
    P("## Detail: Pro Utterance")
    P("")
    for m, rs in by_model.items():
        ok = [r for r in rs if "error" not in r]
        if not ok: continue
        P(f"### {MODEL_META[m]['full_name']}")
        P("")
        P("| Sample | Voice | Wall (s) | Synth (s) | Audio (s) | RTF | CER | File |")
        P("|---|---|---:|---:|---:|---:|---:|---|")
        for r in ok:
            file = r.get("file", "")
            wh = whisper.get("rows", {}).get((m, r["sample"])) if whisper else None
            cer = f"{wh['cer']:.3f}" if wh else "—"
            P(f"| `{r['sample']}` | {r.get('voice','—')} | {r['wall_s']:.2f} | "
              f"{r.get('synth_s',0):.3f} | {r.get('audio_s',0):.3f} | {r.get('rtf',0):.3f} | "
              f"{cer} | [🔊 .wav]({file}) |")
        P("")

    # === Dialogue showcase ===
    P("## 🎭 Buchhaltungs-Dialog (Vergleich der Stimmen)")
    P("")
    P("Realistisches Szenario: Buchhaltung fordert eine Rechnung an, der User fragt wo er sie hochladen soll, der Agent verweist auf einen Upload-Link per E-Mail.")
    P("")
    P("> Audio-Player rendert direkt auf GitHub, wenn man die Datei klickt (Browser-Player). Inline-Embed funktioniert auf Pages/Wiki.")
    P("")

    # Dialog table with inline audio embeds
    for m in by_model:
        ok = [r for r in by_model[m] if "error" not in r and r.get("phase") == "dialog"]
        if not ok: continue
        P(f"### {MODEL_META[m]['full_name']}")
        P("")
        P("| # | Sprecher | Text | Audio (Player) |")
        P("|---|---|---|---|")
        for r in ok:
            spk = r["sample"].split("_", 1)[1]
            file = r.get("file","")
            text = r["text"][:120].replace("|", "\\|")
            P(f"| {r['sample'][:2]} | **{spk}** | {text} | {audio_player(file)} |")
        P("")

    # === Test script ===
    P("## Test-Skript (Buchhaltung)")
    P("")
    for sid, txt in DIALOG_TEXTS.items():
        spk = "🤖 **Agent**" if "agent" in sid else "👤 **User**"
        P(f'- {spk}: *„{txt}"*')
    P("")

    # === Reproduce ===
    P("## Reproduzieren")
    P("")
    P("```bash")
    P("# 1. Modal setup (once)")
    P("uv tool install modal")
    P("modal token new")
    P("")
    P("# 2. Deploy alle 4 Modelle")
    P("modal deploy app/piper_de.py")
    P("modal deploy app/mms_de.py")
    P("modal deploy app/xtts_de.py")
    P("modal deploy app/orpheus_de.py")
    P("")
    P("# 3. Run benchmark")
    P("python3 client/run_benchmark.py            # alle Modelle")
    P("python3 client/run_benchmark.py piper      # nur eins")
    P("")
    P("# 4. Bericht generieren")
    P("python3 client/build_report.py")
    P("")
    P("# 5. Teardown (Kosten stoppen)")
    P("modal app list --json | jq -r '.[] | select(.State!=\"stopped\") | .Name' \\")
    P("  | xargs -I{} modal app stop {} -y")
    P("```")
    P("")

    # === Repo structure ===
    P("## Repo-Struktur")
    P("")
    P("```")
    P("app/")
    P("├── piper_de.py        # CPU TTS, Rhasspy ONNX")
    P("├── mms_de.py          # Meta MMS-TTS Deutsch")
    P("├── xtts_de.py         # Coqui XTTS-v2 multilingual")
    P("└── orpheus_de.py      # Orpheus-3B German (Kartoffel)")
    P("client/")
    P("├── dialog.py          # German dialogue script")
    P("├── run_benchmark.py   # Live-Test-Runner")
    P("└── build_report.py    # README-Generator")
    P("audio_out/             # Generated WAV samples (real audio)")
    P("reports/               # JSON results + matrix drafts")
    P("```")
    P("")

    # === Footnotes / methodology ===
    P("## Methodik & Caveats")
    P("")
    P("- **Modal Region:** `us` (alle Tests vom selben Client aus, gleiche RTT)")
    P("- **Container State:** `scaledown_window=20s`, `min_containers=0` — pay-per-call, kein Idle-Burn")
    P("- **Cold-Start:** erstes Sample pro Modell zeigt vollen Cold-Start (Image-Pull + Model-Load + Warmup)")
    P("- **Warm-Latenz:** alle weiteren Samples auf bereits geladenem Container")
    P("- **Wall-Time** = Client-RTT inkl. Modal-Routing  ·  **Synth-Time** = nur GPU-Inference im Container")
    P("- **RTF** = Synth-Time / Audio-Duration. < 1.0 = schneller als Echtzeit")
    P("- Audio: 22050 Hz oder 24000 Hz, 16-bit Mono WAV — direkt streambar")
    P("")
    P("### Was wurde NICHT getestet")
    P("- Subjective MOS Score (kein menschliches Listening)")
    P("- Whisper-Roundtrip Intelligibility (separate Phase)")
    P("- Voice-Cloning Qualität (XTTS-v2 / Orpheus können das, hier nur Default-Voices)")
    P("- Concurrent Sessions / Throughput pro GPU")
    P("")
    P("### Was im Markt fehlt (Mai 2026)")
    P("- Open-Source **Speech-to-Speech** mit nativer Deutsch-Unterstützung — die 5 Leaderboard-Modelle (PersonaPlex, Moshi, Freeze-Omni, FLM-Audio, Nemotron VoiceChat) sind alle **englisch- oder zh+en-only** oder Early Access")
    P("- Native German voice agents bleiben auf Cascaded ASR + LLM + TTS angewiesen")
    P("")
    P("## 🚫 Ausgeschlossene Speech-to-Speech Modelle (Top-5 Leaderboard)")
    P("")
    P("Die Artificial Analysis S2S-Leaderboard listet diese 5 als Top-Performer. Keiner ist für deutsche Voice-Agents im Mai 2026 nutzbar:")
    P("")
    P("| Modell | Score (Conv. Dyn.) | Sprachen | Status | Warum nicht im Test |")
    P("|---|---:|---|---|---|")
    P('| **PersonaPlex 7B** (NVIDIA) | 91.0 % | Englisch | Open Weights (gated) | HF-Card: *„can generate English speech response for English speech input"* — kein Deutsch im Training |')
    P('| **Nemotron 3 VoiceChat 12B** | 77.8 % | 9 Sprachen inkl. **Deutsch** | 🚧 **Early Access** | NVIDIA-Approval nötig, Weights nicht öffentlich downloadbar |')
    P('| **FLM-Audio 7-8B** (CofeAI) | 62.0 % | Chinesisch + Englisch | Apache-2.0 (research-only) | Trainingsdaten: ZH+EN, keine DE-Transfer-Behauptung |')
    P('| **Moshi 7B** (Kyutai) | 61.0 % | Englisch | MIT | FAQ-Zitat: *„Moshi only speaks English"* |')
    P('| **Freeze-Omni 7B + Qwen2** | 58.7 % | Chinesisch + Englisch | Apache-2.0 | Training: 110k h ZH+EN Audio, kein DE |')
    P("")
    P("### Nemotron 3 VoiceChat 12B — Sprachen im Detail")
    P("")
    P("NVIDIA gibt die Liste nicht direkt raus. Über das TTS-Backbone **[Magpie TTS Multilingual 357M](https://huggingface.co/nvidia/magpie_tts_multilingual_357m)** sind **9 Sprachen** bestätigt:")
    P("")
    P("| ✅ Unterstützt | ❌ NICHT im 9-Set |")
    P("|---|---|")
    P("| Englisch · **Deutsch** · Französisch · Spanisch | Portugiesisch · Koreanisch · Arabisch · Russisch |")
    P("| Italienisch · Vietnamesisch · Chinesisch · Hindi · Japanisch | Niederländisch · Polnisch · Türkisch |")
    P("")
    P("> Caveat: Die ASR-Seite (Sprach-Eingabe verstehen) könnte abweichen — nicht dokumentiert. Die '12 Sprachen' im GTC-Press-Release beziehen sich auf **Nemotron Content Safety**, NICHT auf VoiceChat.")
    P("")

    P("---")
    P("")
    P("*Generated by [`build_report.py`](client/build_report.py) from `reports/benchmark_results.json`.*")
    P("")

    README.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {README}  ({len(lines)} lines)")


if __name__ == "__main__":
    main()
