# 🎙️ German Open-Source TTS Benchmark on Modal

**Real-time live tests** of 4 open-source German Text-to-Speech models deployed serverlessly on Modal.
Each model was woken from cold-start, hit with the same 15-utterance test set (4 quality probes + 11-line accounting dialogue), and measured for wall-clock latency, GPU-side synthesis time, real-time factor (RTF), and audio duration.

**Tested:** Meta MMS-TTS Deutsch, Piper TTS (Rhasspy)
**Date:** 2026-05-18  ·  **Region:** Modal `us`  ·  **Budget burn:** see *Costs* section

---

## Modelle im Überblick

| Modell | Params | Lizenz | GPU/Compute | $/h aktiv | Deutsche Voices | Technologie |
|---|---|---|---|---:|---|---|
| **Meta MMS-TTS Deutsch** | ~36M | CC-BY-NC-4.0 | L4 (24 GB) | $0.80 | 1 (Standard) | VITS, transformers |
| **Piper TTS (Rhasspy)** | ~30M (ONNX) | MIT | **CPU** (2 cores) | $0.047 | thorsten, kerstin, eva_k, pavoque | VITS-style ONNX, eSpeak-NG phonemizer |

## Latenz-Vergleich (gemessen live auf Modal)

| Modell | Cold-Start (1. Request) | Warm Wall-Latenz | GPU Synth-Time | RTF (synth/audio) | Speed-up vs. realtime |
|---|---:|---:|---:|---:|---:|
| **Meta MMS-TTS Deutsch** | 11.85s | 1.11s | 0.135s | **0.030** | **33.6×** |
| **Piper TTS (Rhasspy)** | 11.23s | 3.22s | 2.147s | **0.679** | **1.5×** |

> **RTF (Real-Time Factor)** < 1.0 = schneller als Echtzeit. Speed-up = wieviel mal schneller als gesprochene Audiolänge synthetisiert.

## Detail: Pro Utterance

### Meta MMS-TTS Deutsch

| Sample | Voice | Wall (s) | Synth (s) | Audio (s) | RTF | File |
|---|---|---:|---:|---:|---:|---|
| `greeting` | default | 11.85 | 0.332 | 3.872 | 0.086 | [🔊 .wav](audio_out/mms__short__greeting.wav) |
| `umlauts` | default | 1.31 | 0.461 | 4.576 | 0.101 | [🔊 .wav](audio_out/mms__short__umlauts.wav) |
| `numbers` | default | 1.15 | 0.144 | 5.904 | 0.024 | [🔊 .wav](audio_out/mms__short__numbers.wav) |
| `phone` | default | 1.20 | 0.158 | 6.400 | 0.025 | [🔊 .wav](audio_out/mms__short__phone.wav) |
| `00_agent` | default | 1.00 | 0.147 | 4.240 | 0.035 | [🔊 .wav](audio_out/mms__dialog__00_agent.wav) |
| `01_agent` | default | 1.22 | 0.137 | 4.672 | 0.029 | [🔊 .wav](audio_out/mms__dialog__01_agent.wav) |
| `02_user` | default | 1.07 | 0.130 | 4.016 | 0.032 | [🔊 .wav](audio_out/mms__dialog__02_user.wav) |
| `03_agent` | default | 1.08 | 0.135 | 5.440 | 0.025 | [🔊 .wav](audio_out/mms__dialog__03_agent.wav) |
| `04_user` | default | 1.15 | 0.136 | 4.800 | 0.028 | [🔊 .wav](audio_out/mms__dialog__04_user.wav) |
| `05_agent` | default | 1.22 | 0.134 | 5.392 | 0.025 | [🔊 .wav](audio_out/mms__dialog__05_agent.wav) |
| `06_agent` | default | 1.24 | 0.133 | 4.368 | 0.030 | [🔊 .wav](audio_out/mms__dialog__06_agent.wav) |
| `07_user` | default | 1.07 | 0.135 | 3.488 | 0.039 | [🔊 .wav](audio_out/mms__dialog__07_user.wav) |
| `08_agent` | default | 1.04 | 0.134 | 4.992 | 0.027 | [🔊 .wav](audio_out/mms__dialog__08_agent.wav) |
| `09_user` | default | 1.00 | 0.132 | 3.872 | 0.034 | [🔊 .wav](audio_out/mms__dialog__09_user.wav) |
| `10_agent` | default | 1.01 | 0.130 | 3.024 | 0.043 | [🔊 .wav](audio_out/mms__dialog__10_agent.wav) |

