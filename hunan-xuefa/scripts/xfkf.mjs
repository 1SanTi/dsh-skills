#!/usr/bin/env node
// 湖南学法网（hn.12348.gov.cn）学法任务自动化
// 用法:
//   node xfkf.mjs captcha <手机号>
//   node xfkf.mjs login   <手机号> <密码> <图形码>
//   node xfkf.mjs status  <手机号>
//   node xfkf.mjs answer  <手机号>          # 取题+按内置答案交卷（自动跳过已答对的）
//   node xfkf.mjs questions <手机号>        # 只导出题目到 all_questions-<手机号>.json
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const BASE = 'https://hn.12348.gov.cn';
const DIR = path.dirname(fileURLToPath(import.meta.url));
const jarPath = (phone) => path.join(DIR, `cookies-${phone}.json`);

function loadJar(phone) { try { return JSON.parse(fs.readFileSync(jarPath(phone), 'utf8')); } catch { return {}; } }
function saveJar(phone, j) { fs.writeFileSync(jarPath(phone), JSON.stringify(j, null, 2)); }
const cookieHeader = (jar) => Object.entries(jar).map(([k, v]) => `${k}=${v}`).join('; ');

async function req(phone, p, opt = {}) {
  const jar = loadJar(phone);
  const url = p.startsWith('http') ? p : BASE + p;
  const headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/126 Mobile Safari/537.36',
    Accept: 'application/json, text/plain, */*',
    Referer: BASE + '/ucenter/',
    Origin: BASE,
    ...(opt.headers || {}),
  };
  const ck = cookieHeader(jar);
  if (ck) headers.Cookie = ck;
  let body;
  if (opt.body !== undefined) {
    if (typeof opt.body === 'string') body = opt.body;
    else { body = JSON.stringify(opt.body); headers['Content-Type'] = 'application/json;charset=utf-8'; }
  }
  const res = await fetch(url, { method: opt.method || 'GET', headers, body, redirect: 'manual' });
  if (res.headers.getSetCookie) for (const c of res.headers.getSetCookie()) {
    const [pair] = c.split(';'); const i = pair.indexOf('=');
    if (i > 0) jar[pair.slice(0, i).trim()] = pair.slice(i + 1).trim();
  }
  saveJar(phone, jar);
  const text = await res.text();
  let json = null; try { json = JSON.parse(text); } catch {}
  return { status: res.status, text, json, headers: Object.fromEntries(res.headers.entries()) };
}

// 答案（2026年度《九五普法导读》（一）（二）16章100题）
const ANS = {
  1: ['D'],
  5: ['A,B','A,B,C','B','A,B','C','B','A','B','A','C','B','A'],
  8: ['A,B,C,D','B','D','B','C','A,B,C','A,B,C','A,B,C,D','A,B','A'],
  12: ['A','A','B','A,B,C,D','A','A,B,C','B','D'],   // 第1题法规原文=反映(A)，答案文档写AB属笔误
  17: ['A,C','B','B','C','B','A','A','A'],
  23: ['A,B,C','A','A,B','A,B','A'],
  30: ['D','A,B,C','A,B,C,D','A,B','A,B,C','A,B,C','A','A,B,C,D'],
  38: ['B,C','B','A,B','A','A','A,C','B','A,B,C'],
  47: ['A','B','A','B','B','A,B','A','C'],
  57: ['A','C','C','A,B,C','A','B','A,B,C','A,B'],
  88: ['A','B','C','A','A','A','B'],
  100: ['A,B,C','A','A,B','B','A,B,C,D'],
  221: ['B','A,B,C,D','A,B,C'],
  235: ['A,B','C','A'],
  250: ['C','A','A,B,C,D'],
  266: ['A','A,B,C','B'],
};

const cmd = process.argv[2];
const phone = process.argv[3];

