#!/usr/bin/env node
/**
 * skill-recorder — record what happens on an Android screen and turn it into a
 * reusable loop plan / skill.
 *
 * It does NOT capture raw touch events (Android does not expose them to the app
 * without a system-level service). Instead it samples the DSH screen dump
 * (`scr dump`) while the user demonstrates a task, keeps every meaningful screen
 * transition, and compiles those transitions into a `loop run` plan draft that a
 * human/agent can review and replay.
 *
 * Commands:
 *   check                       verify screen control works (self-heals when possible)
 *   repair                      force re-register the accessibility service (Shizuku)
 *   start --name "任务" [--interval 1200] [--max 900]
 *   stop                        stop the running recording
 *   status                      print current recording state
 *   list                        list recorded sessions
 *   compile [--name] [--session <id>] [--max-steps 20]
 *   replay --plan <path> [--dry]
 *   save --name <skill> --plan <path> [--title "..."]
 */

import { execFile, execFileSync } from 'node:child_process';
import { promisify } from 'node:util';
import fs from 'node:fs';
import path from 'node:path';

const pexec = promisify(execFile);

const SKILL_DIR = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const SESS_DIR = path.join(SKILL_DIR, 'sessions');
const PLAN_DIR = path.join(SKILL_DIR, 'plans');
const ACTIVE = path.join(SESS_DIR, '.active.json');
const HOME = process.env.DSH_HOME || path.resolve(SKILL_DIR, '../..');
const SKILLS_HOME = path.join(HOME, 'skills');

const GENERIC = new Set(['返回', '确定', '取消', '完成', '更多', '关闭', '设置', 'Back', 'OK', 'Cancel', 'Done', 'More', 'Close', 'Settings']);
const PUNCT_ONLY = /^[\p{P}\p{S}\s]+$/u;
function isUsefulText(t) {
  const s = String(t || '').replace(/^d:/, '').trim();
  return s.length >= 2 && !PUNCT_ONLY.test(s);
}

/* ------------------------------ helpers ------------------------------ */

function ensureDirs() {
  for (const d of [SESS_DIR, PLAN_DIR]) fs.mkdirSync(d, { recursive: true });
}

function slugify(s) {
  return String(s || 'session')
    .trim()
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 40) || 'session';
}

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next === undefined || next.startsWith('--')) out[key] = true;
      else {
        out[key] = next;
        i++;
      }
    } else out._.push(a);
  }
  return out;
}

async function run(cmd, args, timeout = 10000) {
  try {
    const { stdout } = await pexec(cmd, args, { timeout, maxBuffer: 8 * 1024 * 1024 });
    return { ok: true, out: stdout };
  } catch (e) {
    return { ok: false, out: String(e.stdout || ''), err: String(e.stderr || e.message) };
  }
}

/* ------------------------------ screens ------------------------------ */

/** Parse `scr dump` text into nodes: {id, text, x, y, clickable, role}. */
function parseDump(raw) {
  const nodes = [];
  for (const line of String(raw || '').split('\n')) {
    const m = line.match(/^\s*(o?\d+)\s+(.*?)\s+@(\d+),(\d+)(.*)$/);
    if (!m) continue;
    const [, id, text, x, y, tail] = m;
    const role = (tail.match(/\[([a-z]+)\]/) || [])[1] || '';
    nodes.push({
      id,
      text: text.trim(),
      x: Number(x),
      y: Number(y),
      clickable: /\bc\b/.test(tail) || role === 'button' || role === 'row' || role === 'switch',
      checked: /(^|\s)v(\s|$)/.test(tail.replace(/@\d+,\d+/, '')),
      role,
    });
  }
  return nodes.filter((n) => n.text);
}

const A11Y_SERVICE = 'app.dsh.mobile/.DshAccessibilityService';
const A11Y_ERROR = /accessibility service not enabled/i;
let lastRepairAt = 0;
let repairInFlight = null;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/**
 * Android sometimes drops the accessibility binding (the service lands in
 * `Crashed services` and `accessibility_enabled` flips back to 0), which is
 * exactly what makes the record button say "screen control is unavailable".
 * Rewriting the two secure settings through the Shizuku shell bridge forces
 * AccessibilityManagerService to unbind and bind the service again, and it
 * takes effect immediately without restarting the app.
 */
