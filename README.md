# 🎙️ German Open-Source TTS Benchmark on Modal

**Real-time live tests** of 4 open-source German Text-to-Speech models deployed serverlessly on Modal.
Each model was woken from cold-start, hit with the same 15-utterance test set (4 quality probes + 11-line accounting dialogue), and measured for wall-clock latency, GPU-side synthesis time, real-time factor (RTF), and audio duration.

**Tested:** Meta MMS-TTS Deutsch, Coqui XTTS-v2, Coqui Thorsten-VITS DE, Piper TTS (Rhasspy)
**Date:** 2026-05-18  ·  **Region:** Modal `us`  ·  **Budget burn:** see *Costs* section

---

## 🎧 Höre das komplette Buchhaltungs-Gespräch

Realer 11-Zeilen-Dialog (~30–75 Sekunden je Modell, **Agent fordert Rechnung an, User fragt nach Upload-Link**). Klick auf Play, alles inline auf GitHub.

### 🥇 **Empfehlung** Piper TTS (Rhasspy)

<audio controls preload="none" style="width:100%;max-width:540px"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/dialog_full_piper.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/dialog_full_piper.mp3">⬇ dialog_full_piper.mp3</a></audio>

<sub>**CPU** (2 cores) · $0.047/h · MIT · CER 0.137</sub>

### 🥈 Premium-Natürlichkeit Coqui Thorsten-VITS DE

<audio controls preload="none" style="width:100%;max-width:540px"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/dialog_full_thorsten.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/dialog_full_thorsten.mp3">⬇ dialog_full_thorsten.mp3</a></audio>

<sub>L4 (24 GB) · $0.80/h · MIT · CER 0.147</sub>

### 🥉 Schnellste GPU-Latenz Meta MMS-TTS Deutsch

<audio controls preload="none" style="width:100%;max-width:540px"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/dialog_full_mms.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/dialog_full_mms.mp3">⬇ dialog_full_mms.mp3</a></audio>

<sub>L4 (24 GB) · $0.80/h · CC-BY-NC-4.0 · CER 0.153</sub>

### Voice-Cloning-fähig Coqui XTTS-v2

<audio controls preload="none" style="width:100%;max-width:540px"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/dialog_full_xtts.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/dialog_full_xtts.mp3">⬇ dialog_full_xtts.mp3</a></audio>

<sub>L4 (24 GB) · $0.80/h · CPML (nicht-kommerziell) · CER 0.268</sub>

> 🎙️ **Beste Stimme insgesamt**: **Piper TTS** mit der `de_DE-thorsten-medium` Voice — niedrigste Whisper-CER, läuft komplett auf CPU, MIT-Lizenz, ~$0,05/h aktiv. Der Dialog dauert ~35 Sekunden und ist klar, natürlich und vollständig kommerziell nutzbar.

---

## Modelle im Überblick

| Modell | Params | Lizenz | GPU/Compute | $/h aktiv | Deutsche Voices | Technologie |
|---|---|---|---|---:|---|---|
| **Meta MMS-TTS Deutsch** | ~36M | CC-BY-NC-4.0 | L4 (24 GB) | $0.80 | 1 (Standard) | VITS, transformers |
| **Coqui XTTS-v2** | ~470M | CPML (nicht-kommerziell) | L4 (24 GB) | $0.80 | 10+ Speaker (multilingual) | GPT + HiFi-GAN, Voice Cloning |
| **Coqui Thorsten-VITS DE** | ~30M | MIT | L4 (24 GB) | $0.80 | 1 (Thorsten Müller, native) | VITS, Coqui-TTS Pipeline |
| **Piper TTS (Rhasspy)** | ~30M (ONNX) | MIT | **CPU** (2 cores) | $0.047 | thorsten, kerstin, eva_k, pavoque | VITS-style ONNX, eSpeak-NG phonemizer |

## Latenz-Vergleich (gemessen live auf Modal)

