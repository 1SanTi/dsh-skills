# 生物医学绘图分类体系与配图检查清单

> 参考学术平台 Generic Diagramming Platform (GDP, BioGDP.com) 的分类思想（Nucleic Acids Research, 2025, PMID 39470721）整理而成，用于在绘图前系统化盘点"这幅图需要哪些图形元素"。仅借鉴分类方法学，不含其任何素材。

## 十大素材大类

| 大类 | 包含元素 | 本技能组件 |
|---|---|---|
| 亚细胞结构 | 细胞器、膜系统、细胞骨架 | nucleus, mitochondrion, golgi, rough_er, smooth_er, lysosome, peroxisome, ribosome, centriole, vesicle, autophagosome, chloroplast, cytoskeleton, membrane_patch |
| 核酸 | DNA/RNA/质粒/染色体 | dna_helix, dna_linear, mrna, trna, plasmid, chromosome, nucleosome, gene_cassette |
| 蛋白 | 受体、酶、抗体、信号分子 | protein_blob, receptor_tmembrane, gpcr, ion_channel, antibody_igg, enzyme_lock_key, proteasome, ubiquitin_tag, phosphate, atp_adp |
| 化合物 | 小分子、离子、药物 | ion_dot, atp_adp（其余用 protein_blob 自定义形状/颜色表示） |
| 细胞 | 血细胞、免疫细胞、干细胞、生殖细胞、病原 | cell_generic, cell_epithelial, fibroblast, adipocyte, macrophage, neutrophil, lymphocyte, rbc, platelet, neuron, muscle_fiber, sperm, oocyte, blastocyst, cancer_cell, bacterium, virus_enveloped, virus_icosa, bacteriophage |
| 组织和器官 | 组织切片、器官示意 | skin_section, villus, alveolus, nephron, organ_heart, organ_brain |
| 物种 | 模式动物、人 | mouse_lab, human_silhouette |
| 实验室 | 器材、耗材、实验流程 | microtube, petri_dish, culture_flask, well_plate, syringe, gel_lanes, microscope, tube_rack |
| 地球和生态 | 环境、生态因素 | 暂缺，可用 rect/circle/path 自绘 |
| 其他 | 通用图解元素 | arrow, group_box, leader_label, legend_row, panel_letter, step_badge, scale_bar, membrane_boundary, text |

## 配图前检查清单（避免漏画元素）

绘制机制图/流程图前，逐项自问：

1. **参与者**：有哪些分子/细胞器/细胞/器官？（每个都要有图形+名称标注）
2. **定位**：发生在哪个区室？（细胞膜/细胞质/核/线粒体——用 membrane_boundary 或 group_box 划分区室）
3. **事件链**：谁激活谁、谁抑制谁？（箭头语义必须正确：实线箭头=激活，T 型=抑制，虚线=易位/间接）
4. **分子状态变化**：磷酸化、泛素化、剪切、二聚？（用 phosphate/ubiquitin_tag 标记）
5. **方向性**：入核、分泌、内吞？（箭头要穿越膜边界并可见）
6. **调控反馈**：正/负反馈回路？（用弯曲箭头 curve 参数画闭环）
7. **对比条件**：正常 vs 处理组？（左右分栏 + panel_letter A/B）
8. **图例**：颜色/形状含义是否需要说明？（legend_row）
9. **标题与编号**：图题、panel 字母、步骤序号（step_badge）
10. **比例尺**：形态学图是否需要？（scale_bar）

## 常见科研图类型 → 推荐构图

| 图类型 | 典型布局 |
|---|---|
| 信号通路图 | 左右流向，受体在膜上→胞质激酶级联→核内转录因子；激活/抑制箭头+图例 |
| 分子互作图 | 中心蛋白+周围伙伴蛋白，用 binding/双向箭头 |
| 实验流程图 | 箭头串联：动物/样本 → 处理 → 检测 → 分析（syringe/mouse_lab/tube_rack/gel_lanes） |
| 细胞死亡机制 | 细胞轮廓内画细胞器事件，外侧画配体-受体 |
| 组织学示意 | 分层结构 + leader_label 引线标注各层 |
| 胚胎发育系列 | 时间轴 + step_badge，各阶段图形并排 |
| 基因工程流程 | gene_cassette/plasmid → 载体 → 转染 → 表达检测 |
| 实验结果示意（非数据图） | gel_lanes 模拟电泳/印迹排布，配合 group_box 分组 |
