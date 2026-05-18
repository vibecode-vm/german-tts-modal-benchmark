"""Piper TTS — German, CPU-only. The cheapest, fastest cold-start option.

Voice: `de_DE-thorsten-medium` (clean male voice, well-known German Piper voice).
"""
import io
import time
import wave

import modal

APP_NAME = "piper-de-tts"
SAMPLE_RATE = 22050  # Piper voices typically 22050

app = modal.App(APP_NAME)
voice_cache = modal.Volume.from_name("piper-voices", create_if_missing=True)
CACHE = "/voices"

image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("wget", "ca-certificates")
    .pip_install("piper-tts==1.3.0", "fastapi[standard]", "pydantic")
    .env({"PIPER_VOICES_DIR": CACHE})
)

with image.imports():
    import subprocess
    from pathlib import Path
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import Response
    from pydantic import BaseModel

    class TTSReq(BaseModel):
        text: str
        voice: str = "de_DE-thorsten-medium"   # also: de_DE-eva_k-x_low, de_DE-kerstin-low, de_DE-pavoque-low


VOICES = {
    "de_DE-thorsten-medium": ("https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx",
                              "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx.json"),
    "de_DE-eva_k-x_low":     ("https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/eva_k/x_low/de_DE-eva_k-x_low.onnx",
                              "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/eva_k/x_low/de_DE-eva_k-x_low.onnx.json"),
    "de_DE-kerstin-low":     ("https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/kerstin/low/de_DE-kerstin-low.onnx",
                              "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/kerstin/low/de_DE-kerstin-low.onnx.json"),
    "de_DE-pavoque-low":     ("https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/pavoque/low/de_DE-pavoque-low.onnx",
                              "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/pavoque/low/de_DE-pavoque-low.onnx.json"),
}


def _download_voice(voice: str) -> Path:
    cache = Path(CACHE) / voice
    cache.mkdir(parents=True, exist_ok=True)
    onnx = cache / f"{voice}.onnx"
    cfg  = cache / f"{voice}.onnx.json"
    if not onnx.exists() or not cfg.exists():
        if voice not in VOICES:
            raise ValueError(f"unknown voice: {voice}")
        u_onnx, u_cfg = VOICES[voice]
        subprocess.run(["wget", "-q", "-O", str(onnx), u_onnx], check=True)
        subprocess.run(["wget", "-q", "-O", str(cfg), u_cfg], check=True)
    return onnx


@app.cls(
    image=image,
    volumes={CACHE: voice_cache},
    cpu=2.0,
    memory=4096,
    timeout=300,
    scaledown_window=20,
)
class PiperDE:
    @modal.enter()
    def setup(self):
        # Pre-download default voice on container start
        for v in ["de_DE-thorsten-medium"]:
            try:
                _download_voice(v)
            except Exception as e:
                print(f"voice {v} download failed: {e}")

    def _synth(self, text: str, voice: str) -> tuple[bytes, float, float]:
        onnx = _download_voice(voice)
        t0 = time.perf_counter()
        proc = subprocess.run(
            ["piper", "--model", str(onnx), "--output-raw"],
            input=text.encode("utf-8"),
            capture_output=True, check=True,
        )
        synth_s = time.perf_counter() - t0
        pcm = proc.stdout
        audio_s = len(pcm) / 2 / SAMPLE_RATE
        return pcm, synth_s, audio_s

    @modal.asgi_app()
    def web(self):
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import HTMLResponse

        api = FastAPI(title="Piper DE TTS — Live Demo")
        api.add_middleware(
            CORSMiddleware,
            allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
        )

        @api.get("/health")
        def health(): return {"ok": True, "voices": list(VOICES)}

        @api.get("/", response_class=HTMLResponse)
        def demo():
            return HTML_DEMO_PAGE

        @api.post("/tts")
        def tts(req: TTSReq):
            if req.voice not in VOICES:
                raise HTTPException(400, f"voice must be one of {list(VOICES)}")
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
                    "X-Voice": req.voice, "X-Model": "piper-tts",
                },
            )
        return api


