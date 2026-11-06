import http from 'node:http';
const PORT = Number(process.env.SPEECH_PORT || 3800);
const PAGE = `<!doctype html><html><head><meta charset="utf-8"><title>语音测试</title>
<style>body{font:20px system-ui;background:#111;color:#eee;padding:24px} #t{font-size:24px;min-height:3em;margin-top:20px;color:#7dd3fc}</style></head>
<body><h3>系统语音识别测试</h3><div id="s">初始化…</div><div id="t"></div>
<script>
const S=(window.SpeechRecognition||window.webkitSpeechRecognition);
if(!S){document.getElementById('s').textContent='浏览器不支持 SpeechRecognition';}
else{
 const rec=new S(); rec.lang='zh-CN'; rec.continuous=true; rec.interimResults=true;
 rec.onresult=(e)=>{let s='';for(const r of e.results)s+=r[0].transcript;document.getElementById('t').textContent=s;};
 rec.onerror=(e)=>{document.getElementById('s').textContent='错误: '+e.error;};
 rec.onstart=()=>{document.getElementById('s').textContent='识别中，请说话';};
 rec.start();
}
</script></body></html>`;
http.createServer((req,res)=>{ res.writeHead(200,{'content-type':'text/html; charset=utf-8'}); res.end(PAGE); }).listen(PORT,'127.0.0.1',()=>console.log('speech on',PORT));
