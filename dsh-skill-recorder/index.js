/**
 * Host half of the Skill Recorder button.
 *
 * The browser half (./client.js) renders a small record button next to the chat
 * composer and talks to this module through one same-origin POST route:
 *
 *   POST api/skill-recorder  { endpoint, payload }
 *
 * It only drives the existing recorder CLI at skills/skill-recorder/scripts/recorder.mjs,
 * so the recorded data format stays identical to the CLI workflow.
 */
import { spawn } from 'node:child_process';
import { existsSync, readdirSync, readFileSync, rmSync, statSync } from 'node:fs';
import path from 'node:path';
import http from 'node:http';

export const name = 'dsh-skill-recorder';
export const inject = ['connection'];

const ROUTE = '/api/skill-recorder';
const DSH_HOME = process.env.DSH_HOME || path.join(process.env.HOME || '.', 'dsh-home');
const SKILL_DIR = path.join(DSH_HOME, 'skills', 'skill-recorder');
const SCRIPT = path.join(SKILL_DIR, 'scripts', 'recorder.mjs');
const SESS_DIR = path.join(SKILL_DIR, 'sessions');
const PLAN_DIR = path.join(SKILL_DIR, 'plans');

/** in-memory pointer to the detached recording child (survives until restart) */
let recording = null;
/** last action result, so the button can show what just happened */
let last = null;

function runCli(args, timeoutMs = 20000) {
  return new Promise((resolve) => {
    if (!existsSync(SCRIPT)) {
      resolve({ ok: false, error: `recorder not found at ${SCRIPT}` });
      return;
    }
    let child;
    try {
      child = spawn(process.execPath, [SCRIPT, ...args], {
        cwd: SKILL_DIR,
        stdio: ['ignore', 'pipe', 'pipe'],
        env: process.env,
      });
    } catch (error) {
      resolve({ ok: false, error: String(error && error.message ? error.message : error) });
      return;
    }
    let out = '';
    let err = '';
    const timer = setTimeout(() => {
      try {
        child.kill('SIGTERM');
      } catch {}
    }, timeoutMs);
    child.stdout.on('data', (d) => (out += d));
    child.stderr.on('data', (d) => (err += d));
    child.on('error', (error) => {
      clearTimeout(timer);
      resolve({ ok: false, error: String(error.message) });
    });
    child.on('exit', (code) => {
      clearTimeout(timer);
      const text = out.trim();
      let json = null;
      try {
        json = JSON.parse(text);
      } catch {
        const lines = text.split('\n').filter(Boolean);
        for (let i = lines.length - 1; i >= 0; i--) {
          try {
            json = JSON.parse(lines[i]);
            break;
          } catch {}
        }
      }
      resolve({ ok: code === 0, code, json, stdout: out, stderr: err });
    });
  });
}

async function status() {
  const r = await runCli(['status'], 8000);
  const rec = r.json && r.json.recording ? r.json.recording : null;
  if (rec && recording && recording.pid !== rec.pid) recording = null;
  // a stale failure must not keep re-surfacing in the composer forever:
  // surface a failure only while it is fresh, successful results always
  const fresh = last && (last.ok === true || Date.now() - Number(last.at || 0) < 20000);
  return { ok: true, recording: rec, last: fresh ? last : null };
}

async function startRecording(payload = {}) {
  const existing = await status();
  if (existing.recording) return { ok: true, ...existing };

  const check = await runCli(['check'], 10000);
  if (!check.ok) {
    last = { at: Date.now(), action: 'start', ok: false, error: (check.json && check.json.error) || check.stderr || 'screen control unavailable' };
    return { ok: false, ...last };
  }

  const stamp = new Date();
  const hh = String(stamp.getHours()).padStart(2, '0');
  const mm = String(stamp.getMinutes()).padStart(2, '0');
  const name = String(payload.name || `手机录制 ${hh}:${mm}`);
  const interval = Math.min(5000, Math.max(250, Number(payload.interval || 400)));

  let logFd = 'ignore';
  try {
    const { openSync } = await import('node:fs');
    logFd = openSync(path.join(process.env.TMPDIR || '/data/local/tmp', 'skill-recorder-host.log'), 'a');
  } catch {}
  const child = spawn(
    process.execPath,
    [SCRIPT, 'start', '--name', name, '--interval', String(interval), '--max', '1800', '--ignore-pkg', 'app.dsh.mobile'],
    { cwd: SKILL_DIR, detached: true, stdio: ['ignore', logFd, logFd], env: process.env }
  );
  child.unref();
  recording = { pid: child.pid, name, startedAt: stamp.toISOString() };
  last = { at: Date.now(), action: 'start', ok: true, name };

  // the CLI spends ~1s on its accessibility self-check before it writes
  // .active.json, so poll instead of assuming a fixed delay
  const deadline = Date.now() + 8000;
  let snapshot = await status();
  while (!snapshot.recording && Date.now() < deadline) {
    await new Promise((r) => setTimeout(r, 400));
    snapshot = await status();
  }
  return snapshot;
}

