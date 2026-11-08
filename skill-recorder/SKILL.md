---
name: skill-recorder
description: Record a real task on this Android phone by sampling the screen at each transition, then compile the recorded screens into a reviewable loop plan and publish it as a reusable skill. Use when the user asks to record/learn a phone workflow, turn a demonstration into a skill or automation, or replay what they just did - 录屏录操作、演示一遍、把刚才的操作变成技能、学习我的操作流程、录制手机操作、录制后自动回放。
metadata:
  slug: skill-recorder
  displayName: Skill Recorder（手机录制即技能）
  version: 1.0.0
  category: 自动化
  platforms: [Android/DSH Mobile]
---

# Skill Recorder（手机端录制即技能）

把「在手机上演示一遍」变成「以后一句话就能重复执行」。

录制器在用户操作期间按固定间隔读取屏幕（`scr dump`），只保留发生实质变化的画面，
然后把「上一屏 → 下一屏」的转换编译成 `loop run` 计划草案：

- 消失的可点击控件 → 猜测的点击目标
- 新出现的文本 → 用于验证的锚点

草案必须经过人工/Agent 审核，再发布成独立技能。

> 与微软 [microsoft/skill-recorder](https://github.com/microsoft/skill-recorder) 思路一致：
> 录一遍 → 重建意图与步骤 → 生成可复用 Skill。区别在于本技能是 **Android 版**，
> 直接跑在 DSH Mobile 上，不依赖桌面端、GitHub Copilot CLI 或 Electron。

## 能录什么、不能录什么

| 能 | 不能 |
| --- | --- |
| 每一屏的文字、坐标、可点击项、前台应用 | 原始触摸事件（Android 不向普通应用开放） |
| 由操作引起的屏幕跳转顺序 | 键盘输入的确切内容（只看到输入后的界面） |
| 通过 OCR 兜底识别 WebView / 画布类界面 | 跨设备、跨账号的隐藏状态 |

因此**录制的产物是「带候选动作的画面序列」**，不是逐帧点击回放。审核步骤是流程的一部分，不能跳过。

## 前提

1. 屏幕控制已开启：设置 → 无障碍 → **DSH Screen Control**。
2. 录制期间不要锁屏、不要切到别的任务再切回来超过一次（会引入无关画面）。
3. 涉及支付、银行、微信/QQ 等风控应用的流程不要录制自动回放（账号风险）。

## 快速开始

```sh
cd $DSH_HOME/skills/skill-recorder

# 0) 自检：无障碍是否可用
node scripts/recorder.mjs check

# 1) 开始录制（后台运行；用户此时在手机上演示任务）
node scripts/recorder.mjs start --name "把照片发到微信收藏"

#    ……用户操作……

# 2) 停止
node scripts/recorder.mjs stop

# 3) 编译成回放稿 + 计划草案
node scripts/recorder.mjs compile
```

> 别把 `start` 接在 `| head` 之类的管道后面：管道关闭会把录制进程一起带走。

**只录屏幕，不录音频（默认）**：录制全程只读无障碍树，不占麦克风、不打开任何页面，
所以你录的时候可以随便切到别的 App（浏览器后台被杀也不影响录制）。
需要旁白时再加 `--audio`（会借一个浏览器页当麦克风载体，切走可能被杀，非必要不用）。

产物在 `sessions/<会话id>/`：

- `frames.jsonl` — **逐帧**采样（默认 400ms 一帧，含未触发步骤的中间态）
- `events.jsonl` — 只保留“画面真的变了”的那几屏
- `storyboard.md` — 人类可读的步骤回放稿（含点击候选、过渡态、耗时）
- `plan-draft.json` — `loop run` 计划草案
- `narration.webm` / `transcript.json` — 仅 `--audio` 时才有

## 在 DSH 界面里用（录制库）

输入框那一排有两个按钮：

- **录制**：点一下开始采样，再点一下停止并自动生成草案。
- **录制库 N**：弹出一个小面板（宽约 300px、高不超过 38vh），**贴在按钮正上方、也就是对话框上方**，不会飘到屏幕左边。

面板只有三件事，尽量不占地方：

| 操作 | 效果 |
|---|---|
| 点一行 | 选中（那一行高亮）；行上只显示名字 + 开始时间，绿点=生成过、灰点=还没 |
| 生成文稿 | 给选中的那份重新编译，底部一行提示「已生成 N 步」，不把全文铺在界面上 |
| 发布 | 填个技能名（就地一行输入框）→ 存成 `skills/<名字>/SKILL.md` |
| 清空 | 就地二次确认，一次删掉全部录制；录制中禁止清空 |

想看详细步骤文稿就去 `sessions/<id>/storyboard.md`，或者直接让 Agent 读。
后端接口：`list / read / compile-session / save-skill / clear`，都在 `POST api/skill-recorder` 上，
和命令行共用同一套会话数据。

## 审核与发布

1. 打开 `storyboard.md` 逐步核对：目标控件是不是用户真正点的那个？
2. `plan-draft.json` 里带 `needsReview: true` 的步骤必须人工确认（锚点缺失或候选不唯一）。
3. 先试跑：`node scripts/recorder.mjs replay --plan sessions/<id>/plan-draft.json --dry` 看 JSON，
   去掉 `--dry` 才真正执行。
4. 发布成技能：

```sh
node scripts/recorder.mjs save --name photo-to-wechat --plan sessions/<id>/plan-draft.json --title "把照片存入微信收藏"
```

会在 `$DSH_HOME/skills/photo-to-wechat/SKILL.md` 生成可直接回放的技能，并把计划存到
`skills/skill-recorder/plans/photo-to-wechat.json`。

## 命令一览

| 命令 | 作用 |
| --- | --- |
| `check` | 自检无障碍与当前屏幕节点数 |
| `start --name <描述> [选项]` | 开始采样录制（前台进程，建议后台跑） |
| `stop` | 停止录制 |
| `status` / `list` | 当前录制状态 / 历史会话 |
| `compile [--session <id>] [--max-steps 20]` | 生成回放稿与计划草案 |
| `replay --plan <path> [--dry]` | 用 `loop run` 执行计划 |
| `save --name <skill> --plan <path>` | 发布成技能 |

`start` 的选项（括号内是默认值）：

| 选项 | 含义 |
| --- | --- |
| `--interval 400` | 采样间隔（ms，最低 250）。越小越连贯，代价是 CPU 与日志体积 |
| `--tick-diff 0.04` | 相邻两帧的文本差异阈值，用来抓“只变几个字”的中间态 |
| `--min-diff 0.12` | 相对上一张“已存画面”的阈值，用来抓累积变化 |
| `--burst-ms 200` | 检测到变化后进入连拍的间隔，用来抓 toast / 新标签页 / 加载完成 |
| `--burst-window 900` | 连拍持续多久（ms） |
| `--frames on` | 是否落 `frames.jsonl` 逐帧档（`off` 只留 events） |
| `--ignore-pkg <包名>` | 这个前台应用期间不记（插件用它排除 DSH 自己） |
| `--audio` | **默认关**。开了才会录麦克风 + 实时转写（借浏览器页，切走有概率被杀） |

## 录制质量技巧

- **正常速度操作就行**：默认 400ms 一帧（变化后 200ms 连拍），不需要刻意放慢；
  只有连续两次点击间隔 < 300ms 时才会被并成一跳。
- **别在 DSH 聊天界面上录**：流式输出会不停改屏，产生大量无关画面（插件已默认 `--ignore-pkg app.dsh.mobile`）。
- **录完先别关**：`compile` 之后先看 `needsReview` 数量，太多说明动作太快或页面在自动跳。
- 同一任务建议录两遍，第二遍用 `useMemory` 更稳；两遍草案一致再发布。
- 一次录制 2 分钟约 300 帧、`frames.jsonl` 数 MB；长录制想省体积用 `--frames off`。
- **需要说明操作意图时，直接对我说**（我记进 storyboard / 技能说明），比开 `--audio` 稳。

## 常见问题

**`check` 报 accessibility service not enabled** — 去 设置 → 无障碍 打开「DSH Screen Control」，然后重试。

**`compile` 说没有事件** — 画面几乎没变化（例如只是在输入框打字且无障碍没暴露文本），
改用 `scr dump` 手动确认；或降低 `--interval` 重录。

**候选目标为空** — 该次跳转不是由点击引起（返回键、自动跳转、网络加载），
在 `storyboard.md` 里手工标注即可，脚本不会猜错动作类型。

**回放失败** — 先 `scr dump` 看真实界面，再改 `target.text`；同一个失败步骤不要连续重试超过两次。
