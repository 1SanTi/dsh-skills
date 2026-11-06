# 独立风格资产站点

线上地址：**[327 项风格资产库](https://story-handdrawn-style-library.vercel.app/)** · [45 秒翻书演示](https://story-handdrawn-style-library.vercel.app/demo/)

这个目录保存静态站点的部署配置。网页沿用 `references/style-library.html` 的图库和公开目录，构建结果写入独立的 `site-dist/`，不包含项目源代码、用户参考图或本地运行资料。

## 本地构建与预览

要求 Node.js 20+ 和支持 `libwebp` 的 FFmpeg。

```bash
npm run site:build
python3 -m http.server 8767 --directory site-dist
```

浏览 `http://localhost:8767/`；单独视频页为 `http://localhost:8767/demo/`。

- 327 项资产使用 440px WebP 缩略图和 1120px WebP 大图，保留画面比例；原 PNG 不修改。
- 放大窗口提供对应固定 Git 提交的原 PNG 链接。
- 首页与 `/demo/` 均提供 45 秒 H.264/AAC 原视频播放器，带播放控制、移动端内联播放和海报。
- 部署内容采用公开文件的明确清单；构建结果超过 100 MB 时退出报错。
- 构建会校验 327 项图片、30 项默认精选、本地资源链接及视频副本校验和，并输出体积摘要。
- `.site-build.json` 记录输入摘要和构建结果，用于重跑时复用已转换的图片；不包含本机绝对路径。

## Vercel 静态部署

构建后只部署 `site-dist/`。该目录包含 `vercel.json`、HTML、WebP、MP4 和许可文件，没有服务器或在线构建步骤。

```bash
vercel --cwd site-dist --prod
```

本项目在 Vercel 使用 `story-handdrawn-style-library` 独立项目，发布已构建的静态目录。仓库推送不会自动部署该站点；如果首次关联时 CLI 自动连接了 Git 仓库，可执行 `vercel git disconnect --cwd site-dist`，然后按上面的命令发布。

若使用 Vercel 控制台导入，请采用 `Other` 框架，安装命令留空、构建命令留空，输出目录为已上传静态目录本身。部署不需要把完整仓库或原始 PNG 上传至 Vercel。

重新生成图库数据后，先执行 `npm run styles:build`，再重建并部署站点。网站不读取本地私人风格库；个人参考图和收藏仍保存在各自的 Skill 工作区中。
