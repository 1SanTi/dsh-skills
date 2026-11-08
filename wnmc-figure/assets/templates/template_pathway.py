# -*- coding: utf-8 -*-
"""模板: 信号通路图 (信号从膜上受体 → 胞质级联 → 核内效应)

用法: 改 RECEPTOR/CASCADE/NUCLEUS_EFFECT 配置即可复用整张图的布局逻辑。
"""
import sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C, leader_label

# ---- 配置区: 按你的通路改这里 ----
TITLE = "受体介导的信号转导通路"
RECEPTOR = ("receptor_tmembrane", "膜受体")          # 膜上起点
CASCADE = [("Ras", "circle"), ("Raf", "square"), ("MEK", "square"), ("ERK", "square")]  # 级联(胞质)
TRANSDUCER = ("gpcr", "G 蛋白偶联")                  # 可选中间体, None 则跳过
NUCLEUS_EFFECT = ["转录因子活化", "靶基因表达"]        # 核内效应
INHIBITOR = ("抑制蛋白", "from_cascade0")            # (名称, 抑制哪一级: from_cascadeN)
# ---------------------------------

W, H = 1500, 950
c = Canvas(W, H)
c.title(TITLE, size=30)

X_R, Y_R = 250, 250
c.add(RECEPTOR[0], X_R, Y_R, label=RECEPTOR[1])

# 级联: 沿水平排布, activation 箭头相连
x0, y0, dx = 500, 400, 240
names, shapes = zip(*CASCADE)
for i, (nm, sh) in enumerate(CASCADE):
    c.add("protein_blob", x0 + i * dx, y0, r=34, label=nm, shape=sh,
          fill=C["orange_l"] if i < len(CASCADE) - 1 else C["red_l"])
    if i:
        c.arrow(x0 + i * dx - 84, y0, x0 + i * dx - 44, y0, kind="activation")

# 受体 -> 第一级
c.arrow(X_R + 60, Y_R + 90, x0 - 90, y0 - 40, kind="activation", curve=0.3)

# 中间体
if TRANSDUCER:
    c.add(TRANSDUCER[0], X_R, Y_R + 200, label=TRANSDUCER[1])
    c.arrow(X_R, Y_R + 250, x0 - 90, y0 + 20, kind="activation", curve=-0.25, dash="6 4")

# 入核: 最后一级 -> 细胞核
nx, ny = x0 + (len(CASCADE) - 1) * dx, 700
c.add("nucleus", nx, ny, r=130, label="细胞核", nucleolus=False)
c.arrow(nx, y0 + 40, nx, ny - 136, kind="translocation", label="入核")

# 核内效应
for k, eff in enumerate(NUCLEUS_EFFECT):
    c.add("gene_cassette", nx - 100, ny - 55 + k * 95, w=200,
          gene=eff, label=None)
c.raw(leader_label(nx + 60, ny + 60, nx + 190, ny - 100, "基因表达调控"))

# 抑制剂
if INHIBITOR:
    ix, iy = x0 - 120, y0 - 220
    c.add("protein_blob", ix, iy, r=26, label=INHIBITOR[0], fill=C["green_l"])
    tx = x0 + {"from_cascade0": 0, "from_cascade1": dx, "from_cascade2": 2 * dx,
               "from_cascade3": 3 * dx}[INHIBITOR[1]]
    c.arrow(ix + 34, iy + 20, tx - 40, y0 - 46, kind="inhibition", curve=-0.2)

c.add("legend_row", 120, H - 60,
      items=[(C["orange_l"], "级联激酶"), (C["red_l"], "终末效应激酶"),
             (C["green_l"], "抑制因子")], size=15)
c.export(r"OUTPUT_PATH", formats=("png", "pdf"), dpi=300)  # 改成你的输出路径
print("done")