/** 任务跑完推一条系统通知：用户切到别的 App 也能看到 */
function notifyDone(title, body) {
  try {
    const port = Number(process.env.DSH_BRIDGE_PORT || 3083);
    const payload = JSON.stringify({ title, body });
    const req = http.request(
      {
        host: '127.0.0.1',
        port,
        path: '/notify',
        method: 'POST',
        timeout: 4000,
        headers: { 'content-type': 'application/json', 'X-DSH-Token': process.env.DSH_BRIDGE_TOKEN || '' },
      },
      (res) => res.resume()
    );
    req.on('error', () => {});
    req.on('timeout', () => req.destroy());
    req.end(payload);
  } catch {}
}

async function stopRecording() {
  const r = await runCli(['stop'], 10000);
  recording = null;
  const compile = r.ok === false ? null : await runCli(['compile', '--max-steps', '25'], 30000);
  const noEvents = !!(compile && !compile.ok && /no events/i.test(String(compile.stderr || '')));
  const result = {
    ok: !!(r.ok && (noEvents || (compile && compile.ok))),
    stopped: r.json && r.json.stopped ? r.json.stopped : null,
    compile: compile && compile.json ? compile.json : null,
    warning: noEvents ? '这次没有录到画面变化（可能操作太快，或一直停留在 DSH 里）' : null,
    error: r.ok ? (compile && !compile.ok && !noEvents ? compile.stderr : null) : r.stderr || 'stop failed',
  };
  if (result.ok && result.compile) {
    notifyDone('✅ 录制完成', `已生成 ${result.compile.steps} 步草案（${result.compile.needsReview} 步待确认）`);
  } else if (noEvents) {
    notifyDone('⚠️ 录制结束', '这次没录到画面变化，建议重录一遍');
  }
  last = { at: Date.now(), action: 'stop', ...result };
  return { ...result, ...(await status()), last };
}

async function compile() {
  const r = await runCli(['compile', '--max-steps', '25'], 30000);
  last = { at: Date.now(), action: 'compile', ok: r.ok, result: r.json || null, error: r.ok ? null : r.stderr };
  return { ok: r.ok, compile: r.json || null, error: r.ok ? null : r.stderr, last };
}

/* ------------------------- 录制库（选择历史录制） ------------------------- */

const readJson = (p) => {
  try {
    return JSON.parse(readFileSync(p, 'utf8'));
  } catch {
    return null;
  }
};
const countLines = (p) => {
  try {
    return readFileSync(p, 'utf8').split('\n').filter(Boolean).length;
  } catch {
    return 0;
  }
};

/** 只允许操作 sessions/ 下的目录名，防止路径穿越 */
function sessionDir(id) {
  const safe = String(id || '').trim();
  if (!safe || !/^[\p{L}\p{N} ._@-]+$/u.test(safe) || safe.startsWith('.')) throw new Error(`bad session id: ${id}`);
  const dir = path.join(SESS_DIR, safe);
  if (!dir.startsWith(SESS_DIR + path.sep)) throw new Error('bad path');
  if (!existsSync(dir)) throw new Error(`session not found: ${safe}`);
  return dir;
}

function listSessions() {
  let names = [];
  try {
    names = readdirSync(SESS_DIR, { withFileTypes: true })
      .filter((d) => d.isDirectory() && !d.name.startsWith('.'))
      .map((d) => d.name);
  } catch {}
  return names
    .map((id) => {
      const dir = path.join(SESS_DIR, id);
      const meta = readJson(path.join(dir, 'meta.json')) || {};
      const plan = readJson(path.join(dir, 'plan-draft.json'));
      const sbPath = path.join(dir, 'storyboard.md');
      let compiledAt = null;
      try {
        compiledAt = statSync(sbPath).mtime.toISOString();
      } catch {}
      const steps = plan && Array.isArray(plan.steps) ? plan.steps.length : null;
      return {
        id,
        name: meta.name || id,
        startedAt: meta.startedAt || null,
        endedAt: meta.endedAt || null,
        interval: meta.interval || null,
        frames: countLines(path.join(dir, 'frames.jsonl')),
        events: countLines(path.join(dir, 'events.jsonl')),
        steps,
        needsReview: plan && Array.isArray(plan.steps) ? plan.steps.filter((s) => s && s.needsReview).length : null,
        hasStoryboard: !!compiledAt,
        compiledAt,
      };
    })
    .sort((a, b) => String(b.startedAt || '').localeCompare(String(a.startedAt || '')));
}

