"""Live Voice Agent — push-to-talk German speech-to-speech demo.

Browser records mic audio → Whisper-base transcribes → rule-based accounting agent
responds → Piper synthesizes → browser plays. Per-phase latencies in response headers.

Architecture (1 CPU container, scale-to-zero):
- Whisper-base int8 CPU (~150 MB model, ~0.5s for short clips)
- Piper de_DE-thorsten-medium (~75 MB ONNX, ~1.5s synth)
- Rule-based agent (keyword matching, ~1ms)

Deploy: modal deploy app/voice_agent.py
"""
from __future__ import annotations

import io
import subprocess
import time
import wave
from pathlib import Path

import modal

APP_NAME = "voice-agent-de"
SAMPLE_RATE = 22050

app = modal.App(APP_NAME)
cache = modal.Volume.from_name("voice-agent-cache", create_if_missing=True)
CACHE = "/cache"
PIPER_VOICE_URL_ONNX = "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx"
PIPER_VOICE_URL_JSON = "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx.json"

image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("wget", "ffmpeg", "ca-certificates")
    .pip_install(
        "piper-tts==1.3.0",
        "faster-whisper==1.0.3",
        "numpy<2.0",
        "fastapi[standard]", "pydantic", "python-multipart",
    )
    .env({"HF_HOME": CACHE, "XDG_CACHE_HOME": CACHE})
)

with image.imports():
    from fastapi import FastAPI, UploadFile, File
    from fastapi.responses import Response, HTMLResponse
    from fastapi.middleware.cors import CORSMiddleware
    from faster_whisper import WhisperModel


# --- Rule-based agent (in lieu of an actual LLM) ----------------------------

AGENT_RULES = [
    # (keywords, response)
    (["hallo", "guten tag", "guten morgen", "servus"],
     "Guten Tag, hier spricht die Buchhaltung von Servas AI. Womit kann ich helfen?"),
    (["rechnung"],
     "Die Rechnung finden Sie in Ihrem Kundenportal unter dem Menüpunkt Rechnungen."),
    (["upload", "hochladen", "wie"],
     "Sie erhalten gleich eine E-Mail mit einem persönlichen Upload-Link. Bitte laden Sie die Datei dort hoch."),
    (["wann", "frist", "bis wann"],
     "Spätestens bis Freitag, den dreiundzwanzigsten Mai, achtzehn Uhr."),
    (["danke", "vielen dank"],
     "Sehr gerne. Falls Sie weitere Fragen haben, melden Sie sich. Auf Wiederhören."),
    (["wer", "wo bist du", "wer bin"],
     "Ich bin der Buchhaltungs-Bot von Servas AI. Powered by Piper TTS und Whisper, beides läuft auf Modal."),
    (["test"],
     "Test erfolgreich. Das Voice-Agent-System ist live."),
]
DEFAULT_RESPONSE = "Entschuldigung, das habe ich nicht verstanden. Können Sie das bitte wiederholen?"


def respond(user_text: str) -> str:
    t = user_text.lower()
    for keys, reply in AGENT_RULES:
        if any(k in t for k in keys):
            return reply
    return DEFAULT_RESPONSE


# --- Piper voice download helper --------------------------------------------

def _ensure_piper_voice() -> Path:
    cache = Path(CACHE) / "piper" / "de_DE-thorsten-medium"
    cache.mkdir(parents=True, exist_ok=True)
    onnx = cache / "model.onnx"
    cfg = cache / "model.onnx.json"
    if not onnx.exists():
        subprocess.run(["wget", "-q", "-O", str(onnx), PIPER_VOICE_URL_ONNX], check=True)
    if not cfg.exists():
        subprocess.run(["wget", "-q", "-O", str(cfg), PIPER_VOICE_URL_JSON], check=True)
    return onnx


