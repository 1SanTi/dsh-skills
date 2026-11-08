#!/usr/bin/env node
/** 浏览器内 Whisper（transformers.js）：把本地音频转成文字，结果 POST 回来。 */
import http from 'node:http';
import fs from 'node:fs';

const PORT = Number(process.env.ASR_PORT || 3801);
const AUDIO = process.argv[2];
if (!AUDIO || !fs.existsSync(AUDIO)) { console.error('usage: asr-server.mjs <audio.webm>'); process.exit(1); }

let result = null;
const PAGE = `<!doctype html><html><head><meta charset="utf-8"><title>转写中</title>
<style>body{font:18px system-ui;background:#0b0b0d;color:#eee;padding:24px}#t{white-space:pre-wrap;color:#7dd3fc;font-size:22px;line-height:1.6}</style></head>
<body><div id="s">加载模型…</div><div id="t"></div>
<script type="module">
import { pipeline, env } from 'https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2/+esm';
env.remoteHost = 'https://hf-mirror.com';
env.remotePathTemplate = '{model}/resolve/{revision}/';
env.allowLocalModels = false;
const S=(m)=>{document.getElementById('s').textContent=m};
try{
  S('加载语音模型（首次约 40MB）…');
  const asr = await pipeline('automatic-speech-recognition','Xenova/whisper-tiny',{quantized:true});
  S('读取音频…');
  const buf = await (await fetch('/file')).arrayBuffer();
  const ctx = new (window.AudioContext||window.webkitAudioContext)({sampleRate:16000});
  const audio = await ctx.decodeAudioData(buf);
  const data = audio.getChannelData(0);
  S('识别中（'+Math.round(audio.duration)+' 秒音频）…');
  const out = await asr(data, {language:'chinese', task:'transcribe', chunk_length_s:30});
  document.getElementById('t').textContent = out.text || '';
  S('完成');
  fetch('/result',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({text:out.text||'',duration:audio.duration})});
}catch(e){ S('失败: '+e); fetch('/result',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({error:String(e)})}); }
</script></body></html>`;

const server = http.createServer((req, res) => {
  const u = new URL(req.url, 'http://127.0.0.1');
  if (u.pathname === '/') { res.writeHead(200, {'content-type':'text/html; charset=utf-8'}); res.end(PAGE); return; }
  if (u.pathname === '/file') { res.writeHead(200, {'content-type':'audio/webm'}); fs.createReadStream(AUDIO).pipe(res); return; }
  if (u.pathname === '/result' && req.method === 'POST') {
    let b=''; req.on('data',d=>b+=d); req.on('end',()=>{ try{result=JSON.parse(b);}catch{result={raw:b}}; res.writeHead(200,{'content-type':'application/json'}); res.end('{"ok":true}'); });
    return;
  }
  if (u.pathname === '/result') { res.writeHead(200,{'content-type':'application/json'}); res.end(JSON.stringify(result||{pending:true})); return; }
  res.writeHead(404); res.end('nf');
});
server.listen(PORT,'127.0.0.1',()=>console.log(JSON.stringify({ok:true,url:`http://127.0.0.1:${PORT}/`})));
