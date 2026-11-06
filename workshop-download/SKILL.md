---
name: workshop-download
description: 把「湖南省全玲玲数字教研工作室（心理健康教育）」湖南智慧教育平台上的资源下载到本机（/storage/emulated/0/Download/全玲玲工作室资料）。当用户说“下载工作室资料 / 琳琳老师工作坊的文件 / 再下几份 / 把这份资源下下来”，或给了某个资源的分享链接、resourceId、文件名时使用。纯命令行 + 平台匿名接口，不需要打开浏览器逐页点。
---

# 工作坊资料下载（湖南智慧教育平台 / tcs.eaes.cn）

站点：`siteId 2056202987599261741`（湖南省全玲玲数字教研工作室-心理健康教育）
专题资源列：`columnId 2078001524301647951`
下载目录：`/storage/emulated/0/Download/全玲玲工作室资料`

## 核心：匿名下载接口（不需要登录、不需要浏览器）

```sh
# resourceId 数组 → 签名下载地址（带 filename）
POST https://tcs.eaes.cn/api/api-tcs/resource/anon/downloadUrls
Content-Type: application/json
["2090021780363743243"]
# → {code:0, data:[{downloadUrl:"https://ossfs.eaes.cn/...&response-content-disposition=...filename*=UTF-8''..."}]}
```

文件名在 `downloadUrl` 的 `response-content-disposition` 里（`filename*=UTF-8''…`），
`ossfs.eaes.cn` 是带 `Expires` 的临时签名地址，拿到就要立刻下载（几分钟内有效）。

## 用法

```sh
S=$DSH_HOME/skills/workshop-download/scripts

# 1) 已知 resourceId，直接下（可传多个）
node $S/fetch.mjs 2090021780363743243
node $S/fetch.mjs 2090021780363743243 2092614963127980044

# 2) 只知道页面链接
#    https://tcs.eaes.cn/2056202987599261741/gateway/specialDetail?resourceId=…&categoryId=…
#    取出 resourceId= 后面那串数字，传给 fetch.mjs 即可

# 3) 不知道 ID、要按列表往下批量抓：UI 采集（需要屏幕控制 + 前台浏览器）
MAX=10 node $S/harvest.mjs      # 下 10 份新的，日志 tmpx/dl/harvest.log
```

`fetch.mjs` 会跳过“同名且同大小”的已有文件；`harvest.mjs` 会把已存在目录里的名字加入去重集。

## 取 resourceId 的可靠办法（重要）

页面本身的 a11y 坐标在这台机上不可靠（见“坑”），但**地址栏可读**：

1. `scr tap <卡片坐标>` 打开资源详情页（详情页桌面版是 4 列网格，
   屏幕 2944×1840 下第一排卡片图片区约在 `x=494/1126/1758/2390, y=1098`）。
2. `scr tap 900 219`（点地址栏）→ `scr dump-full` → 正则 `resourceId=(\d+)`。
   地址栏被点时是可编辑节点，`text` 里就是完整 URL。
3. `scr key back` ×2 回到列表（第一次收键盘，第二次返回）。

## 坑（都实测过）

- **列表接口抓不到**：`/api/api-mas/resource/anon/list` 存在但要求一个未公开的必填参数，
  任何 JSON body 都回 `{"code":1,"message":"must not be null"}`；换 query 参数则 `参数异常`。
  别在这上面耗时间，用 UI 采集或直接给 ID。
- **`scr dump` 坐标是负的**：浏览器多标签时每个 WebView 按 `-2944×n` 排开，
  可见标签页的节点 x 全是负数（如 -14196）。**不要用 dump 坐标点按**，
  用截图/已知网格坐标 `scr tap x y`（这是屏幕坐标，正常）。
- **`/resource/anon/downloadUrls` 返回 402/超时** 时通常是签名过期或网络抖动，重试 1 次即可。
- PDF 在浏览器里点“下载”会**内联打开而不落盘**；走本技能的接口下载才会真正存文件。
- 同名不同内容的文件会被覆盖（脚本按“同名同大小”判重），
  需要留档时先改名再下。
- 大文件（如 60MB 的 pptx）下载慢，node 里别用默认短超时。

## 已下载清单（2026-10-30）

目录里已有 11 份（开学第一课系列、悦纳青春系列、普查测评手册等），
当天目标是 50 份；后续继续跑 `harvest.mjs` 即可增量补齐。