function repairScreenControl(force = false) {
  if (repairInFlight) return repairInFlight;
  if (!force && Date.now() - lastRepairAt < 15000) return Promise.resolve(false);
  lastRepairAt = Date.now();
  repairInFlight = (async () => {
    // the bridge is the only path that can write secure settings (shell uid)
    const probe = await run('shz', ['settings', 'get', 'secure', 'accessibility_enabled'], 8000);
    if (!probe.ok) return false;
    await run('shz', ['settings', 'delete', 'secure', 'enabled_accessibility_services'], 8000);
    await sleep(300);
    await run('shz', ['settings', 'put', 'secure', 'enabled_accessibility_services', A11Y_SERVICE], 8000);
    await sleep(300);
    await run('shz', ['settings', 'put', 'secure', 'accessibility_enabled', '1'], 8000);
    await sleep(1200);
    const check = await run('scr', ['dump'], 8000);
    return check.ok && !A11Y_ERROR.test(check.out || '');
  })().finally(() => {
    repairInFlight = null;
  });
  return repairInFlight;
}

function screenControlError() {
  return new Error(
    'screen control is unavailable: enable "DSH Screen Control" accessibility service (设置 → 无障碍 → DSH Screen Control), then retry.'
  );
}

async function capture(retry = true) {
  let r = await run('scr', ['dump'], 8000);
  let out = r.out || '';
  if (!r.ok || A11Y_ERROR.test(out)) {
    // self-heal once, then re-check before giving up
    if (retry && (await repairScreenControl())) {
      r = await run('scr', ['dump'], 8000);
      out = r.out || '';
    }
    if (!r.ok || A11Y_ERROR.test(out)) throw screenControlError();
  }
  return parseDump(out);
}

async function foregroundPkg() {
  const r = await run('scr', ['pkg'], 4000);
  if (!r.ok) return null;
  const m = String(r.out).match(/[a-z][\w.]+\.[\w.]+/i);
  return m ? m[0] : null;
}

function signature(nodes) {
  return [...new Set(nodes.map((n) => n.text))].sort().join('\u241f');
}

function jaccardDiff(a, b) {
  const A = new Set(a);
  const B = new Set(b);
  let inter = 0;
  for (const x of A) if (B.has(x)) inter++;
  const union = A.size + B.size - inter;
  return union === 0 ? 0 : 1 - inter / union;
}

/* ------------------------------ commands ------------------------------ */

async function cmdCheck() {
  try {
    const nodes = await capture();
    const pkg = await foregroundPkg();
    console.log(JSON.stringify({ ok: true, nodes: nodes.length, pkg }, null, 2));
    return 0;
  } catch (e) {
    console.log(JSON.stringify({ ok: false, error: e.message }, null, 2));
    return 2;
  }
}

async function cmdRepair() {
  const ok = await repairScreenControl(true);
  console.log(JSON.stringify({ ok, repaired: ok }, null, 2));
  return ok ? 0 : 2;
}

/* 系统/桌面/浏览器壳这类屏幕不承载用户任务，编译与实时分析都跳过 */
const NOISE_PKG =
  /^(com\.zui\.launcher|com\.android\.systemui|com\.zui\.resolver|com\.android\.permissioncontroller|com\.zui\.ai\.stylus|com\.android\.settings|com\.lenovo\.launcher|com\.android\.packageinstaller)/;
const NOISE_NAMES = new Set(['主屏幕', '新标签页', '全部清除', '关于手机', '已锁定']);
const LAUNCHER_HINTS = ['时钟', '便签', '欧路词典', '主屏幕', '天气', '应用商店', '计算器', '安全中心', '文件管理'];
const CHROME_TEXT =
  /^(https?:\/\/|帮助中心|收藏本站点|手机访问|首页 首页|工作室动态|课程资源|专题资源|观课议课|更多\.\.\.|\d+条\/页$|前往|\d+\s*页$|ARbg-|000\d$|sb\d|s\d+s\d+|r\d+x\d+)/;
function isNoiseEvent(ev) {
  if (!ev) return true;
  if (NOISE_PKG.test(String(ev.pkg || ''))) return true;
  const useful = [...new Set((ev.texts || []).filter(isUsefulText))];
  if (useful.length < 3) return true;
  const launcherish = useful.filter((t) => LAUNCHER_HINTS.some((h) => t.includes(h))).length;
  if (launcherish >= 3) return true;
  return useful.every((t) => NOISE_NAMES.has(t) || /已锁定$/.test(t));
}
function isChrome(t) {
  return CHROME_TEXT.test(String(t || '').trim());
}
function stripText(x) {
  return String(x || '').replace(/^d:/, '').trim();
}
function signatureTexts(ev) {
  return [...new Set((ev.texts || []).filter(isUsefulText))].sort().join('\u241f');
}

/**
 * 录制过程中同步做一遍轻量分析：每录到一个新画面，就把「点了什么 → 出现什么」
 * 记进 analysis-live.json。纯本地、不需要语音；停止录制后再由 compile 出正式回放稿。
 */
