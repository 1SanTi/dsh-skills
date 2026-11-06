#!/system/bin/sh
# Bring WPS Office to the foreground.
#
# `scr launch cn.wps.moffice_eng` and `monkey -p ...` are unreliable on this
# device (WPS stays behind WeChat), but an explicit activity start works.
# Verified 2026-10-29 on app.dsh.mobile (ZUI / Android 15).
set -u
ACT="cn.wps.moffice_eng/cn.wps.moffice.documentmanager.ab.proxy.main"

if ! command -v shz >/dev/null 2>&1; then
  echo "open-wps: shz not found (Shizuku mode required)" >&2
  exit 2
fi

shz "am start -n $ACT" >/dev/null 2>&1 || true

i=0
while [ "$i" -lt 8 ]; do
  i=$((i + 1))
  sleep 1
  if scr pkg 2>/dev/null | grep -q '"pkg":"cn.wps.moffice_eng"'; then
    echo "wps-foreground: ok"
    exit 0
  fi
done

echo "wps-foreground: failed (try tapping the WPS icon manually, then rerun)" >&2
exit 1
