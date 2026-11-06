# -*- coding: utf-8 -*-
"""孟德尔随机化：设计框架与三大核心假设（中心锚点版）"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1400, 950)
c.title("孟德尔随机化（MR）：利用遗传变异推断因果", size=29)

def panel(cx, cy, w, h, color, fill):
    c.add("group_box", cx, cy, w=w, h=h, color=color, fill=fill)
    return cx - w / 2, cy - h / 2

# 工具变量 SNP 群
x0, y0 = panel(280, 420, 290, 300, C["blue"], "#F4F9FE")
c.text(280, y0 - 16, "遗传工具变量", size=15, bold=True)
for i, rs in enumerate(["rs10861", "rs4712", "rs2981", "rs7903146"]):
    c.circle(245, 330 + i * 52, 11, fill=C["blue_l"], stroke=C["blue"], width=1.6)
    c.text(275, 338 + i * 52, rs, size=12.5, anchor="start")

# 暴露
panel(760, 260, 330, 120, C["teal"], "#F3FAF9")
c.text(760, 252, "暴露（Exposure）", size=16, bold=True)
c.text(760, 290, "如：LDL-C、BMI、血压", size=13, fill=C["gray"])

# 结局
panel(760, 640, 330, 120, C["red"], "#FDF5F6")
c.text(760, 632, "结局（Outcome）", size=16, bold=True)
c.text(760, 670, "如：冠心病、骨质疏松", size=13, fill=C["gray"])

# 三条路径
c.arrow(428, 380, 592, 285, kind="activation", label="假设① 关联性")
c.arrow(760, 325, 760, 575, kind="activation", width=3.2, label="因果效应 β（IVW）")
c.arrow(428, 470, 592, 615, kind="translocation", label="假设③ 仅经暴露")

# 混杂因素
panel(1170, 430, 250, 110, C["gray"], "#F7F7F7")
c.text(1170, 422, "混杂因素", size=14, bold=True)
c.text(1170, 452, "年龄 / 饮食等", size=12, fill=C["gray"])
c.arrow(1042, 400, 932, 310, kind="translocation", width=1.8)
c.arrow(1042, 462, 932, 592, kind="translocation", width=1.8)
c.text(990, 375, "假设② 独立于混杂", size=12.5, fill=C["gray"], anchor="start")

# 多效性检验
x0, y0 = panel(1170, 690, 270, 160, C["red"], "#FDF5F6")
c.text(1170, y0 - 16, "多效性与敏感性检验", size=13.5, bold=True)
for i, t in enumerate(["MR-Egger 截距检验", "MR-PRESSO 离群检测", "leave-one-out 留一法"]):
    c.text(x0 + 28, y0 + 45 + i * 32, "· " + t, size=12.5, anchor="start")

# 方法
x0, y0 = panel(260, 800, 400, 170, C["gray"], "#FAFAFA")
c.text(260, y0 - 16, "常用方法", size=13.5, bold=True)
for i, t in enumerate(["IVW（主分析）", "加权中位数 / 加权众数", "MR-Egger（水平多效性稳健）"]):
    c.text(x0 + 30, y0 + 42 + i * 34, "· " + t, size=12.5, anchor="start")

# 数据来源
x0, y0 = panel(760, 800, 400, 170, C["gray"], "#FAFAFA")
c.text(760, y0 - 16, "数据来源（公开数据库）", size=13.5, bold=True)
for i, t in enumerate(["GWAS Catalog / IEU OpenGWAS", "eQTL: GTEx / eQTLGen", "pQTL: deCODE / UKB-PPP"]):
    c.text(x0 + 30, y0 + 42 + i * 34, "· " + t, size=12.5, anchor="start")

c.text(700, 915, "解读：β ≠ 0 且各方法方向一致、敏感性分析稳健 → 支持因果关联",
       size=13.5, bold=True, fill=C["teal"])

c.add("legend_row", 170, 935, items=[
    (C["blue"], "工具变量 SNP"), (C["teal"], "暴露"),
    (C["red"], "结局"), (C["gray"], "虚线 = 不允许的路径")], size=14)

c.save(os.path.join(OUT, "mendelian_randomization.svg"))
c.export(os.path.join(OUT, "mendelian_randomization"), formats=("png",), dpi=300)
print("mr done")