| Modell | Cold-Start (1. Request) | Warm Wall-Latenz | GPU Synth-Time | RTF (synth/audio) | Speed-up vs. realtime |
|---|---:|---:|---:|---:|---:|
| **Meta MMS-TTS Deutsch** | 11.85s | 1.11s | 0.135s | **0.030** | **33.6×** |
| **Coqui XTTS-v2** | 123.80s | 3.45s | 2.264s | **0.367** | **2.7×** |
| **Coqui Thorsten-VITS DE** | 89.94s | 1.90s | 0.881s | **0.161** | **6.2×** |
| **Piper TTS (Rhasspy)** | 6.56s | 2.75s | 1.712s | **0.455** | **2.2×** |

> **RTF (Real-Time Factor)** < 1.0 = schneller als Echtzeit. Speed-up = wieviel mal schneller als gesprochene Audiolänge synthetisiert.

## 🎯 Qualitäts-Score (Whisper-Roundtrip)

Methode: jedes Sample wird mit **Whisper Large-v3** (NVIDIA SOTA-ASR) auf Deutsch transkribiert, danach
**Character Error Rate (CER)** und **Word Error Rate (WER)** gegen den Original-Text. Niedriger = verständlicher synthetisiert.

| Rang | Modell | Ø CER | Ø WER | Samples | Bewertung |
|---:|---|---:|---:|---:|---|
| 🥇 | **Piper TTS (Rhasspy)** | 0.137 | 0.146 | 15 | Höchste Verständlichkeit |
| 🥈 | **Coqui Thorsten-VITS DE** | 0.147 | 0.163 | 15 | Sehr nah dran am Top |
| 🥉 | **Meta MMS-TTS Deutsch** | 0.153 | 0.181 | 15 | Gut, kleine Schwächen |
| 4️⃣ | **Coqui XTTS-v2** | 0.268 | 0.247 | 15 | Spürbare Aussprache-Drift |

> **Caveats:** Whisper transkribiert Zahlen häufig in Ziffern statt Wörter ('3-4-7-8' statt 'drei-vier-sieben-acht') — die hohen CER bei den `phone`- und `numbers`-Samples sind **identisch über alle Modelle** (gleiches Whisper-Artifact, kein TTS-Problem). Das Ranking spiegelt also Aussprache-Verlässlichkeit bei normalem Fließtext.

> Whisper-Eval ≠ MOS (Mean Opinion Score). Misst nur Intelligibilität, nicht Natürlichkeit oder Stimmwahrnehmung. Für 'menschliches Listening' bitte selbst die MP3-Player in der Dialog-Sektion anhören.

## Detail: Pro Utterance

### Meta MMS-TTS Deutsch