### Piper TTS (Rhasspy)

| Sample | Voice | Wall (s) | Synth (s) | Audio (s) | RTF | File |
|---|---|---:|---:|---:|---:|---|
| `greeting` | de_DE-thorsten-medium | 11.23 | 6.171 | 2.995 | 2.060 | [🔊 .wav](audio_out/piper__short__greeting.wav) |
| `umlauts` | de_DE-thorsten-medium | 3.43 | 2.239 | 5.016 | 0.446 | [🔊 .wav](audio_out/piper__short__umlauts.wav) |
| `numbers` | de_DE-thorsten-medium | 3.53 | 2.175 | 4.377 | 0.497 | [🔊 .wav](audio_out/piper__short__numbers.wav) |
| `phone` | de_DE-thorsten-medium | 3.28 | 2.203 | 5.120 | 0.430 | [🔊 .wav](audio_out/piper__short__phone.wav) |
| `00_agent` | de_DE-kerstin-low | 4.14 | 3.057 | 2.635 | 1.160 | [🔊 .wav](audio_out/piper__dialog__00_agent.wav) |
| `01_agent` | de_DE-kerstin-low | 3.11 | 2.143 | 3.402 | 0.630 | [🔊 .wav](audio_out/piper__dialog__01_agent.wav) |
| `02_user` | de_DE-thorsten-medium | 3.16 | 2.151 | 3.228 | 0.666 | [🔊 .wav](audio_out/piper__dialog__02_user.wav) |
| `03_agent` | de_DE-kerstin-low | 3.28 | 2.186 | 3.692 | 0.592 | [🔊 .wav](audio_out/piper__dialog__03_agent.wav) |
| `04_user` | de_DE-thorsten-medium | 3.16 | 2.114 | 3.077 | 0.687 | [🔊 .wav](audio_out/piper__dialog__04_user.wav) |
| `05_agent` | de_DE-kerstin-low | 3.08 | 2.064 | 2.752 | 0.750 | [🔊 .wav](audio_out/piper__dialog__05_agent.wav) |
| `06_agent` | de_DE-kerstin-low | 3.11 | 2.123 | 3.088 | 0.687 | [🔊 .wav](audio_out/piper__dialog__06_agent.wav) |
| `07_user` | de_DE-thorsten-medium | 3.07 | 2.111 | 2.577 | 0.819 | [🔊 .wav](audio_out/piper__dialog__07_user.wav) |
| `08_agent` | de_DE-kerstin-low | 3.37 | 2.292 | 3.088 | 0.742 | [🔊 .wav](audio_out/piper__dialog__08_agent.wav) |
| `09_user` | de_DE-thorsten-medium | 3.31 | 2.064 | 3.077 | 0.671 | [🔊 .wav](audio_out/piper__dialog__09_user.wav) |
| `10_agent` | de_DE-kerstin-low | 2.91 | 2.011 | 1.591 | 1.264 | [🔊 .wav](audio_out/piper__dialog__10_agent.wav) |

## 🎭 Buchhaltungs-Dialog (Vergleich der Stimmen)

Realistisches Szenario: Buchhaltung fordert eine Rechnung an, der User fragt wo er sie hochladen soll, der Agent verweist auf einen Upload-Link per E-Mail.

> Audio-Player rendert direkt auf GitHub, wenn man die Datei klickt (Browser-Player). Inline-Embed funktioniert auf Pages/Wiki.

### Meta MMS-TTS Deutsch

