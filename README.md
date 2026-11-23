# dsh-skills

本人自研 / 本地化的 DSH 技能合集，备份到 GitHub。

包含：IMA 笔记与知识库、金山文档(KDocs)、微信发图、B站历史分享、WPS 发微信、湖南学法网、任务通知、本地语音转写、科研配图、手绘视频等工具技能，以及 dsh-skill-recorder 插件源码。

## 重点技能：skill-recorder（手机录制即技能）

把「在手机上演示一遍」变成「以后一句话就能重复执行」。

- 录制时按固定间隔读屏（`scr dump`），只保留画面真的变了的那些屏；
- 把「上一屏 → 下一屏」编译成 `loop run` 计划草案（消失的可点击控件 → 猜测的点击目标，新出现的文本 → 验证锚点）；
- 草案人工/Agent 审核后发布成独立技能。

目录：`skill-recorder/` 是技能本体，`dsh-skill-recorder/` 是 DSH 里的录制按钮 + 录制库面板插件。

**本仓库直接带了离线语音识别的全部资产**（`skill-recorder/asr/`，约 79 MB），所以 clone 下来就能用 `--audio` 录旁白转写，不需要额外下载模型、也不需要联网：

| 路径 | 用途 | 大小 |
| --- | --- | --- |
| `asr/models/whisper-tiny/` | Whisper tiny（quantized int8）ONNX 模型 + tokenizer | 42 MB |
| `asr/web/transformers.min.js` | transformers.js 浏览器打包 | 0.9 MB |
| `asr/web/ort-wasm*.wasm` | onnxruntime-web 的 4 个后端（simd / threaded / 组合） | 37 MB |

运行时全部走本地文件：`env.allowRemoteModels=false`、`env.localModelPath='/models/'`、`wasmPaths='/v/'`，由 `scripts/asr-local.mjs` 起一个 `127.0.0.1:3802` 的页面在浏览器里跑推理，结果写 `transcript.json`。不录音频时完全不碰这些文件。

> 只想要屏幕录制、不需要旁白的，可以只保留 `SKILL.md` 和 `scripts/`，删掉 `asr/` 也不影响 `start / stop / compile`。

## 关于示例数据

技能文档里出现的联系人名、学校名、地名、手机号、密码，一律是占位符或化名，只用来演示操作步骤，不对应任何真实个人或机构。

## 关于凭据

本仓库不含任何密钥。需要 key 的技能（如 `miaoda-app-builder`）由使用者自己提供：写进本地的 `.miaoda_key` 即可，该文件已在 `.gitignore` 中排除，不要提交。

## 关于运行态数据

`skill-recorder/sessions/` 这类录屏产物会包含真实屏幕内容（聊天记录、联系人、通知），**不要提交到本仓库**，已在 `.gitignore` 中排除。