| Sample | Voice | Wall (s) | Synth (s) | Audio (s) | RTF | CER | File |
|---|---|---:|---:|---:|---:|---:|---|
| `greeting` | default | 11.85 | 0.332 | 3.872 | 0.086 | 0.022 | [🔊 .wav](audio_out/mms__short__greeting.wav) |
| `umlauts` | default | 1.31 | 0.461 | 4.576 | 0.101 | 0.057 | [🔊 .wav](audio_out/mms__short__umlauts.wav) |
| `numbers` | default | 1.15 | 0.144 | 5.904 | 0.024 | 0.487 | [🔊 .wav](audio_out/mms__short__numbers.wav) |
| `phone` | default | 1.20 | 0.158 | 6.400 | 0.025 | 0.709 | [🔊 .wav](audio_out/mms__short__phone.wav) |
| `00_agent` | default | 1.00 | 0.147 | 4.240 | 0.035 | 0.058 | [🔊 .wav](audio_out/mms__dialog__00_agent.wav) |
| `01_agent` | default | 1.22 | 0.137 | 4.672 | 0.029 | 0.377 | [🔊 .wav](audio_out/mms__dialog__01_agent.wav) |
| `02_user` | default | 1.07 | 0.130 | 4.016 | 0.032 | 0.000 | [🔊 .wav](audio_out/mms__dialog__02_user.wav) |
| `03_agent` | default | 1.08 | 0.135 | 5.440 | 0.025 | 0.000 | [🔊 .wav](audio_out/mms__dialog__03_agent.wav) |
| `04_user` | default | 1.15 | 0.136 | 4.800 | 0.028 | 0.000 | [🔊 .wav](audio_out/mms__dialog__04_user.wav) |
| `05_agent` | default | 1.22 | 0.134 | 5.392 | 0.025 | 0.152 | [🔊 .wav](audio_out/mms__dialog__05_agent.wav) |
| `06_agent` | default | 1.24 | 0.133 | 4.368 | 0.030 | 0.014 | [🔊 .wav](audio_out/mms__dialog__06_agent.wav) |
| `07_user` | default | 1.07 | 0.135 | 3.488 | 0.039 | 0.000 | [🔊 .wav](audio_out/mms__dialog__07_user.wav) |
| `08_agent` | default | 1.04 | 0.134 | 4.992 | 0.027 | 0.419 | [🔊 .wav](audio_out/mms__dialog__08_agent.wav) |
| `09_user` | default | 1.00 | 0.132 | 3.872 | 0.034 | 0.000 | [🔊 .wav](audio_out/mms__dialog__09_user.wav) |
| `10_agent` | default | 1.01 | 0.130 | 3.024 | 0.043 | 0.000 | [🔊 .wav](audio_out/mms__dialog__10_agent.wav) |

### Coqui XTTS-v2

| Sample | Voice | Wall (s) | Synth (s) | Audio (s) | RTF | CER | File |
|---|---|---:|---:|---:|---:|---:|---|
| `greeting` | female | 123.80 | 3.398 | 8.620 | 0.394 | 0.348 | [🔊 .wav](audio_out/xtts__short__greeting.wav) |
| `umlauts` | female | 3.13 | 1.981 | 5.473 | 0.362 | 0.000 | [🔊 .wav](audio_out/xtts__short__umlauts.wav) |
| `numbers` | female | 3.69 | 2.553 | 6.870 | 0.372 | 0.487 | [🔊 .wav](audio_out/xtts__short__numbers.wav) |
| `phone` | female | 4.18 | 2.808 | 7.563 | 0.371 | 0.698 | [🔊 .wav](audio_out/xtts__short__phone.wav) |
| `00_agent` | female | 5.46 | 4.295 | 9.046 | 0.475 | 0.865 | [🔊 .wav](audio_out/xtts__dialog__00_agent.wav) |
| `01_agent` | female | 3.23 | 2.124 | 6.123 | 0.347 | 0.377 | [🔊 .wav](audio_out/xtts__dialog__01_agent.wav) |
| `02_user` | male | 2.95 | 1.923 | 4.908 | 0.392 | 0.000 | [🔊 .wav](audio_out/xtts__dialog__02_user.wav) |
| `03_agent` | female | 3.67 | 2.607 | 7.415 | 0.352 | 0.000 | [🔊 .wav](audio_out/xtts__dialog__03_agent.wav) |
| `04_user` | male | 2.89 | 1.641 | 4.780 | 0.343 | 0.000 | [🔊 .wav](audio_out/xtts__dialog__04_user.wav) |
| `05_agent` | female | 4.86 | 3.491 | 9.323 | 0.374 | 0.545 | [🔊 .wav](audio_out/xtts__dialog__05_agent.wav) |
| `06_agent` | female | 2.76 | 1.784 | 4.961 | 0.360 | 0.000 | [🔊 .wav](audio_out/xtts__dialog__06_agent.wav) |
| `07_user` | male | 2.90 | 1.765 | 5.089 | 0.347 | 0.286 | [🔊 .wav](audio_out/xtts__dialog__07_user.wav) |
| `08_agent` | female | 3.06 | 2.109 | 5.654 | 0.373 | 0.419 | [🔊 .wav](audio_out/xtts__dialog__08_agent.wav) |
| `09_user` | male | 3.92 | 2.799 | 7.841 | 0.357 | 0.000 | [🔊 .wav](audio_out/xtts__dialog__09_user.wav) |
| `10_agent` | female | 3.68 | 2.404 | 6.262 | 0.384 | 0.000 | [🔊 .wav](audio_out/xtts__dialog__10_agent.wav) |

