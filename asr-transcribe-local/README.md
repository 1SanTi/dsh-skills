# 录音转文字 1.4.0

将会议、访谈、课程的录音转成带时间戳的文字稿或字幕。本地普通转写无需云端 API Key，首次需安装依赖并下载/准备模型。

## 开始使用

1. 让支持 Skill 和本地 Python 执行的 Agent 安装本 Skill。
2. 安装本地引擎：`python -m pip install faster-whisper`。
3. 运行 `python scripts/transcribe.py "录音.m4a"`，默认生成 TXT、SRT 和运行回执。

安装到 SkillHub/Agent 只安装说明和脚本，不等于 ASR 引擎及模型已经可用。首次模型下载可能需要网络与磁盘空间。普通 faster-whisper 解码通常不需要另装系统 ffmpeg；试转、WhisperX 和云端转码/切块需要 ffmpeg。

## 1.4.0 的变化

- 页面优先说明用途、普通本地模式的密钥要求与实际输出，去掉冗长关键词和作者专用路径。
- 默认本地引擎优先 faster-whisper，默认模型从 large-v3 改为 small；可按质量要求显式选择 large-v3。此调整降低资源需求，可能影响识别精度，需抽查。
- 新增 `--preview-seconds N` 和仅使用已缓存模型的 `--offline`（普通 faster-whisper 路径）。
- 每次创建独立输出子目录；WhisperX 仅在临时目录生成 JSON，不再扫描删除输出目录里的同名其他文件。
- 所有适配器共用 TXT、Markdown、SRT、VTT、JSON 输出；时间戳按毫秒进位，文字稿有待校对提示。SRT 保持标准字幕结构，待校对说明在回执中。
- 需要说话人分离却失败时停止，不静默回退；无语音结果返回独立状态，不冒充完整转写。
- 云端只在显式选择时运行；OpenAI 当前仅适配 whisper-1，支持分段时间戳；DashScope 保留 Paraformer 非流式适配。未声称其他模型或所有地区都兼容。
- 不再用“1 秒纯音生成文件”证明识别质量；自检分别报告依赖、脚本与实际音频验证。

## 使用与测试

- [安装与进阶配置](references/install.md)
- [输出格式、退出码、故障排查](references/output-format.md)
- `python scripts/verify_r.py`：确定性回归，含模拟引擎；不等于 ASR 准确率验证。
- `python scripts/smoke_test.py`：环境和命令检查，不转写；状态为仅完成预检。
- `python scripts/smoke_test.py --audio "测试录音.wav" --model small`：真实本地转写检查。使用你有权处理的短录音；首次可能下载模型。已有模型时加 `--offline`。

## 边界

模型、编解码器、语言、噪声和重叠说话均影响识别。中性说话人标签不等于真实身份；没有统一准确率承诺。后台模块被发现、测试通过、平台审核通过和用户第一次真实转写成功是不同状态。

发布包只含说明和脚本，不含模型、客户录音、密钥或个人环境。普通本地路径不主动把录音传给云 ASR；可选模型下载与第三方库行为应结合实际运行环境管理。

MIT License — Copyright (c) 2026 liu (博维管理咨询)