if (cmd === 'captcha') {
  const r = await req(phone, '/ucenter/api/kaptcha');
  if (!r.json?.success) { console.error('取图形码失败', r.status, r.text.slice(0, 200)); process.exit(1); }
  const b = r.json.body;
  const img = path.join(DIR, `captcha-${phone}.jpg`);
  fs.writeFileSync(img, Buffer.from(b.base64Img.replace(/^data:image\/\w+;base64,/, ''), 'base64'));
  fs.writeFileSync(path.join(DIR, `captcha-${phone}.json`), JSON.stringify({ captchaKey: b.captchaKey }));
  console.log(JSON.stringify({ ok: true, img, captchaKey: b.captchaKey }));
} else if (cmd === 'login') {
  const pwd = process.argv[4];
  const code = process.argv[5];
  const { captchaKey } = JSON.parse(fs.readFileSync(path.join(DIR, `captcha-${phone}.json`), 'utf8'));
  const r = await req(phone, '/ucenter/api/doLogin', {
    method: 'POST',
    body: { redirectUrl: 'http://hn.12348.gov.cn/fxmain/study?biz=fxmain', username: phone, password: Buffer.from(pwd, 'latin1').toString('base64'), code, captchaKey, ifRemember: false },
  });
  console.log(JSON.stringify(r.json ?? r.text.slice(0, 300)));
} else if (cmd === 'status') {
  const r = await req(phone, '/fxmain/legalpublicity/rule');
  const d = r.json;
  if (!d) { console.error('未登录或返回异常', r.status, r.text.slice(0, 200)); process.exit(1); }
  const p = d.examPersonPojo || {};
  console.log(JSON.stringify({
    name: p.name, unit: p.unitName, dep: p.depName,
    score: d.lpPersonScore?.score, pubZs: d.lpPersonScore?.pubZsScore,
    books: (d.lpContentStudy || []).map(x => ({ contentId: x.contentId, score: x.score })),
    examOpen: (d.examInfoPojo || []).length > 0,
  }, null, 1));
} else if (cmd === 'questions') {
  const books = await listBooks(phone);
  const all = {};
  for (const b of books) {
    const chs = JSON.parse((await req(phone, '/fxmain/legalpublicity/querycontentall', { method: 'POST', body: { contentId: b.id } })).text);
    for (const ch of chs) {
      const html = (await req(phone, `/fxmain/onlineanswer/os?caseId=${b.id}&chapId=${ch.id}`)).text || '';
      const spans = [...html.matchAll(/<span[^>]*flag\s*=\s*"(\d+)"[^>]*qid="(\d+)"[^>]*>([\s\S]*?)<\/span>/g)];
      all[`${b.id}_${ch.chapterNo}`] = {
        bookId: b.id, chapterNo: ch.chapterNo, chapterId: ch.id, title: ch.title,
        questions: spans.map(([, flag, qid, text]) => ({ qid, flag, text: text.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim() })),
      };
    }
  }
  fs.writeFileSync(path.join(DIR, `all_questions-${phone}.json`), JSON.stringify(all, null, 1));
  console.log(JSON.stringify({ ok: true, chapters: Object.keys(all).length, questions: Object.values(all).reduce((a, v) => a + v.questions.length, 0) }));
} else if (cmd === 'answer') {
  const books = await listBooks(phone);
  let submitted = 0, wrongLeft = 0;
  for (const b of books) {
    const chs = JSON.parse((await req(phone, '/fxmain/legalpublicity/querycontentall', { method: 'POST', body: { contentId: b.id } })).text);
    for (const ch of chs) {
      const html = (await req(phone, `/fxmain/onlineanswer/os?caseId=${b.id}&chapId=${ch.id}`)).text || '';
      const qs = [...html.matchAll(/<span[^>]*flag\s*=\s*"(\d+)"[^>]*qid="(\d+)"[^>]*>/g)].map(([, flag, qid]) => ({ flag, qid }));
      if (!qs.length) continue;
      const st = (await req(phone, `/fxmain/onlineanswer/queryAnswerRela?objId=${b.id}&chaptId=${ch.id}`)).text;
      let arr = []; try { arr = JSON.parse(st); } catch {}
      const done = new Map(arr.map(x => [x.answerDTO?.id, x.answerDTO?.name]));
      const ans = ANS[Number(ch.chapterNo)];
      if (!ans) { console.error(`无内置答案: 章 ${ch.chapterNo}`); continue; }
      const todo = qs.map((q, i) => ({ ...q, i })).filter(q => done.get(q.qid) !== '回答正确')
        .map(q => ({ questionId: q.qid, contentId: b.id, contentType: '', flag: q.flag, chapterId: ch.id, answerResult: ans[q.i] }));
      if (!todo.length) { console.log(`ch${ch.chapterNo} 已全对`); continue; }
      const cap = (await req(phone, '/fxmain/onlineanswer/forbidAnswer')).text;
      if (!String(cap).includes('true')) { console.log(`⛔ 今日学分已超额，停止（ch${ch.chapterNo}）`); break; }
      const r = await req(phone, '/fxmain/onlineanswer/ex', { method: 'POST', body: todo, headers: { Referer: `${BASE}/fxmain/subpage/legalpublicity/fx_regulations.html?objId=${b.id}` } });
      const res = r.json?.extend?.result || {};
      const bad = todo.filter(t => res[t.questionId] !== '1');
      submitted += todo.length; wrongLeft += bad.length;
      console.log(`ch${ch.chapterNo} 提交${todo.length} 仍错${bad.length}`);
    }
  }
  const s = (await req(phone, '/fxmain/legalpublicity/rule')).json;
  console.log(JSON.stringify({ submitted, wrongLeft, score: s?.lpPersonScore?.score, pubZs: s?.lpPersonScore?.pubZsScore, examOpen: (s?.examInfoPojo || []).length > 0 }));
} else {
  console.log('用法见文件头部注释');
}

async function listBooks(phone) {
  const r = await req(phone, '/fxmain/legalpublicity/queryPubBook', {
    method: 'POST', body: { condition: { contentType1: 2, state: 3, businessCode: '4' } },
  });
  return JSON.parse(r.text);
}
