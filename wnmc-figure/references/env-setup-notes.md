# WorkBuddy 本机部署的环境坑位与修复（2026-09 实测）

本文件仅适用于在 WorkBuddy 本机（Windows）部署本技能时的环境问题。通用环境要求见 SKILL.md「环境」一节。

## 验证过的解释器

- Python 解释器: `C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Scripts/python.exe`
- 缺包时用宿主解释器补装：`C:/Users/Administrator/.workbuddy/binaries/python/versions/3.13.12/python.exe -m pip --python <venv> install <pkg>`

## 依赖坑位实测

1. **venv 内 pip 自身损坏**（`No module named pip._internal`）：一律改用宿主解释器 `python -m pip --python <venv路径>` 安装。
2. **svglib 与新版 cssselect2 不兼容**（`module 'cssselect2' has no attribute 'Matcher'`）：需 `--ignore-installed --no-deps cssselect2==0.7.0` 强制覆盖（普通卸载会因缺 RECORD 报 uninstall-no-record-file）。
3. **pypdfium2 半安装**（有 dist-info 无包目录）：同样用 `--ignore-installed --no-deps pypdfium2` 修复。

## 中文字体

- Windows: SimHei（`C:\Windows\Fonts\simhei.ttf`，库自动注册）
