# 学科示例图索引（disciplines/）

面向各学科研究生的"标杆示例图"：每张图由同名 `.py` 脚本生成，同目录下有 `.svg`（矢量源，可用 AI/Inkscape 继续编辑）和 `.png`（300DPI）。

## 使用方法

1. 找到自己学科的示例图 → 打开同名 `.py` 脚本；
2. 保留版式骨架，替换组件、文字与数据；
3. 运行脚本即可重新导出 SVG + 300DPI PNG（渲染管线与中文字体自动处理）。

## 学科 → 文件对照表

| 学科方向 | 文件名 | 画面内容 |
|---|---|---|
| 分子生物学 | central_dogma | 中心法则（复制/转录/翻译/逆转录） |
| 病毒学 / 微生物学 | virus_replication_cycle | 有包膜病毒侵染复制六步周期 |
| 微生物学（细菌/寄生虫） | ../parasite_microbe_sheet | 15 种病原体一图流（v1.1 自带） |
| Meta 分析 | meta_forest_plot | 森林图（效应量、95%CI、合并菱形） |
| 单细胞测序 | scrna_workflow | 解离→GEM→测序→UMAP 聚类工作流 |
| 空间转录组 | spatial_transcriptomics | Visium 点阵空间表达图 + 分析流程 |
| WGCNA | wgcna_modules | 聚类树 + 模块色带 + 模块-性状热图 |
| 孟德尔随机化 | mendelian_randomization | 三大假设 DAG + 方法/数据库 |
| 中医妇科 | tcm_gynecology_axis | 肾-天癸-冲任-胞宫轴与病机 |
| 西医妇产 | menstrual_cycle | 卵巢周期-激素曲线-子宫内膜三联图 |
| 子痫前期单细胞 | preeclampsia_scrna | 胎盘绒毛结构 + scRNA 研究方案 |
| 内科 | t2d_mechanism | 2 型糖尿病发病机制与并发症 |
| 超声医学 | ultrasound_principle | 成像原理 + B 超/彩色多普勒图 |
| 口腔医学 | tooth_structure_caries | 牙体剖面 + 龋病进展四阶段 |
| 基础医学 | acute_inflammation | 急性炎症：血管渗出与白细胞游出 |
| 分子机制 · 小鼠 | mouse_experiment_design | 敲基因小鼠实验设计全流程 |
| 临床检验诊断 | elisa_sandwich | ELISA 双抗体夹心法 + 检验流程 |
| 核医学 | pet_ct_principle | PET/CT 显像原理（18F-FDG） |
| 头颈部肿瘤 / 免疫治疗 | immune_checkpoint | PD-1/PD-L1 治疗前后双面板 |
| 肿瘤学 | cancer_metastasis_emt | EMT-内渗-循环-外渗-定植 |
| 肺癌 / 呼吸 | lung_cancer_pathogenesis | 气道上皮癌变四阶段 + 驱动基因 |
| 药物制剂 | liposome_nanomedicine | 脂质体结构、体内命运与 EPR |
| 生物医药 | adc_biopharma | ADC 结构、内吞机制、旁观者效应 |
| 血液肿瘤 | car_t_therapy | CAR 结构、制备流程与体内杀伤 |
| 脑神经 / 蛋白 | alzheimers_mechanism | Aβ 级联 + Tau 磷酸化双机制 |
| 植物化妆品（天麻） | gastrodin_cosmetics | 天麻素提取-透皮-护肤功效机制 |
| 骨科 | fracture_healing | 骨折愈合四期 + 骨重建细胞三联 |

## 注意事项

- 所有图形为代码原创，版权归使用者，可自由用于论文、教学与商业。
- 数据均为示意值，发表前请替换为真实实验数据。
- SimHei 字体不含 "⁺" 与 "²"：正文中写 `CD4+`、`I2`，不要用上标字符。
- `_run_all.py` 是批量渲染辅助脚本，`_fix_api.py`、`render_log.txt` 为开发遗留文件，可忽略或删除。
