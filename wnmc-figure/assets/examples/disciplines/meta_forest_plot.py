# -*- coding: utf-8 -*-
"""Meta 分析：森林图（示例数据，可替换为真实效应量）"""
import os, sys, math
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1400, 950)
c.title("Meta 分析森林图（示例：干预组 vs 对照组，结局 OR）", size=28)

# ---- 坐标映射（log10 刻度 0.1~10）----
X0, X1 = 560, 1150
def xpos(or_):
    t = (math.log10(or_) + 1.0) / 2.0
    return X0 + t * (X1 - X0)

TOP, DY = 210, 52
studies = [
    ("Chen 2019",    0.52, 0.28, 0.96, 11.8),
    ("Wang 2020",    0.71, 0.45, 1.12, 14.6),
    ("Liu 2020",     0.44, 0.21, 0.92,  8.9),
    ("Zhang 2021",   0.83, 0.58, 1.19, 18.4),
    ("Park 2021",    0.60, 0.33, 1.09, 10.2),
    ("Smith 2022",   0.38, 0.17, 0.85,  7.5),
    ("Li 2023",      0.66, 0.42, 1.04, 15.3),
    ("Kumar 2024",   0.55, 0.30, 1.01, 13.3),
]

# 列标题
c.text(470, 165, "研究", size=15, bold=True, anchor="end")
c.text(855, 165, "OR (95% CI)", size=15, bold=True)
c.text(1260, 165, "权重", size=15, bold=True)
c.text(1345, 165, "方向", size=15, bold=True)

# 无效应线 OR=1
x_nul = xpos(1.0)
c.line(x_nul, TOP - 22, x_nul, TOP + DY * 9 + 40, color=C["gray"], width=1.6, dash="5 5")
c.text(x_nul, TOP - 8, "无效应线 OR=1", size=11.5, fill=C["gray"])

y = TOP
for name, est, lo, hi, wt in studies:
    c.text(470, y, name, size=14, anchor="end")
    c.line(xpos(lo), y, xpos(hi), y, color=C["ink"], width=2.0)
    for xe in (xpos(lo), xpos(hi)):
        c.line(xe, y - 5, xe, y + 5, color=C["ink"], width=2.0)
    side = 3.5 + wt * 0.16          # 方块大小随权重
    c.rect(xpos(est) - side/2, y - side/2, side, side, fill=C["blue"], stroke=C["ink"], width=1.2)
    c.text(1260, y, f"{wt:.1f}%", size=13)
    c.text(1290, y, "← 利于干预" if est < 1 else "对照 →", size=12,
           fill=C["teal"] if est < 1 else C["red"], anchor="start")
    y += DY

# 亚组合计（随机效应）
c.line(300, y - 6, 470, y - 6, color=C["gray"], width=1.0)
c.text(470, y + 18, "亚组合计 (n=6)", size=14, bold=True, anchor="end")
sub = [s for s in studies[:6]]
lo, hi, est = 0.44, 0.78, 0.59
c.line(xpos(lo), y + 14, xpos(hi), y + 14, color=C["ink"], width=2.0)
c.rect(xpos(est) - 6, y + 14 - 6, 12, 12, fill=C["blue"], stroke=C["ink"], width=1.2)
c.text(1260, y + 18, "86.6%", size=13, bold=True)
y += DY

# 总合并菱形
c.text(470, y + 22, "总合并效应 (IVW)", size=15, bold=True, anchor="end")
lo, hi, est = 0.51, 0.83, 0.65
xl, xh, xe = xpos(lo), xpos(hi), xpos(est)
c.path(f"M {xl} {y+18} L {xe} {y+4} L {xh} {y+18} L {xe} {y+32} Z",
       fill=C["red_l"], stroke=C["red"], width=2.0)
c.text(1260, y + 22, "100%", size=13, bold=True)
c.text(855, y + 52, "合并 OR = 0.65 [0.51, 0.83]，P < 0.001，I2 = 34%", size=14, bold=True)

# 横轴（log 刻度）
axis_y = y + 84
c.line(X0, axis_y, X1, axis_y, color=C["ink"], width=2.0)
for tick in (0.1, 0.2, 0.5, 1, 2, 5, 10):
    xt = xpos(tick)
    c.line(xt, axis_y, xt, axis_y + 7, color=C["ink"], width=1.5)
    c.text(xt, axis_y + 24, str(tick), size=13)
c.text(855, axis_y + 50, "比值比 OR（对数刻度）← 利于干预 | 利于对照 →", size=13, fill=C["gray"])

# 右下备注框（改为轴下注释行，避免遮挡）
c.text(855, axis_y + 76, "注：方块大小 ∝ 权重；菱形 = 合并效应；横线 = 95%CI；I2 > 50% 提示异质性较高",
       size=12, fill=C["gray"])

c.add("legend_row", 300, 905, items=[
    (C["blue"], "单个研究"), (C["red_l"], "合并效应"),
    (C["gray"], "虚线 = 无效应线")], size=14)

c.save(os.path.join(OUT, "meta_forest_plot.svg"))
c.export(os.path.join(OUT, "meta_forest_plot"), formats=("png",), dpi=300)
print("forest done")
