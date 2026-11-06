# 安装与进阶配置

## 普通本地转写：建议先从这里开始

在 Skill 根目录运行，安装和执行使用同一个 Python。建议单独虚拟环境（例如 `python -m venv .venv`），按宿主方式激活后再安装。

```bash
python -m pip install faster-whisper
python scripts/check_env.py
python scripts/transcribe.py "录音.m4a" --model small --lang zh
```

Python 版本和 GPU 依赖以 [faster-whisper 官方说明](https://github.com/SYSTRAN/faster-whisper) 为准。普通 CPU 转写用默认 `--device cpu --compute-type int8`；GPU 需匹配 CUDA/CTranslate2 环境，可用 `--device cuda --compute-type float16`。

无需云端 API Key。首次会从模型仓库下载模型；也可将已准备好的兼容 CTranslate2 模型目录传给 `--model`。不能访问模型仓库时，不要误报“软件已坏”；按网络权限准备模型。模型缓存齐备后用 `--offline` 禁止普通转写时下载模型。该参数不能证明整个电脑或所有第三方软件绝对无网络活动。

## 先试转 30 秒

需要 ffmpeg。先确认命令 `ffmpeg -version` 可运行；Windows 可使用 `winget install Gyan.FFmpeg`，macOS 可使用 `brew install ffmpeg`，Linux 按发行版安装。仅在已有安装权限内操作。

```bash
python scripts/transcribe.py "会议.m4a" --preview-seconds 30
```

生成的是开头片段，不是整场会议。若要全文，去掉 `--preview-seconds` 再运行；默认 small，资源允许且质量优先时可选 medium 或 large-v3。分段会影响跨段语境，不能把各段的 SPEAKER_00 自动当成同一人。

## 区分说话人：按需配置

安装并激活 WhisperX 环境，准备 ffmpeg，以及 Hugging Face 访问令牌和模型访问权限。

```bash
python -m pip install whisperx
python scripts/transcribe.py "访谈.wav" --diarize --speakers 3 --model small
```

HF_TOKEN 用环境变量提供，不写进 Skill、共享文件或命令示例。WhisperX 版本所用的说话人模型和用户协议见 [WhisperX 官方安装说明](https://github.com/m-bain/whisperX)。由用户本人处理相关账号权限和协议，不能假定令牌存在就已获模型访问权。脚本仍保留 `--hf-token` 兼容参数，但不推荐在命令行明文输入。

`--speakers N` 与 `--min-speakers N --max-speakers M` 二选一。不填则让模型估计人数。重叠发言、短句、噪声可能导致错分或部分片段无标签。失败时报告原因，用户同意普通版本后才去掉 `--diarize`。当前 `--offline` 开关只支持普通 faster-whisper 路径；WhisperX 离线部署需预备其多个模型，不能混用承诺。

## 可选云端：只有该文件已获授权才使用

云端会把音频发给服务商，可能收费。所属单位的保密要求、地区、服务条款与账户权限需按实际情况确定，不能因为“国产”而自动宣称合规。本地不可用时脚本不会自动调用云端。

OpenAI：安装 `python -m pip install openai`，在环境中设置 OPENAI_API_KEY。

```bash
python scripts/transcribe.py "录音.mp3" --engine cloud --cloud-provider openai --formats txt,srt,vtt
```

本适配器只支持 `whisper-1` 的 verbose_json 片段时间戳；不能把其他模型名直接代入。文件达到 24,000,000 字节时转换为 16kHz 单声道 PCM 并按约 10 分钟切块，因此需要 ffmpeg，时间偏移依据实际块长度累计。切点可能影响句子，需要回听。见 [OpenAI 音频转写文档](https://developers.openai.com/api/docs/guides/speech-to-text)。

DashScope：安装 `python -m pip install dashscope`，在环境中设置 DASHSCOPE_API_KEY。

```bash
python scripts/transcribe.py "录音.wav" --engine cloud --cloud-provider dashscope --formats txt,srt,vtt
```

使用 `paraformer-realtime-v2` 非流式文件调用，需 ffmpeg 转为 16kHz 单声道 WAV。模型权限、地区、额度和服务限制以 [DashScope 官方 SDK 文档](https://www.alibabacloud.com/help/zh/model-studio/paraformer-real-time-speech-recognition-python-sdk) 为准，不将它描述成无限时长离线文件服务。当前两个云端适配器均不提供说话人分离。
