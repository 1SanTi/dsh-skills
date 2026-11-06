#!/bin/bash
# 秒哒 CLI 包装器：自动注入 MIAODA_API_KEY（存于 ../.miaoda_key，权限 600）
HERE="$(cd "$(dirname "$0")" && pwd)"
KEY_FILE="$HERE/../.miaoda_key"
if [ -z "${MIAODA_API_KEY:-}" ] && [ -f "$KEY_FILE" ]; then
  MIAODA_API_KEY="$(cat "$KEY_FILE")"
  export MIAODA_API_KEY
fi
PY="${PYTHON:-$(command -v python3 || echo /data/user/0/app.dsh.mobile/files/engine/extensions/python/bin/python3)}"
exec "$PY" "$HERE/miaoda_api.py" "$@"