### Coqui Thorsten-VITS DE

| Sample | Voice | Wall (s) | Synth (s) | Audio (s) | RTF | CER | File |
|---|---|---:|---:|---:|---:|---:|---|
| `greeting` | default | 89.94 | 1.348 | 4.796 | 0.281 | 0.000 | [🔊 .wav](audio_out/thorsten__short__greeting.wav) |
| `umlauts` | default | 1.91 | 0.847 | 5.481 | 0.154 | 0.019 | [🔊 .wav](audio_out/thorsten__short__umlauts.wav) |
| `numbers` | default | 1.88 | 0.712 | 5.225 | 0.136 | 0.487 | [🔊 .wav](audio_out/thorsten__short__numbers.wav) |
| `phone` | default | 2.05 | 0.859 | 6.247 | 0.138 | 0.698 | [🔊 .wav](audio_out/thorsten__short__phone.wav) |
| `00_agent` | default | 1.84 | 0.903 | 3.728 | 0.242 | 0.058 | [🔊 .wav](audio_out/thorsten__dialog__00_agent.wav) |
| `01_agent` | default | 1.65 | 0.623 | 4.505 | 0.138 | 0.377 | [🔊 .wav](audio_out/thorsten__dialog__01_agent.wav) |
| `02_user` | default | 2.42 | 1.294 | 5.342 | 0.242 | 0.034 | [🔊 .wav](audio_out/thorsten__dialog__02_user.wav) |
| `03_agent` | default | 2.15 | 0.938 | 6.329 | 0.148 | 0.024 | [🔊 .wav](audio_out/thorsten__dialog__03_agent.wav) |
| `04_user` | default | 2.23 | 0.982 | 5.029 | 0.195 | 0.000 | [🔊 .wav](audio_out/thorsten__dialog__04_user.wav) |
| `05_agent` | default | 2.11 | 1.054 | 4.378 | 0.241 | 0.015 | [🔊 .wav](audio_out/thorsten__dialog__05_agent.wav) |
| `06_agent` | default | 2.54 | 0.937 | 4.714 | 0.199 | 0.068 | [🔊 .wav](audio_out/thorsten__dialog__06_agent.wav) |
| `07_user` | default | 1.66 | 0.725 | 4.320 | 0.168 | 0.000 | [🔊 .wav](audio_out/thorsten__dialog__07_user.wav) |
| `08_agent` | default | 1.77 | 0.671 | 4.656 | 0.144 | 0.419 | [🔊 .wav](audio_out/thorsten__dialog__08_agent.wav) |
| `09_user` | default | 1.82 | 0.940 | 5.029 | 0.187 | 0.000 | [🔊 .wav](audio_out/thorsten__dialog__09_user.wav) |
| `10_agent` | default | 1.34 | 0.407 | 2.857 | 0.142 | 0.000 | [🔊 .wav](audio_out/thorsten__dialog__10_agent.wav) |

### Piper TTS (Rhasspy)

