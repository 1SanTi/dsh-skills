---
name: send-wps-file
description: Find a file in WPS Office (金山文档 / 我的云文档 / 最近) and send it as a real file attachment to a named contact in WeChat (or QQ), with recipient verification before the send. Use when the user says 把某个文件/试卷/文档发给某人、发个文件给X、从WPS里找出来发给X、微信发送文件、转发文档给老师。Triggers: 发文件、发送文件、把文件发给、发给某人、WPS里找文件、云文档转发、微信发文件给老师。
metadata:
  slug: send-wps-file
  displayName: WPS 找文件并发送给指定人
  version: 1.0.0
  category: 自动化
  platforms: [Android/DSH Mobile]
---

# 从 WPS 找文件 → 微信发给指定人

把「在 WPS 里翻出一份文件、以文件本体发到微信某个联系人」固化成一键流程。
本技能描述的是**这台手机**（app.dsh.mobile，2944×1808，ZUI）上实测走通的路径，
坐标仅作参考，每一步都以 `scr dump` 的文字校验为准。

## 参数

| 参数 | 说明 | 例 |
| --- | --- | --- |
| `{file}` | 文件名关键词（够唯一即可） | `名著阅读`、`红星照耀中国` |
| `{contact}` | 微信联系人/群名 | `小刘老师` |
| `{channel}` | 默认 `微信`，可换 `QQ` | `微信` |

## 前置检查（一次）

```sh
scr pkg            # 无障碍可用
shz id             # Shizuku 可用（拉起 WPS 需要）
```

- 无障碍未开 → 让用户开「DSH Screen Control」，或用 shz 写 secure 设置（见 memory）。
- WPS 未登录 → 只能看到本机文件，云文档搜不到，停下告知用户。
- 微信未登录 → 停在分享选择器，停下告知用户。

## 步骤

### 1. 拉起 WPS

```sh
bash scripts/open-wps.sh    # 期望输出 wps-foreground: ok
```

> `scr launch cn.wps.moffice_eng` 和 `monkey` 在这台机器上都不生效
> （WPS 会被压回后台），必须用 `am start` 主 activity。

### 2. 找文件（两条路，按优先级）

**A. 搜索**（文件多、记得关键词时）

```sh
scr dump | grep -E "搜索"        # 找到搜索框坐标，通常约 1288,129
scr tap <x> <y>
scr input "{file}"              # 中文一次输入，不要分段
scr tap <搜索按钮>               # 输入框右侧放大镜，约 2886,133
sleep 3 && scr dump             # 看「搜索历史/搜索结果」里是否有目标
```

**B. 最近列表**（搜索无结果时）

```sh
scr tap 90 157                  # 左上角 ≡，打开「最近」
scr dump | grep -A2 "{file}"    # 文件按「今天/昨天 修改」排序
```

命中判定：`scr dump` 里出现包含 `{file}` 的文件名行。
**多个候选 → 停下来把候选列给用户选，不要自己挑。**

### 3. 打开并确认（可选但推荐）

```sh
scr tap <文件行>
scr dump | head -3              # 标题行应含 {file}
```

确认是本份文件后再继续；发错文件比发失败更糟。确认完按 `scr key back` 回到列表。

### 4. 分享面板 → **以文件发送**

这是整条流程最容易走错的一步。

```sh
scr long-press <文件行x> <文件行y> 900   # 长按文件
scr tap <分享>                        # 菜单第一项
scr swipe 1472 1500 1472 700 400      # 面板向上滑
scr dump | grep -E "更多发送方式|以文件发送"
scr tap <以文件发送>
```

> WPS 默认那一排（微信/QQ/复制链接/二维码）发出去的是**金山文档链接**。
> 要发文件本体，必须滑到「更多发送方式」→「以文件发送」。

### 5. 选渠道 → 选联系人

```sh
# 系统分享面板
scr tap <发送给朋友>
scr dump | grep -E "请选择|微信|QQ"    # 系统解析器
scr tap <微信>
# 微信「选择聊天」页
scr dump | grep "{contact}"
scr tap <{contact} 所在行>
```

联系人同名/近似（如「小刘老师」与「刘薇老师」）时：**只认精确文字**，
点完必须看预览页；对不上就 `scr key back` 重选，不要猜。

### 6. 发送前校验（强制）

预览页必须同时满足：

- 出现 `发送给：{contact}`
- 出现文件名（含 `{file}`）和体积
- 底部有绿色「发送」按钮

全部满足才：

```sh
scr tap <发送按钮坐标>
```

任一不满足 → 停，告知用户哪里不对，不点发送。

### 7. 验证已送达

```sh
sleep 5
scr dump | grep -E "{contact}|{file}"   # 聊天页应出现时间 + 文件名 + 体积
```

看到聊天里新出现的文件卡片才算成功。只看到「已点击」不代表已发送。

## 安全边界

- **微信/QQ 界面自动化有账号风控风险**：只在用户要求并知情时执行；发送前必须确认收件人，
  发送失败**不要连点重试**，先 `scr dump` 看真实状态。
- 一次只发一个文件；批量发送要用户逐条确认。
- 风控敏感内容（支付、银行、验证码）一律不发。
- 不把聊天内容、联系人列表写进日志或记忆。

## 常见失败

| 现象 | 处理 |
| --- | --- |
| `open-wps.sh` 失败 | 让用户手点 WPS 图标，再重跑脚本 |
| 搜索无结果 | 走「最近列表」；仍没有 → 文件可能在「共享/星标」或本机，停下问用户 |
| 长按没有菜单 | 长按时长加到 1200ms，或点行尾「…」 |
| 分享面板没有「以文件发送」 | 面板没滑到底，再向上滑一次 |
| 选择器里找不到联系人 | 用顶部搜索框输 `{contact}`；仍无 → 用户可能没加好友/群名不同 |
| 点发送无反应 | 看是否有「文件较大，用流量发送」确认框，按实际情况处理 |
