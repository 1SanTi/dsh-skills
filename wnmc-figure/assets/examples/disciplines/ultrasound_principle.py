# -*- coding: utf-8 -*-
"""超声医学：成像原理与典型图像"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1400, 1000)
c.title("超声成像原理与超声图像构成", size=30)

# ---------- 左：探头与声束 ----------
PX, PY = 300, 240
# 探头
c.path(f"M {PX-90} {PY} L {PX+90} {PY} L {PX+60} {PY+46} L {PX-60} {PY+46} Z",
       fill="#DDE7F2", stroke=C["ink"], width=2.0)
c.text(PX, PY - 16, "超声探头（压电晶片）", size=14, bold=True)
for i in range(7):
    c.rect(PX - 66 + i * 20, PY + 6, 14, 18, fill=C["blue"], stroke=C["ink"], width=0.8)
# 声束
for i in range(5):
    x0 = PX - 70 + i * 35
    c.line(x0, PY + 50, PX - 30 + i * 18, PY + 200, color=C["blue"], width=1.4, dash="6 4")
    c.arrow(x0, PY + 200, x0, PY + 90, kind="activation", color=C["orange"], width=1.2, head_size=6)
c.text(PX, PY + 230, "发射声波（蓝） / 接收回波（橙）", size=12.5, fill=C["gray"])

# 组织分层（回波界面）
layers = [("皮肤/皮下脂肪", "#FBEFD3", 36), ("肌肉筋膜", "#DDEEDB", 26),
          ("实质脏器（肝）", "#F9DCDE", 70), ("深层组织", "#E5E7EB", 40)]
ly = PY + 260
for name, col, hh in layers:
    c.rect(180, ly, 740, hh, fill=col, stroke=C["gray"], width=1.2)
    c.text(935, ly + hh/2 + 5, name, size=13, anchor="start")
    ly += hh + 14
c.text(590, ly + 26, "声阻抗差异界面 → 反射回波形成图像", size=13.5, fill=C["gray"])

# ---------- 右上：B-mode 图 ----------
c.rect(1080, 220, 260, 320, fill="#0F0F0F", stroke=C["gray"], width=2.0)
c.text(1210, 204, "B 型灰阶图", size=14, bold=True)
# 灰阶纹理
import math, random
random.seed(3)
for i in range(90):
    x = 1090 + random.random() * 240
    y = 232 + random.random() * 290
    v = random.random()
    g = int(40 + v * 190)
    c.circle(x, y, 4 + random.random() * 7, fill=f"#{g:02x}{g:02x}{g:02x}")
# 无回声囊肿
c.circle(1210, 380, 34, fill="#101010", stroke="#5a5a5a", width=2.0)
c.text(1092, 528, "低回声 = 暗（液性）", size=11.5, fill="#FFFFFF", anchor="start")
# 灰阶条
for i in range(16):
    g = 30 + i * 13
    c.rect(1080 + i * 16.25, 546, 16.25, 14, fill=f"#{g:02x}{g:02x}{g:02x}")

# ---------- 右下：彩色多普勒 ----------
c.rect(1080, 620, 260, 200, fill="#0F0F0F", stroke=C["gray"], width=2.0)
c.text(1210, 604, "彩色多普勒（血流）", size=14, bold=True)
c.path(f"M 1080 720 Q 1210 660 1340 720", stroke="#444444", width=3.0)
c.path(f"M 1080 740 Q 1210 800 1340 740", stroke="#444444", width=3.0)
for i in range(9):
    xx = 1100 + i * 16
    c.arrow(xx, 728, xx + 12, 726, kind="activation", color="#D64550", width=2.0, head_size=6)
for i in range(5):
    xx = 1200 + i * 16
    c.arrow(xx, 745, xx - 12, 752, kind="activation", color="#2A6FBF", width=2.0, head_size=6)
c.text(1090, 655, "朝向探头 = 红", size=11.5, fill="#FF9A9A", anchor="start")
c.text(1340, 655, "背离探头 = 蓝", size=11.5, fill="#9AC2FF", anchor="end")

# 底部要点
c.add("legend_row", 180, 950, items=[
    (C["blue"], "入射声束"), (C["orange"], "反射回波"),
    ("#D64550", "正向血流"), ("#2A6FBF", "反向血流")], size=14)

c.save(os.path.join(OUT, "ultrasound_principle.svg"))
c.export(os.path.join(OUT, "ultrasound_principle"), formats=("png",), dpi=300)
print("ultrasound done")