| # | Sprecher | Text | Audio (Player) |
|---|---|---|---|
| 00 | **agent** | Guten Tag, hier spricht die Buchhaltung von Servas AI. | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/mms__dialog__00_agent.wav"></audio> |
| 01 | **agent** | Wir benötigen noch Ihre Rechnung vom April zweitausendsechsundzwanzig. | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/mms__dialog__01_agent.wav"></audio> |
| 02 | **user** | Guten Tag. Können Sie mir sagen, wo ich diese Rechnung finde? | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/mms__dialog__02_user.wav"></audio> |
| 03 | **agent** | Selbstverständlich. Die finden Sie in Ihrem Kundenportal unter dem Punkt Rechnungen. | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/mms__dialog__03_agent.wav"></audio> |
| 04 | **user** | Verstehe. Und wo genau soll ich die Datei dann hochladen? | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/mms__dialog__04_user.wav"></audio> |
| 05 | **agent** | Sie erhalten gleich eine E-Mail mit einem persönlichen Upload-Link. | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/mms__dialog__05_agent.wav"></audio> |
| 06 | **agent** | Bitte laden Sie die Rechnung über diesen Link hoch, nicht per Antwort-Mail. | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/mms__dialog__06_agent.wav"></audio> |
| 07 | **user** | Alles klar. Bis wann muss das erledigt sein? | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/mms__dialog__07_user.wav"></audio> |
| 08 | **agent** | Spätestens bis Freitag, den dreiundzwanzigsten Mai, achtzehn Uhr. | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/mms__dialog__08_agent.wav"></audio> |
| 09 | **user** | Wunderbar. Vielen Dank für die Information, auf Wiederhören. | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/mms__dialog__09_user.wav"></audio> |
| 10 | **agent** | Vielen Dank, einen schönen Tag noch. | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/mms__dialog__10_agent.wav"></audio> |

### Piper TTS (Rhasspy)

| # | Sprecher | Text | Audio (Player) |
|---|---|---|---|
| 00 | **agent** | Guten Tag, hier spricht die Buchhaltung von Servas AI. | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/piper__dialog__00_agent.wav"></audio> |
| 01 | **agent** | Wir benötigen noch Ihre Rechnung vom April zweitausendsechsundzwanzig. | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/piper__dialog__01_agent.wav"></audio> |
| 02 | **user** | Guten Tag. Können Sie mir sagen, wo ich diese Rechnung finde? | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/piper__dialog__02_user.wav"></audio> |
| 03 | **agent** | Selbstverständlich. Die finden Sie in Ihrem Kundenportal unter dem Punkt Rechnungen. | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/piper__dialog__03_agent.wav"></audio> |
| 04 | **user** | Verstehe. Und wo genau soll ich die Datei dann hochladen? | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/piper__dialog__04_user.wav"></audio> |
| 05 | **agent** | Sie erhalten gleich eine E-Mail mit einem persönlichen Upload-Link. | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/piper__dialog__05_agent.wav"></audio> |
| 06 | **agent** | Bitte laden Sie die Rechnung über diesen Link hoch, nicht per Antwort-Mail. | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/piper__dialog__06_agent.wav"></audio> |
| 07 | **user** | Alles klar. Bis wann muss das erledigt sein? | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/piper__dialog__07_user.wav"></audio> |
| 08 | **agent** | Spätestens bis Freitag, den dreiundzwanzigsten Mai, achtzehn Uhr. | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/piper__dialog__08_agent.wav"></audio> |
| 09 | **user** | Wunderbar. Vielen Dank für die Information, auf Wiederhören. | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/piper__dialog__09_user.wav"></audio> |
| 10 | **agent** | Vielen Dank, einen schönen Tag noch. | <audio controls preload="none" src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_out/piper__dialog__10_agent.wav"></audio> |

## Test-Skript (Buchhaltung)

