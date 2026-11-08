import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { downloadId } from "./dl.mjs";

const OUT = "/storage/emulated/0/Download/工作室资料";
const LIST = "https://tcs.eaes.cn/2056202987599261741/gateway/specialTopic?columnId=2078001524301647951";
const LOG = "/data/user/0/app.dsh.mobile/files/dsh-home/tmpx/dl/harvest.log";
const MAX = Number(process.env.MAX || 8);
const sleep = (ms) => Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
const sh = (b, a) => execFileSync(b, a, { encoding: "utf8", maxBuffer: 96 * 1024 * 1024, timeout: 60000 });
const log = (s) => { const line = new Date().toISOString().slice(11, 19) + " " + s; console.log(line); try { fs.appendFileSync(LOG, line + "\n"); } catch {} };

// read the current page URL from the browser address bar (reliable; dump coords are broken)
function currentUrl() {
  sh("scr", ["tap", "900", "219"]);
  sleep(1300);
  let url = null;
  for (let i = 0; i < 3; i++) {
    try {
      const j = JSON.parse(sh("scr", ["dump-full"]));
      const texts = j.nodes.map((n) => n.text || "").join("\n");
      const m = texts.match(/https?:\/\/[^\s"']*(?:specialDetail|specialTopic)[^\s"']*/);
      if (m) { url = m[0]; break; }
    } catch {}
    sleep(700);
  }
  return url;
}
function dismissBar() { sh("scr", ["key", "back"]); sleep(600); }
function backToList() {
  dismissBar();
  sh("scr", ["key", "back"]); sleep(2200);
}
function openList() {
  sh("shz", ["am", "start", "-a", "android.intent.action.VIEW", "-d", LIST]);
  sleep(6500);
}
function onListUrl(u) { return !!u && /specialTopic/.test(u); }

const NAMES = /\.(docx?|pptx?|pdf|xlsx?|zip|rar|7z|mp4|jpg|png)$/i;
const norm = (s) => s.replace(/\s+/g, "").trim();
const have = new Set();
try { for (const f of fs.readdirSync(OUT)) have.add(norm(f)); } catch {}
log("start; already=" + have.size + " MAX=" + MAX);

const XS = [494, 1126, 1758, 2390];
const YS = [1098];
const seen = new Set();
let ok = 0, missed = 0;

outer:
for (let screen = 0; screen < 40; screen++) {
  let before = ok;
  for (const y of YS) {
    for (const x of XS) {
      if (ok >= MAX) break outer;
      sh("scr", ["tap", String(x), String(y)]);
      sleep(3200);
      const u = currentUrl();
      if (!u) { log("NO_URL at " + x + "," + y); dismissBar(); continue; }
      if (onListUrl(u)) { log("still list at " + x + "," + y); continue; } // tap missed the card
      const m = u.match(/resourceId=(\d+)/);
      if (!m) { log("NO_ID url=" + u.slice(0, 100)); backToList(); continue; }
      const id = m[1];
      dismissBar();
      if (!seen.has(id)) {
        seen.add(id);
        try {
          const r = await downloadId(id);
          const known = have.has(norm(r.name));
          if (!known) { have.add(norm(r.name)); ok++; log("OK " + ok + " | " + id + " | " + r.name + " | " + r.size); }
          else { log("SKIP(dup) " + r.name); }
        } catch (e) {
          log("FAIL " + id + " " + e.message); missed++;
          if (/list|UL/.test(e.message)) {}
        }
      } else { log("seen " + id); }
      backToList();
    }
  }
  // scroll down one screen and continue
  sh("scr", ["swipe", "1472", "1400", "1472", "840", "420"]);
  sleep(1500);
  if (ok === before) { missed++; if (missed >= 2) { log("no progress, stop"); break; } }
}
log("FINISHED ok=" + ok + " have=" + have.size);
process.exit(0);