| Sample | Voice | Wall (s) | Synth (s) | Audio (s) | RTF | CER | File |
|---|---|---:|---:|---:|---:|---:|---|
| `greeting` | de_DE-thorsten-medium | 6.56 | 2.148 | 2.937 | 0.731 | 0.000 | [🔊 .wav](audio_out/piper__short__greeting.wav) |
| `umlauts` | de_DE-thorsten-medium | 2.80 | 1.731 | 4.911 | 0.352 | 0.019 | [🔊 .wav](audio_out/piper__short__umlauts.wav) |
| `numbers` | de_DE-thorsten-medium | 2.82 | 1.728 | 4.505 | 0.384 | 0.487 | [🔊 .wav](audio_out/piper__short__numbers.wav) |
| `phone` | de_DE-thorsten-medium | 2.75 | 1.773 | 4.853 | 0.365 | 0.698 | [🔊 .wav](audio_out/piper__short__phone.wav) |
| `00_agent` | de_DE-thorsten-medium | 2.64 | 1.783 | 3.251 | 0.548 | 0.038 | [🔊 .wav](audio_out/piper__dialog__00_agent.wav) |
| `01_agent` | de_DE-thorsten-medium | 2.80 | 1.709 | 4.040 | 0.423 | 0.377 | [🔊 .wav](audio_out/piper__dialog__01_agent.wav) |
| `02_user` | de_DE-thorsten-medium | 2.66 | 1.662 | 3.251 | 0.511 | 0.000 | [🔊 .wav](audio_out/piper__dialog__02_user.wav) |
| `03_agent` | de_DE-thorsten-medium | 2.75 | 1.681 | 4.772 | 0.352 | 0.024 | [🔊 .wav](audio_out/piper__dialog__03_agent.wav) |
| `04_user` | de_DE-thorsten-medium | 2.81 | 1.751 | 3.088 | 0.567 | 0.000 | [🔊 .wav](audio_out/piper__dialog__04_user.wav) |
| `05_agent` | de_DE-thorsten-medium | 2.67 | 1.724 | 3.704 | 0.466 | 0.000 | [🔊 .wav](audio_out/piper__dialog__05_agent.wav) |
| `06_agent` | de_DE-thorsten-medium | 2.67 | 1.702 | 3.936 | 0.432 | 0.000 | [🔊 .wav](audio_out/piper__dialog__06_agent.wav) |
| `07_user` | de_DE-thorsten-medium | 2.69 | 1.715 | 2.670 | 0.642 | 0.000 | [🔊 .wav](audio_out/piper__dialog__07_user.wav) |
| `08_agent` | de_DE-thorsten-medium | 2.80 | 1.694 | 3.808 | 0.445 | 0.419 | [🔊 .wav](audio_out/piper__dialog__08_agent.wav) |
| `09_user` | de_DE-thorsten-medium | 2.79 | 1.693 | 3.367 | 0.503 | 0.000 | [🔊 .wav](audio_out/piper__dialog__09_user.wav) |
| `10_agent` | de_DE-thorsten-medium | 2.45 | 1.614 | 2.136 | 0.756 | 0.000 | [🔊 .wav](audio_out/piper__dialog__10_agent.wav) |

## 🎭 Buchhaltungs-Dialog (Vergleich der Stimmen)

Realistisches Szenario: Buchhaltung fordert eine Rechnung an, der User fragt wo er sie hochladen soll, der Agent verweist auf einen Upload-Link per E-Mail.

> Audio-Player rendert direkt auf GitHub, wenn man die Datei klickt (Browser-Player). Inline-Embed funktioniert auf Pages/Wiki.

### Meta MMS-TTS Deutsch

