#!/usr/bin/env node
/**
 * 本地 Whisper 转写（浏览器 WASM，模型与 JS 全部本机，不联网）：
 *   node scripts/asr-local.mjs <audio.webm> <sessionDir>
 * 起一个本地页面 → 浏览器里跑 whisper-tiny → 把结果写 transcript.json，
 * 然后再跑一次 compile，把旁白并进回放稿。
 */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync, spawnSync } from 'node:child_process';

const SKILL_DIR = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const ROOT = path.join(SKILL_DIR, 'asr');
const AUDIO = process.argv[2];
const SESSION_DIR = process.argv[3];
const PORT = Number(process.env.ASR_PORT || 3802);
if (!AUDIO || !fs.existsSync(AUDIO) || !SESSION_DIR) {
  console.error('usage: asr-local.mjs <audio.webm> <sessionDir>');
  process.exit(2);
}
let result = null;
const PAGE = `<!doctype html><html><head><meta charset="utf-8"><title>本地转写</title>
<style>body{font:17px system-ui;background:#0b0b0d;color:#eee;padding:24px;line-height:1.6}#t{color:#7dd3fc;white-space:pre-wrap;font-size:20px;margin-top:12px}</style></head>
<body><div id="s">加载…</div><div id="t"></div>
<script type="module">
const S=(m)=>{document.getElementById('s').textContent=m};
try{
 const { pipeline, env } = await import('/v/transformers.min.js');
 env.allowRemoteModels=false; env.allowLocalModels=true; env.localModelPath='/models/';
 env.backends.onnx.wasm.wasmPaths='/v/'; env.backends.onnx.wasm.numThreads=1;
 S('加载 Whisper 模型…');
 const asr = await pipeline('automatic-speech-recognition','whisper-tiny',{quantized:true});
 S('解码音频…');
 const buf = await (await fetch('/file')).arrayBuffer();
 const ctx = new (window.AudioContext||window.webkitAudioContext)({sampleRate:16000});
 const audio = await ctx.decodeAudioData(buf);
 S('识别中（'+audio.duration.toFixed(1)+' 秒）…');
 const out = await asr(audio.getChannelData(0), {language:'chinese', task:'transcribe', chunk_length_s:30});
 document.getElementById('t').textContent = out.text||'';
 S('完成');
 fetch('/result',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({text:out.text||'', duration:audio.duration})});
}catch(e){ S('失败: '+e); fetch('/result',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({error:String(e)})}); }
</script></body></html>`;
const MIME = { '.js': 'text/javascript', '.wasm': 'application/wasm', '.json': 'application/json', '.onnx': 'application/octet-stream' };
const server = http.createServer((req, res) => {
  const u = new URL(req.url, 'http://127.0.0.1');
  const send = (code, body, type = 'application/json') => { res.writeHead(code, { 'content-type': type }); res.end(body); };
  if (u.pathname === '/') return send(200, PAGE, 'text/html; charset=utf-8');
  if (u.pathname === '/file') { res.writeHead(200, { 'content-type': 'audio/webm' }); return fs.createReadStream(AUDIO).pipe(res); }
  if (u.pathname === '/result' && req.method === 'POST') { let b=''; req.on('data',d=>b+=d); req.on('end',()=>{ try { result = JSON.parse(b); } catch { result = { raw: b }; } send(200, '{"ok":true}'); }); return; }
  if (u.pathname === '/result') return send(200, JSON.stringify(result || { pending: true }));
  let full = null;
  if (u.pathname.startsWith('/v/')) full = path.join(ROOT, 'web', u.pathname.slice(3));
  else if (u.pathname.startsWith('/models/')) full = path.join(ROOT, 'models', u.pathname.slice(8));
  if (full && full.startsWith(ROOT) && fs.existsSync(full)) {
    res.writeHead(200, { 'content-type': MIME[path.extname(full)] || 'application/octet-stream' });
    return fs.createReadStream(full).pipe(res);
  }
  send(404, 'nf', 'text/plain');
});
server.listen(PORT, '127.0.0.1', async () => {
  if (process.env.ASR_HEADLESS !== '1') { try { execFileSync('shz', ['am', 'start', '-a', 'android.intent.action.VIEW', '-d', `http://127.0.0.1:${PORT}/`], { timeout: 8000 }); } catch {} } else { console.log('headless: open http://127.0.0.1:' + PORT + '/ in a browser'); }
  const deadline = Date.now() + 6 * 60 * 1000;
  while (Date.now() < deadline && !result) await new Promise((r) => setTimeout(r, 2000));
  const out = result || { error: 'timeout' };
  const text = String(out.text || '');
  const sessionId = path.basename(SESSION_DIR);
  if (text) {
    const meta = (() => { try { return JSON.parse(fs.readFileSync(path.join(SESSION_DIR, 'meta.json'), 'utf8')); } catch { return {}; } })();
    const start = Date.parse(meta.startedAt || '') || Date.now();
    const line = { t: start + 2000, text: text.replace(/(嗯[，,、]?)+/g, '嗯…').replace(/\s+/g, ' ').trim(), final: true };
    fs.writeFileSync(path.join(SESSION_DIR, 'transcript.json'), JSON.stringify([line], null, 1));
    try { spawnSync(process.execPath, [path.join(SKILL_DIR, 'scripts', 'recorder.mjs'), 'compile', '--session', sessionId], { timeout: 60000 }); } catch {}
  }
  fs.writeFileSync(path.join(SESSION_DIR, 'asr-result.json'), JSON.stringify(out, null, 1));
  try { server.close(); } catch {}
  process.exit(text ? 0 : 1);
});
