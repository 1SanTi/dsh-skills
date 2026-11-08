const OUT = "/storage/emulated/0/Download/工作室资料";
import fs from "node:fs";
import path from "node:path";
const API = "https://tcs.eaes.cn/api/api-tcs/resource/anon/downloadUrls";
export async function fetchUrls(ids){
  const r = await fetch(API,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(ids)});
  if(!r.ok) throw new Error("API "+r.status);
  const j = await r.json();
  if(!Array.isArray(j.data)) throw new Error("no data "+JSON.stringify(j).slice(0,200));
  return j.data;
}
export function nameFromUrl(u){
  try{
    const q = new URL(u).searchParams.get("response-content-disposition")||"";
    const m = q.match(/filename\*=UTF-8''([^;]+)/i) || q.match(/filename="?([^";]+)"?/i);
    if(m) return decodeURIComponent(m[1].replace(/['"]/g,""));
  }catch{}
  return null;
}
export async function downloadId(id){
  const data = await fetchUrls([id]);
  const d = data[0];
  const url = d.downloadUrl;
  const name = nameFromUrl(url) || (id + ".bin");
  const res = await fetch(url);
  if(!res.ok) throw new Error("GET "+res.status);
  const buf = Buffer.from(await res.arrayBuffer());
  fs.mkdirSync(OUT,{recursive:true});
  const dest = path.join(OUT, name);
  if(fs.existsSync(dest) && fs.statSync(dest).size === buf.length){ return {name, size:buf.length, skipped:true}; }
  fs.writeFileSync(dest, buf);
  return {name, size:buf.length};
}
if(process.argv[2]){
  downloadId(process.argv[2]).then(r=>console.log(JSON.stringify(r))).catch(e=>{console.error("ERR",e.message);process.exit(1)});
}
