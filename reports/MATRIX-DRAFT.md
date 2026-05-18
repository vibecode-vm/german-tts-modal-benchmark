# German Voice S2S/TTS Benchmark Matrix — Stand 2026-05-18

## Triage: Artificial Analysis Speech-to-Speech Leaderboard (top 5)

| Modell | Score (Conv. Dyn.) | Sprachen lt. Training | Open Weights | Deutsch? | Status |
|---|---:|---|---|---|---|
| **PersonaPlex 7B** | 91.0 % | Englisch | ✅ (gated HF) | ❌ | BLOCKER — nur Englisch |
| **Nemotron 3 VoiceChat 12B** | 77.8 % | 9 Sprachen lt. NVIDIA (inkl. DE) | 🚧 Early Access | ✅ vermutlich | BLOCKER — Approval nötig |
| **FLM-Audio 7-8B** | 62.0 % | Chinesisch + Englisch | ✅ (Apache 2.0 code, research-only weights) | ❌ | BLOCKER — kein DE-Training |
| **Moshi 7B (Kyutai)** | 61.0 % | Englisch (FAQ: "Moshi only speaks English") | ✅ (MIT + CC-BY-4.0) | ❌ | BLOCKER — kein DE |
| **Freeze-Omni 7B + Qwen2** | 58.7 % | Chinesisch + Englisch | ✅ (Apache 2.0) | ❌ | BLOCKER — kein DE |

**Befund:** Die Top-5 der S2S-Leaderboard ist im Mai 2026 effektiv ein Englisch+Chinesisch-Club.
Für **deutsche Voice-Agenten** auf Modal ist im Open-Weights-Raum **keine** dieser S2S-Modelle direkt benutzbar.
Die einzige Option mit Anspruch auf Deutsch-Qualität (Nemotron VoiceChat) ist nicht zugänglich.

---

## Deutsch-kompatible TTS auf Modal (tatsächlich deploybar)

| Modell | Größe | Lizenz | GPU | $/min aktiv | DE-Qualität (Quelle) |
|---|---:|---|---|---:|---|
| **NVIDIA Magpie-TTS Multilingual 357M** | 1.4 GB | NVIDIA OML, kommerziell OK | L4 | ~0,013 $ | CER 0,66 %, SV-SSIM 0,626 auf CML-TTS DE; Arena Elo ~1063 |
| **Coqui XTTS-v2** | ~1.8 GB | CPML, **nicht-kommerziell** | L4 | ~0,013 $ | 2023er Architektur, etabliert |
| **F5-TTS German FT** | ~1.4 GB | CC-BY-NC, **nicht-kommerziell** | L4 | ~0,013 $ | gut bei kurzen Sätzen |
| **Orpheus 3B German FT** | ~6 GB | Apache 2.0 (+ Llama base) | L40S | ~0,033 $ | von Community "sehr gut" |

---

## Live-Benchmark — Magpie TTS DE auf Modal L4

*(Daten werden eingetragen sobald Test fertig)*

### Setup
- GPU: NVIDIA L4 (24 GB)
- Modal `scaledown_window=20s`, `min_containers=0`
- Modell: `nvidia/magpie_tts_multilingual_357m`
- NeMo Commit: `ccbbfbbdb3a4` (main, 2026-05-14) — Pipecat-Pin enthielt kein `HindiCharsTokenizer`
- Endpoint: HTTPS POST `/tts` → 22 kHz Mono WAV

### Latenz (TBD)
| Voice | Cold-Start | Avg Synth-Time | Avg RTF | Avg Wall-Time |
|---|---:|---:|---:|---:|
| sofia | – | – | – | – |
| aria | – | – | – | – |
| leo | – | – | – | – |

### Audio-Qualität (TBD)
| Voice | Whisper-Roundtrip CER | Whisper-Roundtrip WER |
|---|---:|---:|
| sofia | – | – |
| aria | – | – |
| leo | – | – |

### Cost-Tally (TBD)
| Phase | Sekunden | $-Burn |
|---|---:|---:|
| Deploy 1 (crash-loop) | – | – |
| Deploy 2 (live) | – | – |
| Tests | – | – |
| **Total** | – | – |

---

## Empfehlung

*(wird nach Live-Test gefüllt)*