function writeLiveAnalysis(dir, prev, ev) {
  try {
    const file = path.join(dir, 'analysis-live.json');
    let data = { steps: [], events: 0, updatedAt: null };
    try {
      data = JSON.parse(fs.readFileSync(file, 'utf8'));
    } catch {}
    data.events = (data.events || 0) + 1;
    if (prev && !isNoiseEvent(prev) && !isNoiseEvent(ev)) {
      const prevTexts = new Set((prev.texts || []).map(stripText));
      const gone = (prev.nodes || [])
        .filter((n) => n.c)
        .map((n) => stripText(n.t))
        .filter((t) => isUsefulText(t) && !prevTexts.has(t) && !GENERIC.has(t))
        .slice(0, 3);
      const appeared = (ev.texts || [])
        .map(stripText)
        .filter((t) => isUsefulText(t) && !prevTexts.has(t) && !GENERIC.has(t))
        .slice(0, 4);
      if (gone.length || appeared.length) {
        data.steps.push({
          t: ev.iso,
          pkg: ev.pkg || null,
          tap: gone[0] || null,
          appeared,
          fromTexts: (prev.texts || []).slice(0, 3),
          toTexts: (ev.texts || []).slice(0, 3),
        });
        data.steps = data.steps.slice(-60);
      }
    }
    data.updatedAt = new Date().toISOString();
    fs.writeFileSync(file, JSON.stringify(data, null, 1));
    return data.steps.length;
  } catch {
    return 0;
  }
}

/* 状态栏时钟/电量这类每帧都抖的文本，不能算“画面变化” */
const TICK_NOISE = /^(\d{1,2}:\d{2}(:\d{2})?|\d{1,3}%|星期[一二三四五六日天]|\d{1,2}月\d{1,2}日)$/;
const denoise = (arr) => arr.filter((t) => !TICK_NOISE.test(String(t || '').trim()));