function readSession(id) {
  const dir = sessionDir(id);
  let storyboard = '';
  try {
    storyboard = readFileSync(path.join(dir, 'storyboard.md'), 'utf8');
  } catch {}
  const plan = readJson(path.join(dir, 'plan-draft.json'));
  return { ok: true, id, storyboard: storyboard.slice(0, 40000), plan };
}

async function compileSession(payload = {}) {
  const id = String(payload.id || '');
  const dir = sessionDir(id);
  const r = await runCli(['compile', '--session', id, '--max-steps', '25'], 40000);
  last = { at: Date.now(), action: 'compile-session', ok: r.ok, result: r.json || null, error: r.ok ? null : r.stderr };
  if (!r.ok) return { ok: false, error: r.stderr || 'compile failed' };
  const sess = listSessions().find((s) => s.id === id) || null;
  let storyboard = '';
  try {
    storyboard = readFileSync(path.join(dir, 'storyboard.md'), 'utf8');
  } catch {}
  return { ok: true, compile: r.json || null, session: sess, storyboard: storyboard.slice(0, 40000) };
}

/** 选中一份已编译的录制 → 发布成可复用技能 */
async function saveSkill(payload = {}) {
  const id = String(payload.id || '');
  const dir = sessionDir(id);
  const planPath = path.join(dir, 'plan-draft.json');
  if (!existsSync(planPath)) return { ok: false, error: '这份录制还没有编译过，先生成草案' };
  const meta = readJson(path.join(dir, 'meta.json')) || {};
  const slug = String(payload.skillName || '')
    .trim()
    .replace(/[^\p{L}\p{N}]+/gu, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 40);
  if (!slug) return { ok: false, error: '技能名不能为空' };
  const title = String(payload.title || meta.name || slug);
  const r = await runCli(['save', '--name', slug, '--plan', planPath, '--title', title], 20000);
  last = { at: Date.now(), action: 'save-skill', ok: r.ok, error: r.ok ? null : r.stderr };
  return { ok: r.ok, skill: r.json || null, error: r.ok ? null : r.stderr };
}

/** 清空：id 为空或 '*' → 删掉全部录制；否则只删这一份 */
async function clearSessions(payload = {}) {
  const id = String(payload.id || '').trim();
  const all = !id || id === '*' || id === 'all';
  // 正在录制时不动目录，避免把还在写入的会话删掉
  if (recording || (await status()).recording) {
    return { ok: false, error: '正在录制中，先停止再清理', sessions: listSessions() };
  }
  const targets = all ? listSessions().map((s) => s.id) : [id];
  const removed = [];
  const failed = [];
  for (const t of targets) {
    try {
      const dir = sessionDir(t);
      rmSync(dir, { recursive: true, force: true });
      removed.push(t);
    } catch (e) {
      failed.push({ id: t, error: String(e && e.message ? e.message : e) });
    }
  }
  last = { at: Date.now(), action: 'clear', ok: failed.length === 0, removed: removed.length };
  return { ok: failed.length === 0, removed, failed, sessions: listSessions() };
}

async function handle(endpoint, payload) {
  switch (endpoint) {
    case 'status':
      return await status();
    case 'start':
      return await startRecording(payload || {});
    case 'stop':
      return await stopRecording();
    case 'compile':
      return await compile();
    case 'list':
      return { ok: true, sessions: listSessions() };
    case 'read':
      return readSession(payload && payload.id);
    case 'compile-session':
      return await compileSession(payload || {});
    case 'save-skill':
      return await saveSkill(payload || {});
    case 'clear':
      return await clearSessions(payload || {});
    default:
      return { ok: false, error: `unknown endpoint: ${endpoint}` };
  }
}

function startNotifier() {
  try {
    const p = path.join(DSH_HOME, 'tools', 'turn-notify.mjs');
    if (!existsSync(p)) return;
    const child = spawn(process.execPath, [p, 'start'], { detached: true, stdio: 'ignore', env: process.env });
    child.unref();
  } catch {}
}

export function apply(ctx) {
  ctx.effect(
    () =>
      ctx.connection.fetch.register({
        path: ROUTE,
        methods: ['POST'],
        requestBody: 'buffered',
        fetch: async (request) => {
          let body = {};
          try {
            body = await request.json();
          } catch {}
          let result;
          try {
            result = await handle(String(body && body.endpoint ? body.endpoint : 'status'), body && body.payload);
          } catch (error) {
            result = { ok: false, error: String(error && error.message ? error.message : error) };
          }
          return new Response(JSON.stringify(result), {
            status: 200,
            headers: { 'content-type': 'application/json', 'cache-control': 'no-store' },
          });
        },
      }),
    'skill-recorder: api route'
  );
  startNotifier();
}
