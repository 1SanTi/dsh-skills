---
name: medical-illustration
description: 生成期刊级医学生物学示意图（信号通路图、细胞结构图、组织胚胎学示意、实验流程图、机制图等）。当用户需要绘制医学/生物学插图、科研配图、SCI 论文 Figure、机制图、教学示意图，或提到绘图/插图/figure/示意图/通路图时使用。所有图形为代码生成的原创矢量 SVG，可导出 300DPI PNG/TIFF 与矢量 PDF，中文标注完备，版权归使用者。
version: 1.2.0
author: 王睿
display_name: 王睿·医学专业绘图
category: 科研学术
platforms: WorkBuddy
license: 免费使用（可自由用于论文、教学与商业用途）
keywords: 医学绘图, 生物医学插图, 信号通路图, SCI配图, 机制图, 细胞结构图, 组织学, 胚胎学, 实验流程图, 科研绘图
agent_created: true
---

# Medical Illustration — 医学专业绘图

## 用途

用原创 SVG 组件库生成科研级生物医学示意图：细胞/亚细胞结构、分子机制与信号通路、组织学与胚胎学示意、实验流程、基因工程等。输出 SVG（可在 Illustrator/Inkscape 继续编辑）、矢量 PDF、300DPI PNG/TIFF。

## 包结构（全部随包附带，均为相对本 SKILL.md 的路径）

```
medical-illustration/
├── SKILL.md                          # 本文件
├── scripts/
│   ├── bio_graphics.py               # 核心绘图库：百余个原创组件 + Canvas + 导出管线
│   └── make_figure.py                # JSON spec 命令行出图工具
├── references/                       # 绘图规范与科学准确性参考
│   ├── taxonomy.md                   # 元素盘点清单 + 八类科研图构图
│   ├── figure-standards.md           # 期刊分辨率/配色规范 + 版权指引
│   └── conventions.md                # 箭头语义、组织胚胎学配色惯例
├── assets/templates/                 # 3 个参数化模板脚本
└── assets/examples/                  # 可直接运行的完整示例
    ├── *.py / *.svg / *.png          # 细胞结构、凋亡通路、病原体一图流等
    └── disciplines/                  # 26 个学科方向标杆示例（每个 = .py + .svg + .png）
                                       # 包内 PNG 为预览分辨率，运行对应 .py 可随时重出 300DPI 原图
                                       # 索引见下方「学科示例图索引」或 disciplines/README.md
```

## 环境

- Python 3.9+，依赖：`svglib`、`reportlab`、`pypdfium2`、`pillow`（渲染管线：SVG → svglib/reportlab 矢量 PDF → pypdfium2 光栅化 PNG/TIFF）
- 中文字体：SimHei（Windows 系统自带，库自动注册；Linux/Mac 需安装黑体类字体）
- WorkBuddy 本机部署时的依赖安装坑位与修复命令，见 `references/env-setup-notes.md`

## 工作流

1. **明确图的内容**：主题、要展示的机制/结构、标注语言（中文/英文）、目标用途（论文/教学/PPT）。
2. **盘点元素**：读 `references/taxonomy.md` 的检查清单，列出所有参与者、区室、事件链、调控关系。
3. **写绘图脚本**：import `bio_graphics`（位于本技能包 `scripts/` 目录），用 Canvas 组合组件。优先写 Python 脚本（比 JSON spec 更灵活）：

```python
import sys, pathlib
# 将 <技能包目录>/scripts 加入 sys.path（技能包目录 = 本 SKILL.md 所在目录）
sys.path.insert(0, str(pathlib.Path.home() / ".workbuddy" / "skills" / "medical-illustration" / "scripts"))
# 若技能包安装在其他位置，改为：sys.path.insert(0, r"<技能包目录>/scripts")
from bio_graphics import Canvas, C, leader_label

c = Canvas(1400, 1000)
c.title("图1 细胞凋亡信号通路", size=30)
c.add("membrane_boundary", 700, 520, w=1200, h=820, fill="#F4FAFE")   # 细胞边界
c.add("receptor_tmembrane", 300, 180, label="受体")                    # 库组件
c.add("mitochondrion", 800, 260, w=180, h=100, label="线粒体")
c.add("protein_blob", 500, 400, r=28, label="Caspase-9", shape="square")
c.arrow(300, 240, 300, 360, kind="activation")                         # 激活箭头
c.arrow(760, 320, 540, 380, kind="inhibition", label="抑制")           # 抑制箭头
c.raw(leader_label(430, 470, 620, 260, "核仁"))                        # 引线标注
c.add("legend_row", 120, 940, items=[(C["red_l"], "促凋亡"), (C["green_l"], "抗凋亡")], size=15)
c.save("fig1.svg")
c.export("fig1", formats=("png", "pdf"), dpi=300)
```