async function cmdStart(opts) {
  ensureDirs();
  const name = String(opts.name || '未命名任务');
  // 采样间隔：默认 400ms（原为 1200ms；太快会把两次操作并成一跳）
  const interval = Math.max(250, Number(opts.interval || 400));
  // 相邻两帧的判定阈值（比“相对上一张已存画面”的阈值松，抓得更细）
  const tickDiff = Math.min(0.9, Math.max(0.01, Number(opts['tick-diff'] || 0.04)));
  const minDiff = Math.min(0.9, Math.max(0.05, Number(opts['min-diff'] || 0.12)));
  // 变化之后的“连拍”窗口：抓 toast、新标签页、加载态这类一闪而过的画面
  const burstMs = Math.max(120, Number(opts['burst-ms'] || 200));
  const burstWindow = Math.max(0, Number(opts['burst-window'] || 900));
  const keepFrames = String(opts.frames || 'on') !== 'off';
  const maxTicks = Number(opts.max || 900);
  const id = `${slugify(name)}-${Date.now().toString(36)}`;
  const dir = path.join(SESS_DIR, id);
  fs.mkdirSync(dir, { recursive: true });

  if (fs.existsSync(ACTIVE)) {
    console.error('a recording is already running; run `stop` first');
    return 2;
  }

  // fail fast when accessibility is off
  try {
    await capture();
  } catch (e) {
    console.error(e.message);
    return 2;
  }

  const meta = { id, name, dir, interval, tickDiff, burstMs, burstWindow, startedAt: new Date().toISOString() };
  fs.writeFileSync(path.join(dir, 'meta.json'), JSON.stringify(meta, null, 2));
  fs.writeFileSync(ACTIVE, JSON.stringify({ ...meta, pid: process.pid }, null, 2));

  // 录音默认关闭：它必须借一个浏览器页当麦克风载体，切到别的 App 时浏览器后台容易被杀，
  // 反而拖垮录制。需要时显式加 --audio（页面会自己开，录完才有旁白）。
  // 默认只做屏幕采样：纯无障碍读取，不占麦克风、不依赖任何后台页面。
  let audio = null;
  let skipAudioPageUntil = 0;
  if (opts.audio) {
    try {
      const { startAudioCapture } = await import('./audio-capture.mjs');
      audio = await startAudioCapture(dir, (m) => process.stderr.write(m + '\n'));
      try {
        execFileSync('shz', ['am', 'start', '-a', 'android.intent.action.VIEW', '-d', audio.url], { timeout: 8000 });
      } catch {}
      await new Promise((r) => setTimeout(r, 1800));
      skipAudioPageUntil = Date.now() + 3500;
    } catch (e) {
      process.stderr.write('audio capture unavailable: ' + (e && e.message) + '\n');
      audio = null;
    }
  }

  let stopped = false;
  const stop = (sig) => {
    stopped = true;
    try {
      process.stderr.write('signal ' + sig + '\n');
    } catch {}
  };
  process.on('SIGINT', () => stop('SIGINT'));
  process.on('SIGTERM', () => stop('SIGTERM'));
  process.on('SIGHUP', () => stop('SIGHUP'));

  const eventsPath = path.join(dir, 'events.jsonl');
  const framesPath = path.join(dir, 'frames.jsonl');
  if (keepFrames) fs.writeFileSync(framesPath, '');
  let prevSig = null;
  let prevTexts = [];
  let prevPkg = null;
  let prevEvent = null;
  let prevTickTexts = null; // 上一「采样帧」的文本集合，用来做逐帧差分
  let burstUntil = 0;       // 连拍窗口的结束时间
  let frames = 0;
  let ticks = 0;
  let pkg = null;
  // 默认忽略 DSH 自己的界面：聊天流式输出会把录制搞成一堆噪声步骤。
  // 想录 DSH 本身传 --ignore-pkg none。
  const ignoreArg = opts['ignore-pkg'] === undefined ? 'app.dsh.mobile' : String(opts['ignore-pkg']);
  const ignorePkg = /^(none|off|no|-)$/i.test(ignoreArg) ? null : ignoreArg;
  if (ignorePkg) pkg = await foregroundPkg().catch(() => null);

  process.stderr.write(`recording "${name}" -> ${dir} (interval ${interval}ms)\n`);

  while (!stopped && ticks < maxTicks) {
    ticks++;
    const tickStart = Date.now();
    if (ticks % 6 === 1) pkg = await foregroundPkg().catch(() => pkg);
    let nodes;
    try {
      nodes = await capture();
    } catch (e) {
      process.stderr.write(`capture failed: ${e.message}\n`);
      break;
    }
    const texts = denoise([...new Set(nodes.map((n) => n.text).filter(isUsefulText))]);
    if (!texts.length) {
      await new Promise((r) => setTimeout(r, interval));
      continue;
    }
    const sig = signature(nodes);
    const diff = prevSig === null ? 1 : jaccardDiff(prevTexts, texts);
    // 逐帧差分：和“上一次采样”比，这样只变了几个字的中间态（toast、加载完成）也能被抓到
    const tickDelta = prevTickTexts ? jaccardDiff(prevTickTexts, texts) : 1;
    const pkgChanged = pkg && prevPkg && pkg !== prevPkg;
    if (skipAudioPageUntil && Date.now() < skipAudioPageUntil) {
      // 录音页刚打开的那几秒不算用户操作，避免把浏览器录音页录进回放稿
      prevSig = sig;
      prevTexts = texts;
      prevPkg = pkg;
      prevTickTexts = texts;
      await new Promise((r) => setTimeout(r, interval));
      continue;
    }
    const onIgnoredPkg = ignorePkg && pkg === ignorePkg;
    const changed =
      !onIgnoredPkg && sig !== prevSig && (prevSig === null || tickDelta > tickDiff || diff > minDiff || pkgChanged);
    if (keepFrames) {
      // 每一帧都留档（含未触发步骤的中间态），compile 时用它们还原更细的过程
      const frame = {
        t: Date.now(),
        iso: new Date().toISOString(),
        pkg,
        chg: !!changed,
        texts,
        nodes: nodes.map((n) => ({ t: n.text, x: n.x, y: n.y, c: n.clickable, r: n.role })),
      };
      fs.appendFileSync(framesPath, JSON.stringify(frame) + '\n');
      frames++;
    }
    if (onIgnoredPkg) {
      prevSig = sig;
      prevTexts = texts;
      prevPkg = pkg;
      prevTickTexts = texts;
      await new Promise((r) => setTimeout(r, interval));
      continue;
    }
    if (changed) {
      if (ignorePkg) pkg = (await foregroundPkg().catch(() => pkg)) || pkg;
      const ev = {
        t: Date.now(),
        iso: new Date().toISOString(),
        pkg,
        texts,
        nodes: nodes.map((n) => ({ t: n.text, x: n.x, y: n.y, c: n.clickable, r: n.role })),
      };
      fs.appendFileSync(eventsPath, JSON.stringify(ev) + '\n');
      const liveSteps = writeLiveAnalysis(dir, prevEvent, ev);
      prevEvent = ev;
      prevSig = sig;
      prevTexts = texts;
      prevPkg = pkg;
      burstUntil = Date.now() + burstWindow; // 这一跳之后赶紧连拍，别漏掉过渡画面
      process.stderr.write(`  [${new Date().toISOString().slice(11, 19)}] ${texts.length} texts${pkg ? ' @ ' + pkg : ''} | live steps ${liveSteps}\n`);
    }
    prevTickTexts = texts;
    const target = Date.now() < burstUntil ? Math.min(interval, burstMs) : interval;
    // 采一帧本身要 150–300ms，这里把耗时扣掉，让实际节奏接近设定的 interval
    const delay = Math.max(0, target - (Date.now() - tickStart));
    await new Promise((r) => setTimeout(r, delay));
  }

  let audioSummary = null;
  if (audio) {
    try {
      audioSummary = await audio.stopAndSave();
      const meta2 = JSON.parse(fs.readFileSync(path.join(dir, 'meta.json'), 'utf8'));
      meta2.audio = audioSummary.audio || null;
      meta2.transcript = fs.existsSync(path.join(dir, 'transcript.json')) ? path.join(dir, 'transcript.json') : null;
      fs.writeFileSync(path.join(dir, 'meta.json'), JSON.stringify(meta2, null, 2));
      process.stderr.write(
        `audio saved: ${audioSummary.audio || 'none'} (${audioSummary.bytes || 0} bytes), transcript lines: ${audioSummary.lines || 0}\n`
      );
    } catch (e) {
      process.stderr.write('audio finalize failed: ' + (e && e.message) + '\n');
    }
  }

  const endedAt = new Date().toISOString();
  fs.writeFileSync(path.join(dir, 'meta.json'), JSON.stringify({ ...meta, endedAt, audio: audioSummary ? audioSummary.audio : null }, null, 2));
  try {
    const current = JSON.parse(fs.readFileSync(ACTIVE, 'utf8'));
    if (current && current.id === id) fs.unlinkSync(ACTIVE);
  } catch {}
  let count = 0;
  try {
    count = fs.readFileSync(eventsPath, 'utf8').split('\n').filter(Boolean).length;
  } catch {}
  process.stderr.write(`stopped; ${count} events, ${frames} frames\n`);
  return 0;
}

