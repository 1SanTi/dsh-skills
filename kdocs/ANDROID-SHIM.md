# Android / DSH Mobile notes (local shim)

This skill folder is the official 金山文档 `kdocs` skill (v2.7.1), installed for
DSH Mobile on Android.

## What was changed locally

* `references/`, `scripts/`, `SKILL.md` — unmodified official files.
* The `kdocs-cli` Go binary cannot resolve DNS on Android (there is no
  `/etc/resolv.conf`, so the pure-Go resolver dials `[::1]:53` and fails with
  "connection refused"). A transparent shim fixes this:

  | Path | Purpose |
  | --- | --- |
  | `~/.local/bin/kdocs-cli` | real static arm64 binary (installed by `scripts/setup.sh`, replaced by `kdocs-cli upgrade`) |
  | `~/.local/lib/kdocs-proxy.cjs` | tiny local HTTP/CONNECT proxy; resolves via bionic/netd (Node `net.connect`) |
  | `$ENGINE/usr/bin/kdocs-cli` | wrapper on `PATH`: starts the proxy if needed, exports `HTTPS_PROXY=http://127.0.0.1:17890`, then execs the real binary |

  Consequence: always invoke `kdocs-cli` by name (wrapper), not by the absolute
  path `~/.local/bin/kdocs-cli` (raw binary → DNS error).
  After `kdocs-cli upgrade`, the wrapper keeps working (it execs the same path).

## Token

Stored by `kdocs-cli auth set-token` in `~/.config/kdocs-cli/token.enc`
(encrypted file backend — Android has no OS keychain). Check with
`kdocs-cli auth status`.
