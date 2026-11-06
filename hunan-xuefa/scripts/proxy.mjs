#!/usr/bin/env node
// 本地反代：把 127.0.0.1:3210 的请求转发到 hn.12348.gov.cn，并注入指定账号的 Cookie
// 用途：不重新登录也能用浏览器「看到」真实学法页面（截图取证）
// 用法: node proxy.mjs <手机号> [端口]
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.dirname(fileURLToPath(import.meta.url));
const phone = process.argv[2];
const port = Number(process.argv[3] || 3210);
const jar = JSON.parse(fs.readFileSync(path.join(DIR, `cookies-${phone}.json`), 'utf8'));
const cookie = Object.entries(jar).map(([k, v]) => `${k}=${v}`).join('; ');
const UPSTREAM = 'https://hn.12348.gov.cn';

http.createServer(async (req, res) => {
  try {
    const url = UPSTREAM + req.url;
    const headers = { ...req.headers, cookie, host: 'hn.12348.gov.cn', 'accept-encoding': 'identity' };
    delete headers.connection;
    let body;
    if (!['GET', 'HEAD'].includes(req.method)) {
      const chunks = [];
      for await (const c of req) chunks.push(c);
      body = Buffer.concat(chunks);
    }
    const up = await fetch(url, { method: req.method, headers, body, redirect: 'manual' });
    const buf = Buffer.from(await up.arrayBuffer());
    const out = { ...Object.fromEntries(up.headers.entries()) };
    delete out['content-encoding'];
    delete out['transfer-encoding'];
    delete out['content-length'];
    // 让浏览器只跟本地域
    if (out.location && out.location.startsWith(UPSTREAM)) out.location = out.location.slice(UPSTREAM.length) || '/';
    res.writeHead(up.status, out);
    res.end(buf);
  } catch (e) {
    res.writeHead(502, { 'content-type': 'text/plain; charset=utf-8' });
    res.end('proxy error: ' + e.message);
  }
}).listen(port, '127.0.0.1', () => console.log(`proxy http://127.0.0.1:${port} -> ${UPSTREAM} as ${phone}`));