@app.cls(
    image=image,
    volumes={CACHE: cache},
    cpu=4.0,
    memory=4096,
    timeout=300,
    scaledown_window=60,
)
class VoiceAgent:
    @modal.enter()
    def setup(self):
        t0 = time.perf_counter()
        print("Loading Whisper base int8...")
        self.whisper = WhisperModel("base", device="cpu", compute_type="int8",
                                     download_root=CACHE)
        print(f"Whisper loaded in {time.perf_counter()-t0:.1f}s")
        print("Downloading Piper voice...")
        self.piper_voice = _ensure_piper_voice()
        # Warmup Piper
        subprocess.run(["piper", "--model", str(self.piper_voice), "--output-raw"],
                       input=b"Hallo", capture_output=True, check=True)
        print(f"Voice agent ready in {time.perf_counter()-t0:.1f}s total")

    def _transcribe(self, wav_path: Path) -> tuple[str, float]:
        segs, info = self.whisper.transcribe(str(wav_path), language="de",
                                              beam_size=3, vad_filter=True)
        text = " ".join(s.text for s in segs).strip()
        return text, info.duration

    def _synthesize(self, text: str) -> bytes:
        proc = subprocess.run(
            ["piper", "--model", str(self.piper_voice), "--output-raw"],
            input=text.encode("utf-8"), capture_output=True, check=True,
        )
        pcm = proc.stdout
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SAMPLE_RATE)
            w.writeframes(pcm)
        return buf.getvalue()

    @modal.asgi_app()
    def web(self):
        api = FastAPI(title="Voice Agent DE — Live")
        api.add_middleware(CORSMiddleware, allow_origins=["*"],
                           allow_methods=["*"], allow_headers=["*"], expose_headers=["*"])

        @api.get("/", response_class=HTMLResponse)
        def page(): return HTML_PAGE

        @api.get("/health")
        def health(): return {"ok": True}

        @api.post("/turn")
        async def turn(audio: UploadFile = File(...)):
            t0 = time.perf_counter()
            wav_bytes = await audio.read()
            # Save mic upload to disk (Whisper reads file path)
            tmp = Path("/tmp") / f"in_{int(time.time()*1000)}.wav"
            tmp.write_bytes(wav_bytes)

            # 1. ASR
            t1 = time.perf_counter()
            user_text, audio_dur = self._transcribe(tmp)
            t_asr = time.perf_counter() - t1

            # 2. Agent (rule-based)
            t2 = time.perf_counter()
            reply = respond(user_text)
            t_agent = time.perf_counter() - t2

            # 3. TTS
            t3 = time.perf_counter()
            response_wav = self._synthesize(reply)
            t_tts = time.perf_counter() - t3

            try: tmp.unlink()
            except: pass

            return Response(
                content=response_wav,
                media_type="audio/wav",
                headers={
                    "X-User-Said": user_text[:500],
                    "X-Agent-Said": reply[:500],
                    "X-User-Audio-Seconds": f"{audio_dur:.3f}",
                    "X-ASR-Seconds": f"{t_asr:.3f}",
                    "X-Agent-Seconds": f"{t_agent:.4f}",
                    "X-TTS-Seconds": f"{t_tts:.3f}",
                    "X-Total-Seconds": f"{time.perf_counter()-t0:.3f}",
                    "Access-Control-Expose-Headers": "X-User-Said,X-Agent-Said,X-ASR-Seconds,X-Agent-Seconds,X-TTS-Seconds,X-Total-Seconds,X-User-Audio-Seconds",
                },
            )

        return api


