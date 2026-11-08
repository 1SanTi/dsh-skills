# -*- coding: utf-8 -*-
"""口腔医学：牙体结构与龋病进展四阶段"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C, leader_label

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1400, 1000)
c.title("牙体解剖结构与龋病进展", size=30)

# ---------- 左：牙体剖面 ----------
TX, TY = 330, 500   # 牙冠中心

def tooth(x, y, s=1.0, crown=None, dentin=None, lesion=None, root_col="#FDFDFD"):
    """简化磨牙剖面: x,y 为牙冠中心; s 缩放"""
    W, H = 150 * s, 120 * s
    RW, RH = 34 * s, 130 * s
    # 牙根（两根）
    c.path(f"M {x-W*0.42} {y+H*0.5} L {x-RW*1.6} {y+H*0.5+RH} Q {x-RW*1.1} {y+H*0.5+RH*1.12} {x-RW*0.75} {y+H*0.5+RH*0.92} L {x-W*0.12} {y+H*0.5} Z",
           fill=root_col, stroke=C["ink"], width=1.8)
    c.path(f"M {x+W*0.42} {y+H*0.5} L {x+RW*1.6} {y+H*0.5+RH} Q {x+RW*1.1} {y+H*0.5+RH*1.12} {x+RW*0.75} {y+H*0.5+RH*0.92} L {x+W*0.12} {y+H*0.5} Z",
           fill=root_col, stroke=C["ink"], width=1.8)
    # 牙本质
    c.path(f"M {x-W*0.46} {y+H*0.5} Q {x-W*0.5} {y-H*0.62} {x-W*0.22} {y-H*0.52} L {x-W*0.1} {y-H*0.1} L {x+W*0.1} {y-H*0.1} L {x+W*0.22} {y-H*0.52} Q {x+W*0.5} {y-H*0.62} {x+W*0.46} {y+H*0.5} Z",
           fill=dentin or "#F6E3C5", stroke=C["ink"], width=1.8)
    # 牙釉质（冠部外层）
    c.path(f"M {x-W*0.48} {y+H*0.28} Q {x-W*0.56} {y-H*0.72} {x-W*0.2} {y-H*0.62} Q {x} {y-H*0.7} {x+W*0.2} {y-H*0.62} Q {x+W*0.56} {y-H*0.72} {x+W*0.48} {y+H*0.28} Q {x+W*0.2} {y+H*0.36} {x-W*0.2} {y+H*0.36} Z",
           fill=crown or "#FFFFFF", stroke=C["ink"], width=1.8)
    # 牙髓腔
    c.path(f"M {x-W*0.16} {y+H*0.42} L {x-W*0.07} {y-H*0.28} L {x+W*0.07} {y-H*0.28} L {x+W*0.16} {y+H*0.42} Z",
           fill="#F9B8B0", stroke=C["red"], width=1.4)
    if lesion:
        c.circle(x - W*0.30, y - H*0.45, 13 * s, fill=lesion)

tooth(TX, TY)
c.raw(leader_label(TX - 52, TY - 62, 120, 300, "牙釉质", size=14, bold=True))
c.raw(leader_label(TX - 20, TY - 30, 120, 400, "牙本质", size=14, bold=True))
c.raw(leader_label(TX, TY + 30, 160, 560, "牙髓（神经血管）", size=14, bold=True))
c.raw(leader_label(TX - 45, TY + 175, 150, 760, "牙根 / 根管", size=14, bold=True))
# 牙龈与牙槽骨
c.rect(80, TY + 92, 520, 22, fill="#F7A8A0")
c.text(560, TY + 106, "牙龈", size=13, anchor="start")
c.rect(80, TY + 116, 520, 110, fill="#F3E4D2")
c.text(560, TY + 175, "牙槽骨", size=13, anchor="start")

# ---------- 右：龋病进展 ----------
stages = [("健康牙", None), ("釉质龋", "#D8CFC4"), ("牙本质龋", "#A89B8A"), ("牙髓炎", "#7A6A58")]
for i, (name, col) in enumerate(stages):
    x = 800 + (i % 2) * 250
    y = 300 + (i // 2) * 300
    tooth(x, y, s=0.72, lesion=col)
    c.text(x, y + 175, name, size=14, bold=True)
    c.add("step_badge", x - 95, y - 95, n=i + 1)
c.arrow(930, 300, 960, 300, kind="activation")
c.arrow(1050, 430, 1050, 470, kind="activation")
c.arrow(930, 600, 960, 600, kind="activation")
c.text(1050, 120, "龋病由浅入深：釉质 → 牙本质 → 牙髓", size=15, bold=True)
c.text(1050, 152, "深龋未治 → 牙髓感染、根尖周炎", size=13, fill=C["gray"])

c.add("legend_row", 130, 950, items=[
    ("#FFFFFF", "牙釉质（最硬）"), ("#F6E3C5", "牙本质"), ("#F9B8B0", "牙髓"),
    ("#F7A8A0", "牙龈"), ("#F3E4D2", "牙槽骨")], size=13)

c.save(os.path.join(OUT, "tooth_structure_caries.svg"))
c.export(os.path.join(OUT, "tooth_structure_caries"), formats=("png",), dpi=300)
print("tooth done")
