# -*- coding: utf-8 -*-
"""植物来源功效原料：天麻素提取-透皮-护肤机制（中心锚点版）"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C, leader_label

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1400, 1000)
c.title("天麻活性成分（天麻素）护肤功效机制", size=29)

# ---------- 左：植物原料 ----------
c.add("group_box", 300, 330, w=360, h=420, label=None, color=C["green"], fill="#F7FBF5")
c.text(300, 158, "① 植物原料", size=15, bold=True)
c.line(300, 470, 300, 250, color=C["green"], width=5)
c.circle(300, 240, 15, fill=C["yellow_l"], stroke=C["orange"], width=1.8)
for i in range(4):
    c.circle(286 + (i % 2) * 28, 280 + i * 42, 9, fill="#FBF0C8", stroke=C["orange"], width=1.2)
c.path("M 262 500 Q 300 462 338 500 Q 328 536 300 532 Q 272 536 262 500 Z",
       fill="#E8D5A8", stroke="#A8873C", width=2.2)
c.text(300, 560, "天麻块茎（Gastrodia elata）", size=12.5, bold=True)
c.arrow(492, 330, 558, 330, kind="activation", label="醇提")

# ---------- 中：提取纯化 ----------
c.add("group_box", 700, 330, w=260, h=420, label=None, color=C["teal"], fill="#F3FAF9")
c.text(700, 158, "② 提取纯化", size=15, bold=True)
c.add("microtube", 648, 275, h=74, label=None)
c.add("culture_flask", 762, 285, w=84, h=56, label=None)
c.text(700, 375, "对羟基苯甲醇葡萄糖苷", size=11, fill=C["gray"])
c.text(700, 405, "HPLC 纯度 ≥ 98%", size=12, bold=True)
c.add("protein_blob", 700, 460, r=22, shape="hexagon", fill=C["teal_l"], label=None)
c.text(700, 508, "天麻素 Gastrodin", size=13, bold=True, fill=C["teal"])
c.arrow(842, 330, 908, 330, kind="activation", label="透皮")

# ---------- 右：皮肤作用 ----------
c.add("group_box", 1150, 330, w=360, h=420, label=None, color=C["orange"], fill="#FEF8F4")
c.text(1150, 158, "③ 皮肤层面作用", size=15, bold=True)
SKX, SKW = 975, 340
ly = 195
for name, col, hh in [("角质层", "#F5E0C8", 26), ("颗粒层", "#F7E7D4", 24),
                      ("棘层", "#FBEFD9", 40), ("基底层", "#F9E6C8", 32)]:
    c.rect(SKX, ly, SKW, hh, fill=col, stroke="#C8A088", width=1.2)
    c.text(SKX + SKW + 10, ly + hh / 2 + 5, name, size=11, anchor="start")
    ly += hh
c.rect(SKX, ly, SKW, 155, fill="#F6DFE0", stroke="#C8A088", width=1.2)
c.text(SKX + SKW + 10, ly + 75, "真皮层", size=11, anchor="start")
c.add("fibroblast", 1070, ly + 70, w=66, h=38, label=None)
c.path(f"M {SKX+150} {ly+55} q 35 22 70 0", stroke="#E8B4B8", width=3)
c.path(f"M {SKX+145} {ly+95} q 45 28 90 0", stroke="#E8B4B8", width=3)
c.text(SKX + SKW - 12, ly + 18, "胶原合成↑", size=11.5, bold=True, anchor="end", fill=C["red"])
c.arrow(1150, 162, 1150, 192, kind="translocation", width=2.2)
c.add("step_badge", 1190, 178, n=3, r=10)

# ---------- 底：功效三卡 ----------
cards = [("抗氧化", ["清除 ROS / 自由基", "激活 Nrf2 / HO-1", "抑制 UV 诱导氧化损伤"], C["orange"], "#FEF8F4"),
         ("抗炎舒缓", ["抑制 NF-κB 通路", "降低 IL-6 / TNF-α", "缓解敏感肌泛红刺痛"], C["red"], "#FDF5F6"),
         ("屏障修护", ["促进神经酰胺合成", "FLG 表达↑ 屏障强化", "经皮失水率 TEWL↓"], C["teal"], "#F3FAF9")]
for i, (t, lines, col, fillc) in enumerate(cards):
    bx = 320 + i * 380
    c.add("group_box", bx, 760, w=340, h=200, label=None, color=col, fill=fillc)
    c.text(bx, 682, t, size=15, bold=True, fill=col)
    for j, s in enumerate(lines):
        c.text(bx, 735 + j * 42, "· " + s, size=12.5)

c.add("legend_row", 200, 925, items=[(C["teal_l"], "天麻素"), ("#F5E0C8", "角质层"),
                                     ("#F6DFE0", "真皮")], size=13.5)
c.text(700, 955, "宣称依据：体外功效实验 + 人体功效评价（化妆品功效宣称评价规范）",
       size=12, fill=C["gray"])

c.save(os.path.join(OUT, "gastrodin_cosmetics.svg"))
c.export(os.path.join(OUT, "gastrodin_cosmetics"), formats=("png",), dpi=300)
print("gastrodin done")
