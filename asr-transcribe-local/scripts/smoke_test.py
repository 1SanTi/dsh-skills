#!/usr/bin/env python3
"""Explicitly separate preflight, real audio pipeline, and accuracy evaluation."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from check_env import inspect
from transcribe import configure_console


def main():
    configure_console()
    ap = argparse.ArgumentParser(description="默认只检查环境；提供真实短音频才运行本地转写，不自动上云。")
    ap.add_argument("--audio")
    ap.add_argument("--model", default="small")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--output-dir", default="./smoke-outputs")
    args = ap.parse_args()
    print(json.dumps(dict(environment=inspect()), ensure_ascii=False))
    script = str(Path(__file__).with_name("transcribe.py"))
    r = subprocess.run([sys.executable, script, "--help"], stdout=subprocess.DEVNULL)
    if r.returncode:
        return r.returncode
    if not args.audio:
        print(json.dumps(dict(status="preflight_only", recognition_tested=False,
                              note="未提供音频；未验证模型加载、转写链路或识别质量。"), ensure_ascii=False))
        return 0
    cmd = [sys.executable, script, args.audio, "--engine", "local", "--model", args.model,
           "--formats", "txt,srt,vtt,md,json", "--output-dir", args.output_dir]
    if args.offline:
        cmd.append("--offline")
    result = subprocess.run(cmd)
    print(json.dumps(dict(status="audio_pipeline_completed" if result.returncode == 0 else "audio_pipeline_not_completed",
                          accuracy_evaluated=False, note="需与人工参考稿逐项比对后，才能评价准确率。"), ensure_ascii=False))
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
