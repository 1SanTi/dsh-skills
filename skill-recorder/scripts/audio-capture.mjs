/**
 * 录音 + **实时**语音转写（录制时用）。
 *
 * 设计要点：
 * - 麦克风只能被 App/WebView 持有，所以用一个本地页面当“麦克风载体”；
 * - 页面里用 WebAudio 边录边切 4 秒窗口，本地 WASM Whisper（whisper-tiny，模型全在本机）
 *   逐窗识别，**边说边出字**（不再等停止后整段转写）；
 * - 识别结果即时 POST /transcript，同时显示在页面上；
 * - 同时用 MediaRecorder 存一份 narration.webm 作为原始录音留档。
 */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const SKILL_DIR = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const ASR_ROOT = path.join(SKILL_DIR, 'asr');
const MIME = {
  '.js': 'text/javascript',
  '.wasm': 'application/wasm',
  '.json': 'application/json',
  '.onnx': 'application/octet-stream',
};

export function startAudioCapture(dir, log = () => {}) {
  const state = { stop: false, audio: null, bytes: 0, lines: [], served: 0, startedAt: Date.now() };

  const PAGE = `<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>录音中</title>
<style>
body{font:17px system-ui;background:#0b0b0d;color:#eee;margin:0;padding:24px;line-height:1.6}
.dot{display:inline-block;width:14px;height:14px;border-radius:50%;background:#ef4444;animation:p 1.2s infinite;margin-right:8px}
@keyframes p{50%{opacity:.25}}
#s{color:#a3a3a3;font-size:15px}
#t{font-size:22px;color:#7dd3fc;white-space:pre-wrap;margin-top:14px;min-height:3em}
#log{color:#4b5563;font-size:13px;white-space:pre-wrap;margin-top:18px}
</style></head>
<body>
<div><span class="dot"></span><b>录音中 · 实时转写</b></div>
<div id="s">加载模型…</div>
<div id="t"></div>
<div id="log"></div>
<script type="module">
const S=(m)=>{document.getElementById('s').textContent=m};
const LOG=(m)=>{const el=document.getElementById('log');el.textContent=(m+"\\n"+el.textContent).split("\\n").slice(0,6).join("\\n")};
const SR=16000, WIN=4*SR, OVER=Math.round(0.3*SR);

let asr=null, loading=null, ctx=null, src=null, proc=null, stream=null, mr=null, chunks=[];
let pcm=[], consumed=0, busy=false, stopped=false, lastLine='';

async function loadModel(){
  if (asr || loading) return loading;
  loading=(async()=>{
    S('加载本地 Whisper 模型…');
    const { pipeline, env } = await import('/v/transformers.min.js');
    env.allowRemoteModels=false; env.allowLocalModels=true; env.localModelPath='/models/';
    env.backends.onnx.wasm.wasmPaths='/v/'; env.backends.onnx.wasm.numThreads=1;
    asr=await pipeline('automatic-speech-recognition','whisper-tiny',{quantized:true});
    S('模型就绪，边说边转写');
    LOG('model ready');
    return asr;
  })();
  return loading;
}

function addLine(text){
  text=String(text||'').trim();
  if(!text) return;
  const norm=text.replace(/[\s，。,.、！!？?…~-]/g,'');
  if(!norm) return;
  if(/^(我|你|好|嗯|啊|哦|的|是|了|这)$/.test(norm)) return;  // 单字噪声
  if(text===lastLine) return;
  if(lastLine && (lastLine.includes(text) || text.includes(lastLine))) return; // 窗口重叠重复
  lastLine=text;
  const t=document.getElementById('t');
  t.textContent = (t.textContent? t.textContent+'\\n' : '') + text;
  t.scrollIntoView(false);
  fetch('/transcript',{method:'POST',headers:{'content-type':'application/json'},
    body:JSON.stringify({t:Date.now(),text,final:true})}).catch(()=>{});
}

function concat(){
  let n=0; for(const a of pcm) n+=a.length;
  const out=new Float32Array(n); let o=0;
  for(const a of pcm){ out.set(a,o); o+=a.length; }
  return out;
}
function compact(){
  // 丢掉已经完全消费掉的整块，控制内存
  let dropped=0;
  while(pcm.length && dropped + pcm[0].length <= consumed){
    dropped += pcm[0].length; pcm.shift();
  }
  if(dropped) consumed-=dropped;
}
function to16k(input, rate){
  if(rate===SR) return input;
  const ratio=rate/SR, len=Math.floor(input.length/ratio);
  const out=new Float32Array(len);
  for(let i=0;i<len;i++){
    const p=i*ratio, i0=Math.floor(p), i1=Math.min(i0+1,input.length-1), f=p-i0;
    out[i]=input[i0]*(1-f)+input[i1]*f;
  }
  return out;
}

function rms(a){ let s=0; for(let i=0;i<a.length;i++) s+=a[i]*a[i]; return Math.sqrt(s/(a.length||1)); }
// 有声比例：语音是有起伏的，环境噪声相对平；用它当第二道闸
function activeRatio(a,th=0.02){ let n=0; for(let i=0;i<a.length;i++) if(Math.abs(a[i])>th) n++; return n/(a.length||1); }
let noiseFloor=0.006;   // 自适应环境底噪

async function pump(){
  if(stopped || busy || !asr) return;
  const all=concat();
  if(all.length-consumed < WIN*0.6) return;   // 不足 2.4 秒先等
  busy=true;
  try{
    const end=Math.min(all.length, consumed+WIN);
    const win=all.slice(consumed, end);
    consumed=end-OVER>consumed? end-OVER : end;
    compact();
    const level=rms(win), ratio=activeRatio(win);
    // 静音判定：低于自适应底噪的 2.5 倍，或几乎没有超过 0.02 的采样点
    const silent = level < Math.max(0.01, noiseFloor*2.5) || ratio < 0.04;
    if(silent){
      noiseFloor = noiseFloor*0.92 + level*0.08;   // 只在“像噪声”时更新底噪
      LOG('skip level='+level.toFixed(4)+' ratio='+ratio.toFixed(3)+' floor='+noiseFloor.toFixed(4));
      busy=false; return;
    }
    LOG('asr  level='+level.toFixed(4)+' ratio='+ratio.toFixed(3)+' floor='+noiseFloor.toFixed(4));
    const out=await asr(win,{language:'chinese',task:'transcribe'});
    addLine(out && out.text);
  }catch(e){ LOG('asr error: '+e); }
  busy=false;
}

async function boot(){
  try{
    stream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true}});
    S('麦克风已开，加载模型…');

    // 1) 留档用的原始录音（webm/opus）
    try{
      const mime=MediaRecorder.isTypeSupported('audio/webm;codecs=opus')?'audio/webm;codecs=opus':'audio/webm';
      mr=new MediaRecorder(stream,{mimeType:mime,audioBitsPerSecond:64000});
      mr.ondataavailable=e=>{ if(e.data.size) chunks.push(e.data); };
      mr.onstop=async()=>{
        const blob=new Blob(chunks,{type:mr.mimeType||'audio/webm'});
        try{ await fetch('/upload',{method:'POST',body:blob,headers:{'content-type':blob.type}}); }catch(e){}
        document.getElementById('s').textContent='已保存';
      };
      mr.start(1000);
    }catch(e){ LOG('recorder: '+e); }

    // 2) 实时识别用的 PCM 流
    ctx=new (window.AudioContext||window.webkitAudioContext)({sampleRate:SR});
    src=ctx.createMediaStreamSource(stream);
    proc=ctx.createScriptProcessor(4096,1,1);
    proc.onaudioprocess=(ev)=>{
      if(stopped) return;
      const raw=ev.inputBuffer.getChannelData(0);
      pcm.push(to16k(new Float32Array(raw), ctx.sampleRate));
    };
    src.connect(proc); proc.connect(ctx.destination);

    loadModel().catch(e=>{ S('模型加载失败: '+e); LOG('model fail: '+e); });
    setInterval(pump, 700);

    setInterval(async()=>{
      if(stopped) return;
      try{
        const s=await fetch('/status').then(r=>r.json());
        if(s.stop){
          stopped=true;
          try{ await pump(); }catch(e){}
          try{ proc&&proc.disconnect(); }catch(e){}
          try{ src&&src.disconnect(); }catch(e){}
          try{ mr&&mr.stop(); }catch(e){}
          try{ stream.getTracks().forEach(t=>t.stop()); }catch(e){}
          S('已停止');
        }
      }catch(e){}
    },700);
  }catch(e){ S('麦克风失败: '+e); }
}
boot();
</script></body></html>`;

  const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://127.0.0.1');
    const send = (code, body, type = 'application/json') => {
      res.writeHead(code, { 'content-type': type });
      res.end(body);
    };
    if (url.pathname === '/audio') return send(200, PAGE, 'text/html; charset=utf-8');
    if (url.pathname === '/status') return send(200, JSON.stringify({ stop: state.stop, lines: state.lines.length, audio: !!state.audio }));
    if (url.pathname === '/stop' && req.method === 'POST') {
      state.stop = true;
      return send(200, '{"ok":true}');
    }
    if (url.pathname === '/upload' && req.method === 'POST') {
      const file = path.join(dir, 'narration.webm');
      const ws = fs.createWriteStream(file);
      let bytes = 0;
      req.on('data', (d) => {
        bytes += d.length;
        ws.write(d);
      });
      req.on('end', () => {
        ws.end();
        state.audio = file;
        state.bytes = bytes;
        send(200, JSON.stringify({ ok: true, bytes }));
      });
      return;
    }
    if (url.pathname === '/transcript' && req.method === 'POST') {
      let body = '';
      req.on('data', (d) => (body += d));
      req.on('end', () => {
        try {
          const o = JSON.parse(body);
          if (o.text) {
            state.lines.push({ t: o.t, text: String(o.text), final: !!o.final });
            fs.writeFileSync(path.join(dir, 'transcript.json'), JSON.stringify(state.lines, null, 1));
          }
        } catch {}
        send(200, '{"ok":true}');
      });
      return;
    }
    // 静态资源：/v/ 是 transformers.js + onnxruntime wasm，/models/ 是 whisper 模型
    let full = null;
    if (url.pathname.startsWith('/v/')) full = path.join(ASR_ROOT, 'web', url.pathname.slice(3));
    else if (url.pathname.startsWith('/models/')) full = path.join(ASR_ROOT, 'models', url.pathname.slice(8));
    if (full && full.startsWith(ASR_ROOT) && fs.existsSync(full)) {
      res.writeHead(200, { 'content-type': MIME[path.extname(full)] || 'application/octet-stream' });
      return fs.createReadStream(full).pipe(res);
    }
    send(404, 'not found', 'text/plain');
  });

  return new Promise((resolve) => {
    server.listen(0, '127.0.0.1', () => {
      const port = server.address().port;
      const url = `http://127.0.0.1:${port}/audio`;
      state.url = url;
      state.port = port;
      log(`audio page ${url} (实时转写)`);
      resolve({
        url,
        server,
        state,
        stopAndSave() {
          state.stop = true;
          return new Promise((r) =>
            setTimeout(() => {
              try {
                server.close();
              } catch {}
              if (state.lines.length) {
                try {
                  fs.writeFileSync(path.join(dir, 'transcript.json'), JSON.stringify(state.lines, null, 1));
                } catch {}
              }
              r({ audio: state.audio, bytes: state.bytes, lines: state.lines.length, path: state.audio });
            }, 4500)
          );
        },
      });
    });
  });
}
