#!/usr/bin/env python3
"""Read-only capability discovery, not a claim of model readiness."""
import argparse
import json
import os
import shutil
import sys
from transcribe import available, configure_console


def inspect():
    return dict(python=sys.version.split()[0], ffmpeg=bool(shutil.which("ffmpeg")),
                faster_whisper_package=available("faster_whisper"),
                whisperx_command=bool(shutil.which("whisperx")),
                hf_token_present=bool(os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")),
                openai_package=available("openai"), openai_key_present=bool(os.environ.get("OPENAI_API_KEY")),
                dashscope_package=available("dashscope"), dashscope_key_present=bool(os.environ.get("DASHSCOPE_API_KEY")),
                model_cache_verified=False, recognition_tested=False)


def main():
    configure_console()
    ap = argparse.ArgumentParser(description="仅发现依赖和配置，不下载模型，不上传音频，不输出密钥")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    info = inspect()
    if not args.json:
        print("=== asr-transcribe 环境自检 ===")
    print(json.dumps(info, ensure_ascii=False, indent=2))
    if not args.json:
        print("发现依赖不等于模型已缓存、令牌有效或识别质量通过。")
        print("普通本地转写无需云端 API Key；首次需准备模型。安装见 references/install.md。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
