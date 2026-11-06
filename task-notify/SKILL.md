---
name: task-notify
description: 任务跑完时给你发一条系统通知，切到别的 App 也能看到。当用户说“做完了通知我”“后台跑完提醒我”“我看不到进度”时使用；也可以每个较长自动化任务结束时主动调用。
---

# 任务完成通知

两条链路：

| 场景 | 触发 | 通知内容 |
|---|---|---|
| **任意对话任务** | `tools/turn-notify.mjs` 守护进程盯着会话日志，发现新的 `turn/end` | 「✅ DSH 任务完成 · 『会话标题』已完成」 |
| **录制结束** | dsh-skill-recorder 插件在 stop→compile 之后 | 「✅ 录制完成 · 已生成 N 步草案」 |
| **手动/脚本** | `notify "文字"` 或桥 `POST /notify` | 自定义 |

## 守护进程

```sh
node $DSH_HOME/tools/turn-notify.mjs start    # 后台常驻（引擎重启后插件会自动拉起）
node $DSH_HOME/tools/turn-notify.mjs status
node $DSH_HOME/tools/turn-notify.mjs stop
node $DSH_HOME/tools/turn-notify.mjs once     # 手动扫一次（调试）
```

原理：DSH 每完成一轮对话会往 `sessions/<工作区>/<会话>/session.v4.jsonl.zstd` 追加一条
`turn/end` 事件。守护进程每 4 秒扫一次最近 2 分钟动过的会话日志，解压后取最后一条
`turn/end`，比上次通知过的时间新、且已过 3 秒（避免把收尾中间态当完成），就调
`127.0.0.1:3083/notify` 推一条系统通知。状态记在 `tmpx/turn-notify.state.json`，同一个
turn 不会重复提醒；超过 30 分钟的历史 turn 只记账不补发。

## 直接发一条

```sh
notify "任务完成：已把 4 份文件发给小刘老师"
# 或带自定义标题（走桥）：
curl -s -X POST -H "X-DSH-Token: $DSH_BRIDGE_TOKEN" -H 'content-type: application/json' \
  -d '{"title":"DSH 任务完成","body":"B站视频已分享给三体"}' http://127.0.0.1:3083/notify
```

## 注意

- 通知是系统级常驻通知，可能被系统「勿扰」挡掉；声音/震动跟系统通知设置走。
- 守护进程依赖引擎的 3083 桥，引擎重启后由插件 `startNotifier()` 自动拉起；**App 被杀后需要重新 start**（或等下次开 App 后由插件拉起）。
- 日志：`tmpx/turn-notify.log`；重复通知排查看 `tmpx/turn-notify.state.json` 里的时间戳。
