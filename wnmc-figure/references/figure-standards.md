# 期刊插图技术规范（含版权与引用指引）

## 分辨率与格式

| 用途 | 最低要求 | 推荐输出 |
|---|---|---|
| 期刊线图/示意图 | 300 DPI | PDF(矢量) 或 TIFF 300–600 DPI |
| 半色调照片图 | 300 DPI | TIFF 300 DPI |
| 组合图(线图+照片) | 500 DPI | TIFF 500 DPI |
| 学位论文 | 300 DPI | PNG/TIFF 300 DPI + 矢量 PDF |
| PPT/教学 | 屏幕显示 | SVG 或 PNG 150 DPI |

导出命令：`c.export("fig1", formats=("png","tiff","pdf","svg"), dpi=300)`
- PDF 为矢量（无限放大不失真，期刊首选）；PNG/TIFF 按 `dpi/72` 倍光栅化并写入 DPI 元数据。
- TIFF 使用 LZW 无损压缩。
- 需要透明背景：`export(..., transparent=True)`（仅 PNG/TIFF）。

## 画布尺寸（参考期刊单栏/双栏）

| 版式 | 常见宽度 | 建议画布(px) |
|---|---|---|
| 单栏 | 80–90 mm | 1000–1100（300dpi） |
| 1.5 栏 | 120–140 mm | 1400–1700 |
| 双栏 | 170–183 mm | 2000–2200 |

高度一般 ≤ 247 mm。画布用 px 表示即可，导出时 DPI 决定物理尺寸。

## 字体

- 期刊偏好：Arial / Helvetica（西文）、SimHei（中文标签）。
- 字号：正文标注 14–18 px，图题 26–32 px，最小不低于 7 pt（约 20 px @300dpi 画布 1400px 时注意换算）。
- 基因/蛋白符号规范：基因 *斜体*（如 *TP53*），蛋白正体（p53），物种 *斜体*（*E. coli*）。
- 本库自动处理：含中文的文本自动用 SimHei；"bold" 对中文以同色描边模拟加粗（reportlab 无中文粗体变体）。

## 配色

- 使用色盲友好配色；本库调色板（bio_graphics.C）已按此设计：
  blue #3B7DBF / teal #2A9D8F / orange #E76F51 / yellow #E9C46A / purple #7B5EA7 / green #5B9E51 / red #D64550
- 每色配浅色底（`_l` 后缀）用于填充，深色用于描边/文字。
- 不要用红绿对表达"对立"语义（红绿色盲不可分）；对立语义用 红vs蓝 或 橙vs青。
- 语义色约定（课题组内保持一致即可）：红色=损伤/促凋亡/上调，绿色=保护/抗凋亡/下调，蓝色=中性结构，紫色=核酸/核相关，黄色=能量/ATP/脂质。

## 版权与引用（重要）

1. **本技能生成的所有图形**为代码原创矢量图形，版权归使用者，可自由用于论文、教学、商业。
2. 若改用第三方素材平台（BioGDP、BioRender、Servier Medical Art 等），必须遵守其许可：
   - **BioGDP**：学术/教育用途免费，**禁止商用**；用于期刊发表需在其平台导出"授权许可"文件，并引用其论文：
     > Generic Diagramming Platform (GDP): a comprehensive database of high-quality biomedical graphics. *Nucleic Acids Research*, 2025. PMID: 39470721, DOI: 10.1093/nar/gkae973
   - BioRender：付费订阅，发表需购买发表授权。
   - Servier Medical Art：CC-BY 3.0，需注明出处。
3. 不要将任何第三方平台的素材库批量下载/转存进本技能——那是再分发，超出其授权范围。
4. 用户自行持有版权的素材（自己拍的切片照片、自己买的授权图）可放入 `assets/` 一并使用。