| # | Sprecher | Text | Audio (Player) |
|---|---|---|---|
| 00 | **agent** | Guten Tag, hier spricht die Buchhaltung von Servas AI. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__00_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__00_agent.mp3">⬇ mms__dialog__00_agent.mp3</a></audio> |
| 01 | **agent** | Wir benötigen noch Ihre Rechnung vom April zweitausendsechsundzwanzig. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__01_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__01_agent.mp3">⬇ mms__dialog__01_agent.mp3</a></audio> |
| 02 | **user** | Guten Tag. Können Sie mir sagen, wo ich diese Rechnung finde? | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__02_user.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__02_user.mp3">⬇ mms__dialog__02_user.mp3</a></audio> |
| 03 | **agent** | Selbstverständlich. Die finden Sie in Ihrem Kundenportal unter dem Punkt Rechnungen. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__03_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__03_agent.mp3">⬇ mms__dialog__03_agent.mp3</a></audio> |
| 04 | **user** | Verstehe. Und wo genau soll ich die Datei dann hochladen? | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__04_user.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__04_user.mp3">⬇ mms__dialog__04_user.mp3</a></audio> |
| 05 | **agent** | Sie erhalten gleich eine E-Mail mit einem persönlichen Upload-Link. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__05_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__05_agent.mp3">⬇ mms__dialog__05_agent.mp3</a></audio> |
| 06 | **agent** | Bitte laden Sie die Rechnung über diesen Link hoch, nicht per Antwort-Mail. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__06_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__06_agent.mp3">⬇ mms__dialog__06_agent.mp3</a></audio> |
| 07 | **user** | Alles klar. Bis wann muss das erledigt sein? | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__07_user.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__07_user.mp3">⬇ mms__dialog__07_user.mp3</a></audio> |
| 08 | **agent** | Spätestens bis Freitag, den dreiundzwanzigsten Mai, achtzehn Uhr. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__08_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__08_agent.mp3">⬇ mms__dialog__08_agent.mp3</a></audio> |
| 09 | **user** | Wunderbar. Vielen Dank für die Information, auf Wiederhören. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__09_user.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__09_user.mp3">⬇ mms__dialog__09_user.mp3</a></audio> |
| 10 | **agent** | Vielen Dank, einen schönen Tag noch. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__10_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/mms__dialog__10_agent.mp3">⬇ mms__dialog__10_agent.mp3</a></audio> |

### Coqui XTTS-v2

| # | Sprecher | Text | Audio (Player) |
|---|---|---|---|
| 00 | **agent** | Guten Tag, hier spricht die Buchhaltung von Servas AI. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__00_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__00_agent.mp3">⬇ xtts__dialog__00_agent.mp3</a></audio> |
| 01 | **agent** | Wir benötigen noch Ihre Rechnung vom April zweitausendsechsundzwanzig. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__01_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__01_agent.mp3">⬇ xtts__dialog__01_agent.mp3</a></audio> |
| 02 | **user** | Guten Tag. Können Sie mir sagen, wo ich diese Rechnung finde? | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__02_user.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__02_user.mp3">⬇ xtts__dialog__02_user.mp3</a></audio> |
| 03 | **agent** | Selbstverständlich. Die finden Sie in Ihrem Kundenportal unter dem Punkt Rechnungen. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__03_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__03_agent.mp3">⬇ xtts__dialog__03_agent.mp3</a></audio> |
| 04 | **user** | Verstehe. Und wo genau soll ich die Datei dann hochladen? | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__04_user.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__04_user.mp3">⬇ xtts__dialog__04_user.mp3</a></audio> |
| 05 | **agent** | Sie erhalten gleich eine E-Mail mit einem persönlichen Upload-Link. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__05_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__05_agent.mp3">⬇ xtts__dialog__05_agent.mp3</a></audio> |
| 06 | **agent** | Bitte laden Sie die Rechnung über diesen Link hoch, nicht per Antwort-Mail. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__06_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__06_agent.mp3">⬇ xtts__dialog__06_agent.mp3</a></audio> |
| 07 | **user** | Alles klar. Bis wann muss das erledigt sein? | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__07_user.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__07_user.mp3">⬇ xtts__dialog__07_user.mp3</a></audio> |
| 08 | **agent** | Spätestens bis Freitag, den dreiundzwanzigsten Mai, achtzehn Uhr. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__08_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__08_agent.mp3">⬇ xtts__dialog__08_agent.mp3</a></audio> |
| 09 | **user** | Wunderbar. Vielen Dank für die Information, auf Wiederhören. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__09_user.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__09_user.mp3">⬇ xtts__dialog__09_user.mp3</a></audio> |
| 10 | **agent** | Vielen Dank, einen schönen Tag noch. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__10_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/xtts__dialog__10_agent.mp3">⬇ xtts__dialog__10_agent.mp3</a></audio> |