function readActive() {
  try {
    return JSON.parse(fs.readFileSync(ACTIVE, 'utf8'));
  } catch {
    return null;
  }
}

async function cmdStop() {
  const a = readActive();
  if (!a) {
    console.log(JSON.stringify({ ok: false, error: 'no recording is running' }));
    return 1;
  }
  try {
    process.kill(a.pid, 'SIGTERM');
  } catch (e) {
    /* already gone */
  }
  // 等录制进程收尾（它要把录音和转写落盘），最多 9 秒
  const deadline = Date.now() + 9000;
  while (Date.now() < deadline) {
    try {
      process.kill(a.pid, 0);
    } catch {
      break;
    }
    await new Promise((r) => setTimeout(r, 200));
  }
  try {
    fs.unlinkSync(ACTIVE);
  } catch {}
  // 实时转写没出字时，才回退到停止后整段跑一次本地 Whisper
  try {
    const sessDir = a.dir || path.join(SESS_DIR, a.id);
    const audio = path.join(sessDir, "narration.webm");
    let needFallback = true;
    try {
      const t = JSON.parse(fs.readFileSync(path.join(sessDir, "transcript.json"), "utf8"));
      needFallback = !Array.isArray(t) || !t.filter((x) => x && String(x.text || "").trim()).length;
    } catch {
      needFallback = true;
    }
    if (fs.existsSync(audio) && needFallback) {
      const { spawn } = await import("node:child_process");
      const child = spawn(process.execPath, [path.join(SKILL_DIR, "scripts", "asr-local.mjs"), audio, sessDir], {
        detached: true,
        stdio: "ignore",
        env: process.env,
      });
      child.unref();
    }
  } catch {}
  console.log(JSON.stringify({ ok: true, stopped: a.id }, null, 2));
  return 0;
}

function cmdStatus() {
  const a = readActive();
  console.log(JSON.stringify(a ? { ok: true, recording: a } : { ok: false, recording: null }, null, 2));
  return 0;
}

function listSessions() {
  ensureDirs();
  return fs
    .readdirSync(SESS_DIR)
    .filter((d) => !d.startsWith('.'))
    .map((d) => {
      const dir = path.join(SESS_DIR, d);
      let meta = {};
      try {
        meta = JSON.parse(fs.readFileSync(path.join(dir, 'meta.json'), 'utf8'));
      } catch {}
      let events = 0;
      try {
        events = fs.readFileSync(path.join(dir, 'events.jsonl'), 'utf8').split('\n').filter(Boolean).length;
      } catch {}
      return { id: d, name: meta.name || d, startedAt: meta.startedAt, events };
    })
    .sort((a, b) => String(b.startedAt).localeCompare(String(a.startedAt)));
}