HTML_DEMO_PAGE = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Piper TTS Deutsch — Live Demo</title>
<style>
  :root { --bg:#0b0d12; --fg:#e8eaf0; --accent:#5b8def; --muted:#9ba3b4; --card:#161922; }
  * { box-sizing:border-box }
  body { font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif; background:var(--bg); color:var(--fg); margin:0; padding:24px; line-height:1.5 }
  .wrap { max-width:720px; margin:0 auto }
  h1 { margin:0 0 8px; font-size:28px }
  .sub { color:var(--muted); margin-bottom:24px }
  textarea, select, button { width:100%; font-size:16px; padding:12px; border-radius:8px; border:1px solid #2a2f3a; background:var(--card); color:var(--fg); font-family:inherit }
  textarea { min-height:120px; resize:vertical }
  button { background:var(--accent); border-color:var(--accent); color:white; font-weight:600; cursor:pointer; margin-top:12px }
  button:hover { filter:brightness(1.1) }
  button:disabled { opacity:0.6; cursor:wait }
  .row { display:flex; gap:8px; margin-top:12px }
  .row > * { flex:1 }
  audio { width:100%; margin-top:20px }
  .stats { color:var(--muted); font-size:14px; margin-top:10px; font-family:monospace }
  .footer { color:var(--muted); font-size:13px; margin-top:32px; padding-top:16px; border-top:1px solid #2a2f3a }
  a { color:var(--accent) }
  .preset { padding:8px 12px; background:var(--card); border:1px solid #2a2f3a; border-radius:6px; cursor:pointer; font-size:14px; color:var(--fg) }
  .preset:hover { border-color:var(--accent) }
  .presets { display:flex; flex-wrap:wrap; gap:6px; margin-top:8px }
</style>
</head>
<body>
<div class="wrap">
  <h1>🎙️ Piper TTS Deutsch — Live Demo</h1>
  <p class="sub">Schreib deutschen Text, drück Play. Synthetisiert von Piper TTS auf Modal (CPU, MIT-Lizenz, native Sprecher-Aufnahme).</p>

  <label for="text"><b>Text</b></label>
  <textarea id="text">Guten Tag, hier spricht die Buchhaltung von Servas AI. Wir benötigen noch Ihre Rechnung vom April. Sie erhalten gleich eine E-Mail mit einem Upload-Link.</textarea>

  <div class="presets">
    <button class="preset" data-preset="greeting">Begrüßung</button>
    <button class="preset" data-preset="invoice">Rechnung anfordern</button>
    <button class="preset" data-preset="numbers">Zahlen / Datum</button>
    <button class="preset" data-preset="closing">Abschluss</button>
  </div>

  <div class="row">
    <select id="voice">
      <option value="de_DE-thorsten-medium" selected>Thorsten (männlich, medium quality — empfohlen)</option>
      <option value="de_DE-eva_k-x_low">Eva K. (weiblich, x_low)</option>
      <option value="de_DE-kerstin-low">Kerstin (weiblich, low)</option>
      <option value="de_DE-pavoque-low">Pavoque (männlich, low)</option>
    </select>
  </div>

  <button id="play" onclick="synth()">▶ Synthetisieren & Abspielen</button>

  <audio id="audio" controls style="display:none"></audio>
  <div class="stats" id="stats"></div>

  <div class="footer">
    <p>Backend: Modal (serverless CPU, scale-to-zero, ~$0,05/h aktiv).<br>
    Code & Benchmarks: <a href="https://github.com/vibecode-vm/german-tts-modal-benchmark" target="_blank">github.com/vibecode-vm/german-tts-modal-benchmark</a></p>
  </div>
</div>

<script>
const PRESETS = {
  greeting: "Guten Tag, hier ist die Servas AI Buchhaltung. Schön, dass Sie anrufen.",
  invoice:  "Wir benötigen noch Ihre Rechnung vom April. Bitte laden Sie diese über den Link in der E-Mail hoch.",
  numbers:  "Ihre Bestellnummer ist drei-vier-sieben-acht. Der Betrag beträgt einhundertneunundzwanzig Euro und fünfzig Cent. Lieferung am dritten Juni zweitausendsechsundzwanzig.",
  closing:  "Großartig, vielen Dank für Ihr Vertrauen. Auf Wiederhören und einen schönen Tag noch.",
};
document.querySelectorAll('.preset').forEach(b => b.onclick = () => {
  document.getElementById('text').value = PRESETS[b.dataset.preset];
});

async function synth() {
  const btn = document.getElementById('play');
  const stats = document.getElementById('stats');
  const audio = document.getElementById('audio');
  const text = document.getElementById('text').value.trim();
  const voice = document.getElementById('voice').value;
  if (!text) { alert('Bitte Text eingeben'); return; }
  btn.disabled = true; btn.textContent = '⏳ Synthetisiere…';
  stats.textContent = '';
  const t0 = performance.now();
  try {
    const r = await fetch('/tts', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({text, voice, language:'de'})
    });
    if (!r.ok) throw new Error(r.status + ': ' + await r.text());
    const synthS = parseFloat(r.headers.get('X-Synth-Seconds')||'0');
    const audioS = parseFloat(r.headers.get('X-Audio-Seconds')||'0');
    const rtf = parseFloat(r.headers.get('X-RTF')||'0');
    const wall = ((performance.now()-t0)/1000).toFixed(2);
    const blob = await r.blob();
    const url = URL.createObjectURL(blob);
    audio.src = url; audio.style.display = 'block'; audio.play();
    stats.textContent = `Wall: ${wall}s · Synth: ${synthS.toFixed(2)}s · Audio: ${audioS.toFixed(2)}s · RTF: ${rtf.toFixed(3)} (${(1/rtf).toFixed(1)}× realtime)`;
  } catch (e) {
    stats.textContent = '❌ Fehler: ' + e.message;
  } finally {
    btn.disabled = false; btn.textContent = '▶ Synthetisieren & Abspielen';
  }
}
</script>
</body>
</html>
"""
