#!/usr/bin/env node
/**
 * 本地录音小服务：浏览器打开 http://127.0.0.1:3799/audio 后
 * 用 getUserMedia + MediaRecorder 录麦克风，录完把 blob POST 回来。
 * 只监听 127.0.0.1，页面与接口同源；不依赖任何第三方。
 */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const PORT = Number(process.env.AUDIO_PORT || 3799);
const OUT_DIR = process.env.AUDIO_OUT_DIR || '/data/user/0/app.dsh.mobile/files/dsh-home/tmpx/audio';
fs.mkdirSync(OUT_DIR, { recursive: true });

let stop = false;
let uploads = [];
let finalFile = null;
let startedAt = null;

const PAGE = `<!doctype html><html><head><meta charset="utf-8"><title>录音中</title>
<style>body{font:16px system-ui;background:#111;color:#eee;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;flex-direction:column;gap:16px} .dot{width:18px;height:18px;border-radius:50%;background:#ef4444;animation:p 1.2s infinite} @keyframes p{50%{opacity:.3}} pre{max-width:80vw;white-space:pre-wrap}</style>
</head><body><div class="dot"></div><div id="s">正在申请麦克风…</div><pre id="log"></pre>
<script>
let mr=null, chunks=[], stream=null, stopped=false;
const log=(m)=>{document.getElementById('log').textContent+=m+"\\n"};
async function boot(){
  try{
    stream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true}});
    const mime = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : 'audio/webm';
    mr=new MediaRecorder(stream,{mimeType:mime,audioBitsPerSecond:64000});
    mr.ondataavailable=e=>{ if(e.data.size) chunks.push(e.data); };
    mr.onstop=async()=>{
      document.getElementById('s').textContent='上传中…';
      const blob=new Blob(chunks,{type:mr.mimeType||'audio/webm'});
      try{ const r=await fetch('/upload',{method:'POST',body:blob,headers:{'content-type':blob.type}}); const j=await r.json(); document.getElementById('s').textContent='已保存 '+j.bytes+' 字节'; }
      catch(e){ document.getElementById('s').textContent='上传失败 '+e; }
    };
    mr.start(1000);
    document.getElementById('s').textContent='录音中';
    setInterval(async()=>{ if(stopped) return; try{ const s=await fetch('/status').then(r=>r.json()); if(s.stop){ stopped=true; mr.stop(); stream.getTracks().forEach(t=>t.stop()); } }catch(e){} },800);
  }catch(e){ document.getElementById('s').textContent='麦克风失败: '+e; }
}
boot();
</script></body></html>`;

const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://127.0.0.1');
  if (url.pathname === '/audio') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(PAGE);
    return;
  }
  if (url.pathname === '/status') {
    res.writeHead(200, { 'content-type': 'application/json' });
    res.end(JSON.stringify({ recording: !finalFile, stop, uploads: uploads.length, file: finalFile }));
    return;
  }
  if (url.pathname === '/stop' && req.method === 'POST') {
    stop = true;
    res.writeHead(200, { 'content-type': 'application/json' });
    res.end(JSON.stringify({ ok: true }));
    return;
  }
  if (url.pathname === '/upload' && req.method === 'POST') {
    const name = 'narration-' + Date.now() + '.webm';
    const file = path.join(OUT_DIR, name);
    const ws = fs.createWriteStream(file);
    let bytes = 0;
    req.on('data', (d) => { bytes += d.length; ws.write(d); });
    req.on('end', () => {
      ws.end();
      finalFile = file;
      uploads.push({ file, bytes });
      res.writeHead(200, { 'content-type': 'application/json' });
      res.end(JSON.stringify({ ok: true, file, bytes }));
    });
    return;
  }
  if (url.pathname === '/file') {
    if (!finalFile || !fs.existsSync(finalFile)) { res.writeHead(404); res.end('none'); return; }
    res.writeHead(200, { 'content-type': 'audio/webm' });
    fs.createReadStream(finalFile).pipe(res);
    return;
  }
  res.writeHead(404); res.end('not found');
});

server.listen(PORT, '127.0.0.1', () => {
  startedAt = new Date().toISOString();
  process.stdout.write(JSON.stringify({ ok: true, port: PORT, url: `http://127.0.0.1:${PORT}/audio` }) + '\n');
});