function cmdList() {
  console.log(JSON.stringify(listSessions(), null, 2));
  return 0;
}

function pickSession(name) {
  const all = listSessions();
  if (!all.length) throw new Error('no recorded sessions yet');
  if (!name) return all[0];
  const hit = all.find((s) => s.id === name) || all.find((s) => s.name === name) || all.find((s) => s.id.startsWith(name));
  if (!hit) throw new Error(`session not found: ${name}`);
  return hit;
}

function loadEvents(dir) {
  try {
    return fs
      .readFileSync(path.join(dir, 'events.jsonl'), 'utf8')
      .split('\n')
      .filter(Boolean)
      .map((l) => JSON.parse(l));
  } catch {
    return [];
  }
}

function loadFrames(dir) {
  // 优先用逐帧档（frames.jsonl）：400ms 一帧，能还原中间态；
  // 老会话没有这个文件，退回 events.jsonl
  for (const name of ['frames.jsonl', 'events.jsonl']) {
    const f = path.join(dir, name);
    try {
      const rows = fs
        .readFileSync(f, 'utf8')
        .split('\n')
        .filter(Boolean)
        .map((l) => {
          try {
            return JSON.parse(l);
          } catch {
            return null;
          }
        })
        .filter(Boolean);
      if (rows.length) return rows;
    } catch {}
  }
  return [];
}

/* 点击候选打分：短标签、按钮/行/开关角色优先；导航/通用词降权 */
function scoreCandidate(n) {
  const t = String(n.t || '');
  let s = 0;
  if (n.c) s += 2;
  if (/button|row|switch/.test(n.r || '')) s += 2;
  if (t.length > 0 && t.length <= 8) s += 1;
  if (isChrome(t)) s -= 3;
  if (GENERIC.has(t)) s -= 3;
  if (/^\d+$/.test(t)) s -= 2;
  return s;
}

