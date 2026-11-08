# -*- coding: utf-8 -*-
"""妇产科 / 单细胞：子痫前期胎盘单细胞研究"""
import os, sys, random, math
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C, leader_label

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)
random.seed(11)

c = Canvas(1450, 1000)
c.title("子痫前期（PE）胎盘单细胞测序研究设计", size=28)

# ---------- 左：胎盘绒毛结构 ----------
c.add("group_box", 370, 385, w=520, h=470, label=None, color=C["red"], fill="#FDF5F6")
c.text(370, 120, "胎盘绒毛（胎盘屏障）", size=15, bold=True)
# 绒毛树干
c.path("M 370 560 Q 340 470 300 420 Q 260 370 270 300", stroke="#C8A088", width=14)
c.path("M 370 560 Q 420 480 470 430 Q 520 380 510 320", stroke="#C8A088", width=10)
c.path("M 300 420 Q 350 380 400 340", stroke="#C8A088", width=8)
# 滋养细胞层（外层）
for (tx, ty) in [(270, 300), (330, 350), (400, 340), (510, 320), (470, 430)]:
    c.circle(tx, ty, 17, fill="#F7C8C0", stroke=C["red"], width=2.0)
# 绒毛内血管
c.circle(280, 310, 9, fill=C["red_l"], stroke=C["red"], width=1.6)
c.circle(420, 350, 9, fill=C["red_l"], stroke=C["red"], width=1.6)
c.circle(500, 330, 8, fill=C["red_l"], stroke=C["red"], width=1.6)
# 母体蜕膜侧
c.rect(110, 590, 520, 30, fill="#F3E4D2")
c.text(370, 640, "蜕膜（母体面）：螺旋动脉重铸障碍 → 灌流不足", size=12.5, fill=C["gray"])
labels = [("CTB 细胞滋养层", 200, 230), ("STB 合体滋养层", 560, 250),
          ("EVT 绒毛外滋养层", 600, 430), ("Hofbauer 巨噬", 240, 450)]
for t, lx, ly in labels:
    pass
c.raw(leader_label(270, 300, 180, 200, "CTB 细胞滋养层", size=12.5, bold=True))
c.raw(leader_label(400, 335, 600, 210, "STB 合体滋养层", size=12.5, bold=True))
c.raw(leader_label(510, 320, 620, 400, "EVT 侵入功能↓", size=12.5, bold=True, color=C["red"]))
c.raw(leader_label(280, 318, 180, 380, "绒毛血管", size=12))

# ---------- 右：scRNA-seq 设计 ----------
c.add("group_box", 1015, 385, w=650, h=470, label=None, color=C["purple"], fill="#F9F7FC")
c.text(1015, 120, "单细胞研究方案", size=15, bold=True)
# 分组
c.text(720, 190, "分组（各 n≥3）", size=13.5, bold=True, anchor="start")
c.rect(720, 210, 26, 26, fill=C["teal_l"], stroke=C["teal"], width=1.4)
c.text(760, 228, "正常胎盘（足月）", size=12.5, anchor="start")
c.rect(720, 250, 26, 26, fill=C["red_l"], stroke=C["red"], width=1.4)
c.text(760, 268, "PE 胎盘（早发/晚发）", size=12.5, anchor="start")
c.arrow(950, 240, 1000, 240, kind="activation", label="解离建库")
c.text(1030, 228, "10x 平台", size=12, anchor="start")
c.text(1030, 254, "≥ 5000 cells/样", size=11.5, anchor="start", fill=C["gray"])
# 主要细胞类型与发现
c.text(720, 320, "主要细胞群与 PE 核心发现", size=13.5, bold=True, anchor="start")
finds = [("EVT：侵袭相关基因（ITGA5/ HLA-G）↓ → 螺旋动脉重铸失败", C["red"]),
         ("CTB → EVT 拟时序受阻，分化轨迹偏移", C["orange"]),
         ("Hofbauer 细胞：抗原提呈与促炎通路↑", C["purple"]),
         ("蜕膜 NK / T 细胞：免疫耐受失衡", C["teal"]),
         ("细胞通讯：EVT-免疫细胞 CXCL/CXCR 通路紊乱", C["blue"])]
for i, (t, col) in enumerate(finds):
    c.rect(725, 350 + i * 46, 18, 18, fill=col)
    c.text(755, 364 + i * 46, t, size=12.3, anchor="start")

# ---------- 底部：临床转化 ----------
c.add("group_box", 725, 760, w=1230, h=180, label=None, color=C["blue"], fill="#F4F9FE")
c.text(725, 640, "向临床转化的落点", size=15, bold=True)
for i, (t, s) in enumerate([
        ("预测标志物", "scRNA 优先基因 → 血浆蛋白（PLGF/sFlt-1 之外的新靶标）"),
        ("干预靶点", "促进 EVT 侵袭 / 恢复免疫耐受的小分子或生物药"),
        ("分型用药", "早发型 vs 晚发型 PE 分子分型 → 精准监测")]):
    bx = 160 + i * 400
    c.text(bx, 700, t, size=13.5, bold=True, anchor="start", fill=C["blue"])
    c.text(bx, 735, s, size=12, anchor="start", fill=C["gray"])
c.text(725, 795, "研究闭环：临床样本 → 单细胞图谱 → 机制发现 → 标志物/靶点验证（qPCR/IHC/血清学）",
       size=12.5, bold=True, anchor="start")

c.add("legend_row", 200, 920, items=[("#F7C8C0", "滋养细胞"), (C["red_l"], "绒毛血管"),
                                     ("#F3E4D2", "蜕膜"), (C["purple_l"], "免疫细胞")], size=13.5)

c.save(os.path.join(OUT, "preeclampsia_scrna.svg"))
c.export(os.path.join(OUT, "preeclampsia_scrna"), formats=("png",), dpi=300)
print("pe done")