### Coqui Thorsten-VITS DE

| # | Sprecher | Text | Audio (Player) |
|---|---|---|---|
| 00 | **agent** | Guten Tag, hier spricht die Buchhaltung von Servas AI. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__00_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__00_agent.mp3">⬇ thorsten__dialog__00_agent.mp3</a></audio> |
| 01 | **agent** | Wir benötigen noch Ihre Rechnung vom April zweitausendsechsundzwanzig. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__01_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__01_agent.mp3">⬇ thorsten__dialog__01_agent.mp3</a></audio> |
| 02 | **user** | Guten Tag. Können Sie mir sagen, wo ich diese Rechnung finde? | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__02_user.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__02_user.mp3">⬇ thorsten__dialog__02_user.mp3</a></audio> |
| 03 | **agent** | Selbstverständlich. Die finden Sie in Ihrem Kundenportal unter dem Punkt Rechnungen. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__03_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__03_agent.mp3">⬇ thorsten__dialog__03_agent.mp3</a></audio> |
| 04 | **user** | Verstehe. Und wo genau soll ich die Datei dann hochladen? | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__04_user.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__04_user.mp3">⬇ thorsten__dialog__04_user.mp3</a></audio> |
| 05 | **agent** | Sie erhalten gleich eine E-Mail mit einem persönlichen Upload-Link. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__05_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__05_agent.mp3">⬇ thorsten__dialog__05_agent.mp3</a></audio> |
| 06 | **agent** | Bitte laden Sie die Rechnung über diesen Link hoch, nicht per Antwort-Mail. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__06_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__06_agent.mp3">⬇ thorsten__dialog__06_agent.mp3</a></audio> |
| 07 | **user** | Alles klar. Bis wann muss das erledigt sein? | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__07_user.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__07_user.mp3">⬇ thorsten__dialog__07_user.mp3</a></audio> |
| 08 | **agent** | Spätestens bis Freitag, den dreiundzwanzigsten Mai, achtzehn Uhr. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__08_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__08_agent.mp3">⬇ thorsten__dialog__08_agent.mp3</a></audio> |
| 09 | **user** | Wunderbar. Vielen Dank für die Information, auf Wiederhören. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__09_user.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__09_user.mp3">⬇ thorsten__dialog__09_user.mp3</a></audio> |
| 10 | **agent** | Vielen Dank, einen schönen Tag noch. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__10_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/thorsten__dialog__10_agent.mp3">⬇ thorsten__dialog__10_agent.mp3</a></audio> |

### Piper TTS (Rhasspy)