4. **导出**：`c.export(stem, formats=("svg","png","pdf","tiff"), dpi=300)`；论文用 PDF+300DPI TIFF，教学用 PNG。
5. **自检**（生成后必须检查）：中文是否正常渲染（粗体中文已由库自动处理为伪粗体）、标注是否压住图形、箭头语义是否正确、图例是否齐全。

## 组件速查

完整组件列表（含参数签名）：在本技能包目录下运行
`python scripts/bio_graphics.py`

分组概览：
- **亚细胞**: nucleus, nucleolus, mitochondrion, rough_er, smooth_er, golgi, lysosome, peroxisome, ribosome, centriole, vesicle, autophagosome, chloroplast, cytoskeleton, membrane_patch, cell_generic, membrane_boundary
- **核酸**: dna_helix, dna_linear, mrna, trna, plasmid, chromosome, nucleosome, gene_cassette
- **蛋白**: protein_blob(circle/square/triangle/hexagon/crescent), receptor_tmembrane, gpcr, ion_channel, antibody_igg, enzyme_lock_key, proteasome, ubiquitin_tag, phosphate, atp_adp, ion_dot
- **细胞**: cell_epithelial, fibroblast, adipocyte, macrophage, neutrophil, lymphocyte, rbc, platelet, neuron, muscle_fiber, sperm, oocyte, blastocyst, cancer_cell, bacterium, virus_enveloped, virus_icosa, bacteriophage
- **寄生虫与病原(节肢动物)**: mite(螨虫), tick(硬蜱, engorged=饱血), flea(跳蚤), mosquito(蚊子)
- **寄生虫与病原(蠕虫)**: roundworm(蛔虫), tapeworm(绦虫), schistosome(血吸虫雌雄合抱)
- **寄生虫与病原(原虫)**: plasmodium_rbc(疟原虫红内期环状体), giardia(贾第鞭毛虫), amoeba(阿米巴)
- **真菌与细菌**: yeast(出芽酵母), aspergillus(曲霉孢子头), staphylococcus(葡萄球菌串), streptococcus(链球菌链), spirochete(螺旋体)
- **组织器官**: skin_section, villus, alveolus, nephron, organ_heart, organ_brain
- **实验室**: microtube, petri_dish, culture_flask, well_plate, syringe, gel_lanes, microscope, mouse_lab, human_silhouette, tube_rack
- **图解**: arrow(kind=activation|inhibition|translocation|bidirectional, curve), leader_label, legend_row, group_box, panel_letter, step_badge, scale_bar, text, rect, circle, path

也可以用命令行跑 JSON spec：
`python make_figure.py spec.json -o out/fig1 --dpi 300 --format png,pdf`

## 深入参考（按需加载）

- `references/taxonomy.md` — 绘图前元素盘点清单、八类科研图的典型构图
- `references/figure-standards.md` — 期刊分辨率/画布/字体/配色规范、**版权与引用指引**
- `references/conventions.md` — 科学准确性画法要点、箭头语义、组织学与胚胎学配色惯例
- `assets/examples/` — 可直接改写的完整示例脚本与成图
- `assets/examples/disciplines/` — **26 个学科方向的标杆示例图**（见下方索引）
- `assets/templates/` — 常见图型的参数化模板脚本

## 学科示例图索引（assets/examples/disciplines/）

每个条目 = 同名 .py 绘图脚本 + .svg 矢量源 + .png（300DPI）。研究生可直接打开对应 .py 改数据/文字复用。