function cmdCompile(opts) {
  const s = pickSession(opts.session || opts.name);
  const dir = path.join(SESS_DIR, s.id);
  const allEvents = loadFrames(dir);
  if (!allEvents.length) throw new Error(`session ${s.id} has no events`);

  // 先把桌面、系统弹窗、打开方式这类无关屏幕去掉
  const events = allEvents.filter((ev) => !isNoiseEvent(ev));
  if (events.length < 2) throw new Error(`session ${s.id} only has launcher/system screens, nothing to replay`);

  const maxSteps = Number(opts['max-steps'] || 20);

  const norm = (t) => String(t || '').replace(/^d:/, '').trim();
  const cleanArr = (arr) => [...new Set((arr || []).map(norm).filter(isUsefulText).filter((t) => !isChrome(t)))];

  // 相邻同签名帧折叠，只留真正变了画面的那些
  const seq = [];
  for (const ev of events) {
    const k = signatureTexts(ev);
    if (!seq.length || signatureTexts(seq[seq.length - 1]) !== k) seq.push(ev);
  }

  const transitions = [];
  for (let i = 0; i < seq.length - 1 && transitions.length < maxSteps; i++) {
    const a = seq[i];
    const b = seq[i + 1];
    if (a.pkg === b.pkg && signatureTexts(a) === signatureTexts(b)) continue;
    const aTexts = new Set(cleanArr(a.texts));
    const bTexts = new Set(cleanArr(b.texts));
    if (!bTexts.size) continue;

    const disappeared = (a.nodes || [])
      .map((n) => ({ ...n, t: norm(n.t) }))
      .filter((n) => n.c && !bTexts.has(n.t) && isUsefulText(n.t) && !GENERIC.has(n.t) && !isChrome(n.t))
      .sort((x, y) => scoreCandidate(y) - scoreCandidate(x));

    const appeared = [...bTexts].filter((t) => !aTexts.has(t) && !GENERIC.has(t));
    const gone = [...aTexts].filter((t) => !bTexts.has(t) && !GENERIC.has(t));
    if (!disappeared.length && !appeared.length && !gone.length) continue;

    transitions.push({
      from: a,
      to: b,
      candidates: disappeared.map((n) => n.t).slice(0, 5),
      appeared: appeared.slice(0, 5),
      gone: gone.slice(0, 5),
      target: disappeared.length ? disappeared[0].t : null,
      confident: disappeared.length >= 1 && disappeared.length <= 2 && appeared.length > 0,
      dt: (b.t || 0) - (a.t || 0),
    });
  }

  // 二次整形：没有点击候选的跳转（加载完成/toast/自动刷新）并进上一步的证据；
  // 连续点同一个目标（比如点了三次「下载」）合并成一步，标 repeat
  const steps = [];
  for (const tr of transitions) {
    const last = steps[steps.length - 1];
    if (!tr.target) {
      if (last) {
        last.extraAppeared = [...new Set([...(last.extraAppeared || []), ...tr.appeared])].slice(0, 6);
        last.extraGone = [...new Set([...(last.extraGone || []), ...tr.gone])].slice(0, 6);
      } else {
        steps.push({ ...tr, noTarget: true });
      }
      continue;
    }
    if (last && !last.noTarget && last.target === tr.target) {
      last.repeat = (last.repeat || 1) + 1;
      last.appeared = [...new Set([...last.appeared, ...tr.appeared])].slice(0, 6);
      continue;
    }
    steps.push({ ...tr });
  }

  const story = [];
  story.push(`# 录制回放稿：${s.name}`, '');
  story.push(`- 会话：\`${s.id}\``, `- 时间：${s.startedAt || ''} → ${seq[seq.length - 1]?.iso || ''}`);
  story.push(`- 画面变化：${seq.length} 屏（逐帧 ${allEvents.length} 帧），可回放步骤草案：${steps.length}`, '');
  steps.forEach((tr, i) => {
    story.push(`## 步骤 ${i + 1}${tr.confident ? '' : '（需人工确认目标）'}`);
    story.push('', `**当前屏文本**（前三项）: ${cleanArr(tr.from.texts).slice(0, 8).join(' / ')}`);
    if (tr.candidates.length) story.push(`**点击候选**（本屏消失的可点击项）: ${tr.candidates.join(' / ')}`);
    if (tr.repeat) story.push(`**重复动作**: 同一目标连续点了 ${tr.repeat} 次`);
    story.push(`**下一屏新增**: ${tr.appeared.join(' / ') || '(无新文本，用 frameChanged 验证)'}`);
    if (tr.extraAppeared && tr.extraAppeared.length) story.push(`**随后出现（过渡态/toast）**: ${tr.extraAppeared.join(' / ')}`);
    if (tr.extraGone && tr.extraGone.length) story.push(`**随后消失**: ${tr.extraGone.join(' / ')}`);
    if (tr.dt) story.push(`**这一步耗时**: ${(tr.dt / 1000).toFixed(1)}s`);
    if (tr.from.pkg) story.push(`**应用**: ${tr.from.pkg}`);
    story.push('');
  });

  const plan = {
    goal: s.name,
    source: { session: s.id, screens: seq.length, frames: allEvents.length },
    steps: steps.map((tr, i) => {
      const fallback = tr.target || tr.candidates[0] || null;
      const step = {
        id: `s${i + 1}`,
        desc: fallback ? `点击「${fallback}」${tr.repeat ? ` ×${tr.repeat}` : ''}` : '（录到的是返回/自动跳转，请手工补一步）',
        target: fallback ? { text: [fallback] } : null,
        action: { type: fallback ? 'tap' : 'noop' },
        verify: tr.appeared.length ? { anyText: [tr.appeared[0]] } : { frameChanged: true },
        onFail: { retry: 1, then: 'escalate' },
      };
      if (tr.repeat) step.repeat = tr.repeat;
      if (!tr.confident || !step.target) step.needsReview = true;
      return step;
    }),
  };

  // 旁白：把录音转写按时间戳并进回放稿，并把每一句挂到时间上最接近的步骤
  let narration = [];
  try {
    narration = JSON.parse(fs.readFileSync(path.join(dir, 'transcript.json'), 'utf8'));
  } catch {}
  if (narration.length) {
    let base = 0;
    try {
      base = new Date(JSON.parse(fs.readFileSync(path.join(dir, 'meta.json'), 'utf8')).startedAt).getTime() || 0;
    } catch {}
    story.push('## 旁白（录音转写）', '');
    for (const line of narration) {
      const t = Number(line.t) || 0;
      const rel = Math.max(0, t - base);
      const mm = Math.floor(rel / 60000);
      const ss = Math.floor(rel / 1000) % 60;
      const mark = `${String(mm).padStart(2, '0')}:${String(ss).padStart(2, '0')}`;
      story.push(`- [${mark}] ${line.text}`);
    }
    story.push('');
  }

  fs.writeFileSync(path.join(dir, 'storyboard.md'), story.join('\n'));
  const planPath = path.join(dir, 'plan-draft.json');
  fs.writeFileSync(planPath, JSON.stringify(plan, null, 2));

  console.log(
    JSON.stringify(
      {
        ok: true,
        session: s.id,
        storyboard: path.join(dir, 'storyboard.md'),
        plan: planPath,
        steps: plan.steps.length,
        needsReview: plan.steps.filter((x) => x.needsReview).length,
      },
      null,
      2
    )
  );
  return 0;
}