HTML_PAGE = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>🎙️ Live Voice Agent DE — Servas AI Buchhaltung</title>
<style>
  :root { --bg:#0b0d12; --fg:#e8eaf0; --accent:#5b8def; --green:#22c55e; --red:#ef4444; --muted:#9ba3b4; --card:#161922; --line:#2a2f3a }
  * { box-sizing:border-box }
  body { font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif; background:var(--bg); color:var(--fg); margin:0; padding:20px; line-height:1.5; min-height:100vh }
  .wrap { max-width:720px; margin:0 auto }
  h1 { margin:0 0 4px; font-size:24px }
  .sub { color:var(--muted); margin:0 0 20px; font-size:14px }
  a { color:var(--accent) }
  #convo { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:14px; min-height:220px; max-height:50vh; overflow-y:auto; margin-bottom:14px }
  .msg { padding:10px 12px; border-radius:10px; margin:6px 0; font-size:15px }
  .user { background:#22324a; align-self:flex-end; margin-left:30px }
  .agent { background:#1d2b1f; margin-right:30px }
  .meta { color:var(--muted); font-size:11px; margin-top:4px; font-family:monospace }
  #status { color:var(--muted); font-size:13px; text-align:center; padding:10px; min-height:20px }
  .ctrl { display:flex; gap:10px; align-items:center }
  #ptt { flex:1; padding:18px; border-radius:99px; border:none; background:var(--accent); color:#fff; font-weight:700; font-size:17px; cursor:pointer; user-select:none; -webkit-user-select:none; transition:all .1s }
  #ptt:active, #ptt.rec { background:var(--red); transform:scale(0.98) }
  #ptt:disabled { opacity:.5; cursor:not-allowed }
  .lat { display:grid; grid-template-columns:repeat(5,1fr); gap:6px; margin:10px 0 6px; font-size:12px; font-family:monospace }
  .lat > div { padding:8px; border-radius:6px; background:var(--card); border:1px solid var(--line); text-align:center }
  .lat > div b { display:block; font-size:14px; color:var(--accent) }
  .lat > div.live b { color:var(--green); animation:pulse 0.7s infinite }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
  .footer { color:var(--muted); font-size:12px; margin-top:24px; padding-top:12px; border-top:1px solid var(--line) }
  .col { display:flex; flex-direction:column }
</style>
</head>
<body>
<div class="wrap">
  <h1>🎙️ Live Voice Agent · Deutsch</h1>
  <p class="sub">Drück + halte den Knopf, sprich deutsch (z.B. „Wo finde ich die Rechnung?"), lass los, hör die Antwort. Whisper + Rule-Agent + Piper, alles auf Modal-CPU.</p>

  <div id="convo" class="col"></div>

  <div class="lat">
    <div id="lat-asr"><b>—</b>ASR<br><span style="color:var(--muted)">Whisper</span></div>
    <div id="lat-agent"><b>—</b>Agent<br><span style="color:var(--muted)">Rules</span></div>
    <div id="lat-tts"><b>—</b>TTS<br><span style="color:var(--muted)">Piper</span></div>
    <div id="lat-net"><b>—</b>Network<br><span style="color:var(--muted)">RTT</span></div>
    <div id="lat-total"><b>—</b>Total<br><span style="color:var(--muted)">round-trip</span></div>
  </div>

  <div id="status">Bereit. Klicke den Knopf, halte ihn gedrückt, sprich, lass los.</div>

  <div class="ctrl">
    <button id="ptt">🎤 Push-to-talk — gedrückt halten</button>
  </div>

  <audio id="audio" autoplay style="display:none"></audio>

  <div class="footer">
    Backend: Modal CPU · Whisper-base int8 · Piper de_DE-thorsten-medium · <a href="https://github.com/vibecode-vm/german-tts-modal-benchmark" target="_blank">GitHub</a>
  </div>
</div>

<script>
const $ = id => document.getElementById(id);
let rec, chunks = [], stream;
const ptt = $('ptt'), st = $('status'), conv = $('convo'), aud = $('audio');

async function start() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({audio:true});
    rec = new MediaRecorder(stream, {mimeType:'audio/webm'});
    chunks = [];
    rec.ondataavailable = e => chunks.push(e.data);
    rec.onstop = onStop;
    rec.start();
    ptt.classList.add('rec');
    ptt.textContent = '🔴 Aufnahme… loslassen zum Senden';
    st.textContent = 'Höre dich…';
  } catch (e) {
    st.textContent = '❌ Mikrofon-Zugriff verweigert: ' + e.message;
  }
}

async function onStop() {
  ptt.classList.remove('rec');
  ptt.textContent = '🎤 Push-to-talk — gedrückt halten';
  st.textContent = '⏳ Verarbeite…';
  stream.getTracks().forEach(t=>t.stop());

  // Animate "thinking" on latency cells
  ['asr','agent','tts'].forEach(k => {
    const el = $('lat-'+k); el.classList.add('live'); el.querySelector('b').textContent='…';
  });
  ['net','total'].forEach(k => $('lat-'+k).querySelector('b').textContent='…');

  const blob = new Blob(chunks, {type:'audio/webm'});
  const fd = new FormData(); fd.append('audio', blob, 'mic.webm');

  const t0 = performance.now();
  try {
    const r = await fetch('/turn', {method:'POST', body:fd});
    const totalMs = performance.now() - t0;
    if (!r.ok) throw new Error(r.status + ': ' + await r.text());
    const u = r.headers.get('X-User-Said') || '(stille)';
    const a = r.headers.get('X-Agent-Said') || '';
    const tAsr = parseFloat(r.headers.get('X-ASR-Seconds')||'0');
    const tAg  = parseFloat(r.headers.get('X-Agent-Seconds')||'0');
    const tTts = parseFloat(r.headers.get('X-TTS-Seconds')||'0');
    const tTot = parseFloat(r.headers.get('X-Total-Seconds')||'0');
    const tNet = (totalMs/1000) - tTot;

    addMsg('user', u, `audio≈${parseFloat(r.headers.get('X-User-Audio-Seconds')||'0').toFixed(1)}s`);
    addMsg('agent', a, `total ${tTot.toFixed(2)}s · ASR ${tAsr.toFixed(2)}s · TTS ${tTts.toFixed(2)}s`);

    $('lat-asr').querySelector('b').textContent = (tAsr*1000).toFixed(0)+'ms';
    $('lat-agent').querySelector('b').textContent = (tAg*1000).toFixed(0)+'ms';
    $('lat-tts').querySelector('b').textContent = (tTts*1000).toFixed(0)+'ms';
    $('lat-net').querySelector('b').textContent = Math.max(0,(tNet*1000)).toFixed(0)+'ms';
    $('lat-total').querySelector('b').textContent = totalMs.toFixed(0)+'ms';
    ['asr','agent','tts','net','total'].forEach(k => $('lat-'+k).classList.remove('live'));

    const blob = await r.blob();
    aud.src = URL.createObjectURL(blob);
    aud.play();
    st.textContent = '✅ Bereit für die nächste Frage.';
  } catch (e) {
    st.textContent = '❌ ' + e.message;
    ['asr','agent','tts','net','total'].forEach(k => { $('lat-'+k).classList.remove('live'); $('lat-'+k).querySelector('b').textContent='—'; });
  }
}

function addMsg(who, text, meta) {
  const d = document.createElement('div'); d.className = 'msg ' + who;
  const speaker = who === 'user' ? '🧑 Du' : '🤖 Agent';
  d.innerHTML = `<b>${speaker}:</b> ${text}<div class="meta">${meta}</div>`;
  conv.appendChild(d); conv.scrollTop = conv.scrollHeight;
}

// Mouse + touch + space for PTT
ptt.addEventListener('mousedown', start);
ptt.addEventListener('touchstart', e => { e.preventDefault(); start(); });
window.addEventListener('mouseup', () => rec && rec.state === 'recording' && rec.stop());
window.addEventListener('touchend', () => rec && rec.state === 'recording' && rec.stop());
window.addEventListener('keydown', e => {
  if (e.code === 'Space' && (!rec || rec.state !== 'recording')) { e.preventDefault(); start(); }
});
window.addEventListener('keyup', e => {
  if (e.code === 'Space' && rec && rec.state === 'recording') { e.preventDefault(); rec.stop(); }
});
</script>
</body>
</html>
"""