- 🤖 **Agent**: *„Guten Tag, hier spricht die Buchhaltung von Servas AI."*
- 🤖 **Agent**: *„Wir benötigen noch Ihre Rechnung vom April zweitausendsechsundzwanzig."*
- 👤 **User**: *„Guten Tag. Können Sie mir sagen, wo ich diese Rechnung finde?"*
- 🤖 **Agent**: *„Selbstverständlich. Die finden Sie in Ihrem Kundenportal unter dem Punkt Rechnungen."*
- 👤 **User**: *„Verstehe. Und wo genau soll ich die Datei dann hochladen?"*
- 🤖 **Agent**: *„Sie erhalten gleich eine E-Mail mit einem persönlichen Upload-Link."*
- 🤖 **Agent**: *„Bitte laden Sie die Rechnung über diesen Link hoch, nicht per Antwort-Mail."*
- 👤 **User**: *„Alles klar. Bis wann muss das erledigt sein?"*
- 🤖 **Agent**: *„Spätestens bis Freitag, den dreiundzwanzigsten Mai, achtzehn Uhr."*
- 👤 **User**: *„Wunderbar. Vielen Dank für die Information, auf Wiederhören."*
- 🤖 **Agent**: *„Vielen Dank, einen schönen Tag noch."*

## Reproduzieren

```bash
# 1. Modal setup (once)
uv tool install modal
modal token new

# 2. Deploy alle 4 Modelle
modal deploy app/piper_de.py
modal deploy app/mms_de.py
modal deploy app/xtts_de.py
modal deploy app/orpheus_de.py

# 3. Run benchmark
python3 client/run_benchmark.py            # alle Modelle
python3 client/run_benchmark.py piper      # nur eins

# 4. Bericht generieren
python3 client/build_report.py

# 5. Teardown (Kosten stoppen)
modal app list --json | jq -r '.[] | select(.State!="stopped") | .Name' \
  | xargs -I{} modal app stop {} -y
```

## Repo-Struktur

```
app/
├── piper_de.py        # CPU TTS, Rhasspy ONNX
├── mms_de.py          # Meta MMS-TTS Deutsch
├── xtts_de.py         # Coqui XTTS-v2 multilingual
└── orpheus_de.py      # Orpheus-3B German (Kartoffel)
client/
├── dialog.py          # German dialogue script
├── run_benchmark.py   # Live-Test-Runner
└── build_report.py    # README-Generator
audio_out/             # Generated WAV samples (real audio)
reports/               # JSON results + matrix drafts
```

## Methodik & Caveats

- **Modal Region:** `us` (alle Tests vom selben Client aus, gleiche RTT)
- **Container State:** `scaledown_window=20s`, `min_containers=0` — pay-per-call, kein Idle-Burn
- **Cold-Start:** erstes Sample pro Modell zeigt vollen Cold-Start (Image-Pull + Model-Load + Warmup)
- **Warm-Latenz:** alle weiteren Samples auf bereits geladenem Container
- **Wall-Time** = Client-RTT inkl. Modal-Routing  ·  **Synth-Time** = nur GPU-Inference im Container
- **RTF** = Synth-Time / Audio-Duration. < 1.0 = schneller als Echtzeit
- Audio: 22050 Hz oder 24000 Hz, 16-bit Mono WAV — direkt streambar

### Was wurde NICHT getestet
- Subjective MOS Score (kein menschliches Listening)
- Whisper-Roundtrip Intelligibility (separate Phase)
- Voice-Cloning Qualität (XTTS-v2 / Orpheus können das, hier nur Default-Voices)
- Concurrent Sessions / Throughput pro GPU

### Was im Markt fehlt (Mai 2026)
- Open-Source **Speech-to-Speech** mit nativer Deutsch-Unterstützung — die 5 Leaderboard-Modelle (PersonaPlex, Moshi, Freeze-Omni, FLM-Audio, Nemotron VoiceChat) sind alle **englisch- oder zh+en-only** oder Early Access
- Native German voice agents bleiben auf Cascaded ASR + LLM + TTS angewiesen

---

*Generated by [`build_report.py`](client/build_report.py) from `reports/benchmark_results.json`.*