async function cmdReplay(opts) {
  const src = opts.plan;
  if (!src) throw new Error('--plan <path> is required');
  const plan = JSON.parse(fs.readFileSync(path.resolve(src), 'utf8'));
  const payload = JSON.stringify({ goal: plan.goal, steps: plan.steps });
  if (opts.dry) {
    console.log(payload);
    return 0;
  }
  const child = spawn('loop', ['run', '-'], { stdio: ['pipe', 'inherit', 'inherit'] });
  child.stdin.end(payload);
  return await new Promise((res) => child.on('exit', (code) => res(code ?? 0)));
}

function cmdSave(opts) {
  const name = String(opts.name || '');
  if (!name) throw new Error('--name <skill-name> is required');
  const planSrc = opts.plan;
  if (!planSrc) throw new Error('--plan <path> is required');
  const plan = JSON.parse(fs.readFileSync(path.resolve(planSrc), 'utf8'));
  const dir = path.join(SKILLS_HOME, name);
  fs.mkdirSync(dir, { recursive: true });
  const title = String(opts.title || plan.goal || name);
  const md = `---
name: ${name}
description: ${title}。由 skill-recorder 录制并审核后生成的可回放流程技能。
metadata:
  generatedBy: skill-recorder
  version: 1.0.0
---

# ${title}

这是从一次真实手机操作录制中编译出的流程技能。回放前先确认当前设备状态符合前提。

## 前提

- 屏幕控制（无障碍）已开启。
- 目标应用已安装且处于可进入的状态。

## 回放

\`\`\`sh
node ${path.join(SKILL_DIR, 'scripts', 'recorder.mjs')} replay --plan ${path.join(SKILL_DIR, 'plans', name + '.json')}
\`\`\`

## 步骤（loop plan）

\`\`\`json
${JSON.stringify(plan, null, 2)}
\`\`\`

## 修订指南

- \`needsReview: true\` 的步骤必须人工确认锚点文字后再回放。
- 回放失败时先 \`scr dump\` 看真实界面，再改 \`target.text\`。
`;
  fs.writeFileSync(path.join(dir, 'SKILL.md'), md);
  fs.copyFileSync(path.resolve(planSrc), path.join(PLAN_DIR, name + '.json'));
  console.log(JSON.stringify({ ok: true, skill: dir }, null, 2));
  return 0;
}

/* ------------------------------ main ------------------------------ */

import { spawn } from 'node:child_process';

const argv = process.argv.slice(2);
const cmd = argv[0];
const opts = parseArgs(argv.slice(1));

const USAGE = `skill-recorder commands:
  check
  repair
  start --name "任务描述" [--interval 1200]
  stop | status | list | live
  compile [--session <id>] [--max-steps 20]
  replay --plan <path> [--dry]
  save --name <skill> --plan <path> [--title "..."]`;

try {
  let code = 0;
  switch (cmd) {
    case 'check':
      code = await cmdCheck();
      break;
    case 'repair':
      code = await cmdRepair();
      break;
    case 'start':
      code = await cmdStart(opts);
      break;
    case 'stop':
      code = await cmdStop();
      break;
    case 'status':
      code = cmdStatus();
      break;
    case 'list':
      code = cmdList();
      break;
    case 'live': {
      const s = pickSession(opts.session || opts.name);
      try {
        const data = JSON.parse(fs.readFileSync(path.join(SESS_DIR, s.id, 'analysis-live.json'), 'utf8'));
        console.log(JSON.stringify({ ok: true, session: s.id, steps: data.steps.length, updatedAt: data.updatedAt, last: data.steps.slice(-5) }, null, 2));
      } catch {
        console.log(JSON.stringify({ ok: false, session: s.id, error: 'no live analysis yet' }, null, 2));
        code = 1;
      }
      break;
    }
    case 'compile':
      code = cmdCompile(opts);
      break;
    case 'replay':
      code = await cmdReplay(opts);
      break;
    case 'save':
      code = cmdSave(opts);
      break;
    default:
      console.log(USAGE);
      code = cmd ? 1 : 0;
  }
  process.exit(code);
} catch (e) {
  console.error(`error: ${e.message}`);
  process.exit(1);
}