| 学科方向 | 示例文件 |
|---|---|
| 分子生物 / 基础医学（中心法则） | central_dogma |
| 病毒 / 微生物 | virus_replication_cycle（另见 parasite_microbe_sheet） |
| Meta 分析 | meta_forest_plot |
| 单细胞测序 | scrna_workflow |
| 空间转录组 | spatial_transcriptomics |
| WGCNA | wgcna_modules |
| 孟德尔随机化 | mendelian_randomization |
| 中医妇科 | tcm_gynecology_axis |
| 西医妇产（月经周期） | menstrual_cycle |
| 子痫前期单细胞 | preeclampsia_scrna |
| 内科（T2D 机制） | t2d_mechanism |
| 超声医学 | ultrasound_principle |
| 口腔 | tooth_structure_caries |
| 基础医学（炎症） | acute_inflammation（另见 central_dogma） |
| 分子机制 · 小鼠实验 | mouse_experiment_design |
| 临床检验诊断 | elisa_sandwich |
| 核医学 | pet_ct_principle |
| 头颈部肿瘤 / 免疫治疗 | immune_checkpoint |
| 肿瘤（转移 / EMT） | cancer_metastasis_emt |
| 肺癌 / 呼吸 | lung_cancer_pathogenesis |
| 药物制剂 | liposome_nanomedicine |
| 生物医药（ADC） | adc_biopharma |
| 血液肿瘤（CAR-T） | car_t_therapy |
| 脑神经 / 蛋白（阿尔茨海默） | alzheimers_mechanism |
| 植物化妆品 · 天麻 | gastrodin_cosmetics |
| 骨科 | fracture_healing |

**用法学**：先找同学科示例图 → 打开其 .py → 保留版式骨架，替换组件/文字/数据 → `c.export()` 重出图。跨学科组合时优先借用布局最接近的两张图拼接。

## 硬约束（svglib 渲染器限制）

生成 SVG 时禁止使用：`<filter>`（阴影等）、CSS `<style>` 块、`textPath`、`mask`。渐变仅用基础 linearGradient/radialGradient，且 **radialGradient 的 stop-opacity 不生效（会渲染成实心）**。**透明度属性 opacity / fill-opacity 在导出位图时同样不可靠**——需要层次感时一律用实色近似（浅色底 + 深色描边），不要依赖半透明叠加。文本一律用库的 `text_el()`（自动处理中文字体）。

## 字形与渲染坑位（实测）

- **SimHei 无 U+207A（⁺ 上标加号）与 U+00B2（² 上标平方）**：reportlab 渲染为方框"□"。文本中的 "CD8⁺/CD4⁺" 一律写成 "CD8+/CD4+"，"I²" 一律写成 "I2"。希腊字母 γ/α、→、·、–、—、Ⅰ/Ⅱ、～ 在 SimHei 中正常。
- **纯 ASCII 字符串 + font="SimHei" + bold=True 会退化**（无 SimHei-Bold）：需要伪粗体时手写 `stroke=同文字色, stroke-width≈0.9, paint-order="stroke"`。
- **text_el 的 halo 参数是宽度数值**（描边色默认白色，可用 `halo_color` 自定义；旧版曾把宽度值误用作描边色导致 svglib 报 "Can't handle color"，已修复，现在可放心对任意文本使用 halo）。
- **svglib 光栅化实际缩放 ≈0.75×**：dpi=300 时输出宽 ≈ 画布宽×3.125（而非 ×4.17）。1780px 画布 → 5563px 宽 PNG，已满足期刊 300DPI；需更高分辨率直接调大 dpi。
- **group_box 的 label 画在框上方 -h/2-12**，与进入框的箭头或相邻文本易重叠：复杂版式建议不加 label，改为在框内顶部自绘标题。
- **group_box / 大多数面板组件以 (x, y) 为中心锚点**（非左上角）：面板跨度 = x±w/2、y±h/2。版式前先算好边界，面板内文字同样以中心坐标排布，否则会整体偏出画布。
- **arrow 的 curve 参数弧度远超像素直觉**（curve=40 即可甩出半个画布的大弧）：跨区连线一律用直线（不传 curve），需要弧线时先用 curve≤15 试渲染。
- **自检流程**：出图后必做——① PIL 缩略图整体看布局；② 每个区域局部裁剪放大，查文字重叠与缺字形（方框）；③ 检查箭头语义（实线=激活、T型=抑制、虚线=易位）。

## 版权红线

- 本库所有图形为代码原创（含 v1.1.0 新增的 15 个寄生虫与微生物组件，成图见 `assets/examples/parasite_microbe_sheet.*`，复现脚本 `build_parasite_sheet.py`；v1.2.0 新增 26 个学科方向标杆示例图及其绘图脚本），用户可自由使用（含商用）。
- **禁止**将 BioGDP/BioRender 等第三方平台的素材批量下载、转存进本技能——超出其授权范围（BioGDP 学术免费但禁止商用、需引用其论文并导出授权文件；详见 `references/figure-standards.md`）。
- 用户自有版权素材可放 `assets/` 使用。