| # | Sprecher | Text | Audio (Player) |
|---|---|---|---|
| 00 | **agent** | Guten Tag, hier spricht die Buchhaltung von Servas AI. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__00_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__00_agent.mp3">⬇ piper__dialog__00_agent.mp3</a></audio> |
| 01 | **agent** | Wir benötigen noch Ihre Rechnung vom April zweitausendsechsundzwanzig. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__01_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__01_agent.mp3">⬇ piper__dialog__01_agent.mp3</a></audio> |
| 02 | **user** | Guten Tag. Können Sie mir sagen, wo ich diese Rechnung finde? | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__02_user.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__02_user.mp3">⬇ piper__dialog__02_user.mp3</a></audio> |
| 03 | **agent** | Selbstverständlich. Die finden Sie in Ihrem Kundenportal unter dem Punkt Rechnungen. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__03_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__03_agent.mp3">⬇ piper__dialog__03_agent.mp3</a></audio> |
| 04 | **user** | Verstehe. Und wo genau soll ich die Datei dann hochladen? | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__04_user.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__04_user.mp3">⬇ piper__dialog__04_user.mp3</a></audio> |
| 05 | **agent** | Sie erhalten gleich eine E-Mail mit einem persönlichen Upload-Link. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__05_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__05_agent.mp3">⬇ piper__dialog__05_agent.mp3</a></audio> |
| 06 | **agent** | Bitte laden Sie die Rechnung über diesen Link hoch, nicht per Antwort-Mail. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__06_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__06_agent.mp3">⬇ piper__dialog__06_agent.mp3</a></audio> |
| 07 | **user** | Alles klar. Bis wann muss das erledigt sein? | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__07_user.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__07_user.mp3">⬇ piper__dialog__07_user.mp3</a></audio> |
| 08 | **agent** | Spätestens bis Freitag, den dreiundzwanzigsten Mai, achtzehn Uhr. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__08_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__08_agent.mp3">⬇ piper__dialog__08_agent.mp3</a></audio> |
| 09 | **user** | Wunderbar. Vielen Dank für die Information, auf Wiederhören. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__09_user.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__09_user.mp3">⬇ piper__dialog__09_user.mp3</a></audio> |
| 10 | **agent** | Vielen Dank, einen schönen Tag noch. | <audio controls preload="none"><source src="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__10_agent.mp3" type="audio/mpeg"><a href="https://raw.githubusercontent.com/vibecode-vm/german-tts-modal-benchmark/main/audio_mp3/piper__dialog__10_agent.mp3">⬇ piper__dialog__10_agent.mp3</a></audio> |

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

## 🚫 Ausgeschlossene Speech-to-Speech Modelle (Top-5 Leaderboard)

Die Artificial Analysis S2S-Leaderboard listet diese 5 als Top-Performer. Keiner ist für deutsche Voice-Agents im Mai 2026 nutzbar:

| Modell | Score (Conv. Dyn.) | Sprachen | Status | Warum nicht im Test |
|---|---:|---|---|---|
| **PersonaPlex 7B** (NVIDIA) | 91.0 % | Englisch | Open Weights (gated) | HF-Card: *„can generate English speech response for English speech input"* — kein Deutsch im Training |
| **Nemotron 3 VoiceChat 12B** | 77.8 % | 9 Sprachen inkl. **Deutsch** | 🚧 **Early Access** | NVIDIA-Approval nötig, Weights nicht öffentlich downloadbar |
| **FLM-Audio 7-8B** (CofeAI) | 62.0 % | Chinesisch + Englisch | Apache-2.0 (research-only) | Trainingsdaten: ZH+EN, keine DE-Transfer-Behauptung |
| **Moshi 7B** (Kyutai) | 61.0 % | Englisch | MIT | FAQ-Zitat: *„Moshi only speaks English"* |
| **Freeze-Omni 7B + Qwen2** | 58.7 % | Chinesisch + Englisch | Apache-2.0 | Training: 110k h ZH+EN Audio, kein DE |

### Nemotron 3 VoiceChat 12B — Sprachen im Detail

NVIDIA gibt die Liste nicht direkt raus. Über das TTS-Backbone **[Magpie TTS Multilingual 357M](https://huggingface.co/nvidia/magpie_tts_multilingual_357m)** sind **9 Sprachen** bestätigt:

| ✅ Unterstützt | ❌ NICHT im 9-Set |
|---|---|
| Englisch · **Deutsch** · Französisch · Spanisch | Portugiesisch · Koreanisch · Arabisch · Russisch |
| Italienisch · Vietnamesisch · Chinesisch · Hindi · Japanisch | Niederländisch · Polnisch · Türkisch |

> Caveat: Die ASR-Seite (Sprach-Eingabe verstehen) könnte abweichen — nicht dokumentiert. Die '12 Sprachen' im GTC-Press-Release beziehen sich auf **Nemotron Content Safety**, NICHT auf VoiceChat.

---

*Generated by [`build_report.py`](client/build_report.py) from `reports/benchmark_results.json`.*
