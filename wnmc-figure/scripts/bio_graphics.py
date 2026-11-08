# -*- coding: utf-8 -*-
"""
bio_graphics.py — 原创生物医学 SVG 图形组件库 (Medical Illustration Component Library)

所有图形均为代码生成的原创矢量图形，用户拥有完整版权，可自由用于论文/教学/商业。
渲染管线: SVG(主交付物) -> 矢量 PDF(svglib+reportlab) -> PNG/TIFF(pypdfium2, 300DPI)

约束 (svglib 渲染器限制，生成 SVG 时必须遵守):
  - 不用 <filter> / CSS <style> 块 / textPath / mask —— 仅用元素属性
  - 渐变仅支持 linearGradient / radialGradient(基础用法)
  - 文本字体: 含中文时 font-family="SimHei"，纯西文用 "Helvetica"
"""
from __future__ import annotations
import math, os, re, sys

# ---------------------------------------------------------------- palette
C = {
    "blue": "#3B7DBF", "blue_l": "#D6E8F7",
    "teal": "#2A9D8F", "teal_l": "#D3F0EC",
    "orange": "#E76F51", "orange_l": "#FADCD3",
    "yellow": "#E9C46A", "yellow_l": "#FBEFD3",
    "purple": "#7B5EA7", "purple_l": "#E4DCF2",
    "green": "#5B9E51", "green_l": "#DDEEDB",
    "red": "#D64550", "red_l": "#F9DCDE",
    "gray": "#6B7280", "gray_l": "#E5E7EB",
    "ink": "#1F2937", "paper": "#FFFFFF",
}
DEFAULT_STROKE = "#2F5D7C"
CJK_RE = re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]')
FONT_CJK, FONT_LAT = "SimHei", "Helvetica"


def pick_font(text: str) -> str:
    return FONT_CJK if CJK_RE.search(str(text)) else FONT_LAT


def esc(t) -> str:
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def E(tag: str, **a) -> str:
    """构建 SVG 元素字符串; 值为 None 的属性被跳过, True->空属性"""
    parts = [f"<{tag}"]
    for k, v in a.items():
        k = k.rstrip("_").replace("_", "-")
        if v is None:
            continue
        parts.append(f' {k}="{v.lower() if v is True else v}"')
    return "".join(parts) + "/>"


def text_el(x, y, t, size=16, fill=None, anchor="middle", bold=False,
            font=None, italic=False, halo=None, halo_color=None, letter=None, opacity=None):
    """文本元素。halo=白色描边宽度, 提高在复杂底色上的可读性; halo_color 自定义描边色"""
    font = font or pick_font(t)
    fill = fill or C["ink"]
    is_cjk = bool(CJK_RE.search(str(t)))
    # reportlab 无中文字体的 bold 变体: CJK 用同色细描边模拟加粗, 否则会退化成方块
    weight = "normal" if is_cjk else ("bold" if bold else "normal")
    extra = f' letter-spacing="{letter}"' if letter else ""
    halo_w = halo or 0
    if bold and is_cjk:
        halo_w = max(halo_w, 0.7)
    halo_attr = ""
    if halo_w:
        # CJK 伪加粗用文字本色描边; 普通光晕用白色(或指定色)描边。
        # 注意: 描边颜色绝不能误用 halo 宽度值, 否则 svglib 报 "Can't handle color" 并丢弃描边
        sc = fill if (bold and is_cjk) else (halo_color or "#FFFFFF")
        halo_attr = (f' stroke="{sc}" stroke-width="{halo_w}" '
                     f'stroke-linejoin="round" paint-order="stroke"')
    op = f' opacity="{opacity}"' if opacity is not None else ""
    it = ' font-style="italic"' if italic else ""
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}"'
            f'{it}{extra}{halo_attr}{op}>{esc(t)}</text>')


# ---------------------------------------------------------------- arrow heads
def _head(x, y, ang_deg, size=9, color=None, kind="solid"):
    """在 (x,y) 处按角度 ang 画箭头尖端"""
    a = math.radians(ang_deg)
    color = color or DEFAULT_STROKE
    if kind == "solid":
        p1 = (x - size * math.cos(a) + size * 0.5 * math.sin(a),
              y - size * math.sin(a) - size * 0.5 * math.cos(a))
        p2 = (x - size * math.cos(a) - size * 0.5 * math.sin(a),
              y - size * math.sin(a) + size * 0.5 * math.cos(a))
        return (f'<polygon points="{x:.1f},{y:.1f} {p1[0]:.1f},{p1[1]:.1f} '
                f'{p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>')
    return ""  # 非实心箭头由各自组件自绘


def _line_pts(p1, p2, pad1=0.0, pad2=0.0):
    """返回从 p1 沿方向缩进 pad 后的坐标"""
    x1, y1 = p1; x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    return (x1 + ux * pad1, y1 + uy * pad1), (x2 - ux * pad2, y2 - uy * pad2)


def _stroke_line(p1, p2, color=None, width=2.2, dash=None, cap="round"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" '
            f'y2="{p2[1]:.1f}" stroke="{color or DEFAULT_STROKE}" '
            f'stroke-width="{width}" stroke-linecap="{cap}"{d}/>')


# ================================================================ COMPONENTS
# 每个组件返回以 (0,0) 为锚点的局部 SVG 片段, 由 _loc() 平移到目标位置
def _loc(x, y, inner, scale=None, rotate=None):
    tr = f"translate({x},{y})"
    if rotate:
        tr += f" rotate({rotate})"
    if scale:
        tr += f" scale({scale})"
    return f'<g transform="{tr}">{inner}</g>'


def _bilayer(w, h, color=None, head=C["gray"], tail="#9CA3AF"):
    """磷脂双分子层片段, 局部坐标: 以 (0,0) 为中心, 宽 w 高 h"""
    out, n = [], max(2, int(w / 11))
    for row in (-h / 2 + 4, h / 2 - 4):
        for i in range(n):
            cx = -w / 2 + (i + 0.5) * w / n
            out.append(f'<circle cx="{cx:.1f}" cy="{row:.1f}" r="3.2" fill="{head}"/>')
            ty = row + (3.4 if row < 0 else -3.4)
            out.append(f'<line x1="{cx:.1f}" y1="{row:.1f}" x2="{cx-1.8:.1f}" y2="{ty:.1f}" stroke="{tail}" stroke-width="1.4"/>')
            out.append(f'<line x1="{cx:.1f}" y1="{row:.1f}" x2="{cx+1.8:.1f}" y2="{ty:.1f}" stroke="{tail}" stroke-width="1.4"/>')
    return "".join(out)


# ---- 亚细胞结构 SUBCELLULAR -------------------------------------------------
def nucleus(x, y, r=70, label=None, nucleolus=True, pores=True, fill=None):
    fill = fill or C["blue_l"]
    s = [f'<circle r="{r}" fill="{fill}" stroke="{DEFAULT_STROKE}" stroke-width="3"/>']
    # 双层核膜
    s.append(f'<circle r="{r-6}" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="1.2" stroke-dasharray="4 3"/>')
    if pores:
        for i in range(8):
            a = math.pi * 2 * i / 8 + 0.3
            s.append(f'<circle cx="{(r-3)*math.cos(a):.1f}" cy="{(r-3)*math.sin(a):.1f}" r="3.4" fill="#FFFFFF" stroke="{DEFAULT_STROKE}" stroke-width="1.6"/>')
    if nucleolus:
        s.append(f'<circle cx="{-r*0.22:.1f}" cy="{-r*0.18:.1f}" r="{r*0.3:.1f}" fill="{C["purple"]}" opacity="0.55"/>')
    out = "".join(s)
    if label:
        out += text_el(0, r + 22, label, 17)
    return _loc(x, y, out)


def nucleolus(x, y, r=22, label=None):
    o = f'<circle r="{r}" fill="{C["purple"]}" opacity="0.6" stroke="{C["purple"]}" stroke-width="2"/>'
    if label:
        o += text_el(0, r + 20, label, 15)
    return _loc(x, y, o)


def mitochondrion(x, y, w=130, h=70, label=None, angle=0):
    """线粒体: 外膜 + 内膜 + 嵴"""
    s = [f'<ellipse rx="{w/2}" ry="{h/2}" fill="{C["orange_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.6"/>',
         f'<ellipse rx="{w/2-7}" ry="{h/2-7}" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="1.2"/>']
    n = max(3, int(w / 34))
    for i in range(n):
        cx = -w / 2 + 22 + i * (w - 44) / max(1, n - 1)
        d = (f'M {cx:.1f} {-h/2+9:.1f} C {cx-9:.1f} {-h/2+26:.1f} {cx-9:.1f} {h/2-26:.1f} '
             f'{cx:.1f} {h/2-9:.1f}') if i % 2 == 0 else \
            (f'M {cx:.1f} {-h/2+9:.1f} C {cx+9:.1f} {-h/2+26:.1f} {cx+9:.1f} {h/2-26:.1f} '
             f'{cx:.1f} {h/2-9:.1f}')
        s.append(f'<path d="{d}" fill="none" stroke="{C["orange"]}" stroke-width="3.2" stroke-linecap="round"/>')
    o = "".join(s)
    if label:
        o += text_el(0, h / 2 + 22, label, 16)
    return _loc(x, y, o, rotate=angle)


def rough_er(x, y, w=150, h=90, label=None, angle=0):
    """粗面内质网: 波浪膜 + 核糖体"""
    s = [f'<path d="M {-w/2} {-h/2+14} C {-w/2+w*0.15} {-h/2-6} {-w/2+w*0.3} {-h/2+30} {-w/2+w*0.45} {-h/2+8} '
         f'S {-w/2+w*0.75} {-h/2+34} {w/2} {-h/2+4}" fill="none" stroke="{C["teal"]}" stroke-width="9" stroke-linecap="round"/>']
    for i in range(7):
        t = i / 6
        cx = -w / 2 + t * w
        cy = -h / 2 + 16 + (10 if i % 2 else -6) * math.sin(t * 9)
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.4" fill="{C["purple"]}"/>')
    o = "".join(s)
    if label:
        o += text_el(0, h / 2 + 22, label, 15)
    return _loc(x, y, o, rotate=angle)


def smooth_er(x, y, w=140, h=70, label=None):
    s = []
    for k in range(3):
        yy = -h / 2 + k * (h / 2.4)
        s.append(f'<path d="M {-w/2} {yy:.1f} q 20 -18 42 0 t 42 0 t 42 0" fill="none" '
                 f'stroke="{C["teal"]}" stroke-width="7" stroke-linecap="round" opacity="{0.95-k*0.15}"/>')
    o = "".join(s)
    if label:
        o += text_el(0, h / 2 + 20, label, 15)
    return _loc(x, y, o)


def golgi(x, y, w=150, h=95, label=None, flip=False):
    """高尔基体: 4 层扁平囊 + 出芽囊泡"""
    sc = -1 if flip else 1
    s = []
    for k in range(4):
        yy = -h / 2 + k * (h / 3.6)
        s.append(f'<path d="M {-w/2} {yy:.1f} C {-w/4} {yy+16*sc:.1f} {w/4} {yy-16*sc:.1f} {w/2} {yy+4*sc:.1f}" '
                 f'fill="none" stroke="{C["yellow"]}" stroke-width="9" stroke-linecap="round" '
                 f'opacity="{1 - k * 0.1}"/>')
    for cx, cy in ((-w / 2 - 14, h / 2 - 6), (w / 2 + 16, -h / 2 + 10), (w / 2 + 4, h / 2 + 8)):
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="{C["yellow_l"]}" stroke="{C["yellow"]}" stroke-width="2"/>')
    o = "".join(s)
    if label:
        o += text_el(0, h / 2 + 26, label, 15)
    return _loc(x, y, o)


def lysosome(x, y, r=30, label=None):
    o = (f'<circle r="{r}" fill="{C["red_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>'
         f'<circle r="{r-7}" fill="none" stroke="{C["red"]}" stroke-width="1.4" stroke-dasharray="3 3"/>')
    if label:
        o += text_el(0, r + 20, label, 15)
    return _loc(x, y, o)


def peroxisome(x, y, r=24, label=None):
    o = f'<circle r="{r}" fill="{C["teal_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.2"/>'
    if label:
        o += text_el(0, r + 19, label, 14)
    return _loc(x, y, o)


def ribosome(x, y, label=None, r=12):
    o = (f'<ellipse cx="0" cy="3" rx="{r}" ry="{r*0.72:.1f}" fill="{C["purple_l"]}" stroke="{C["purple"]}" stroke-width="2"/>'
         f'<ellipse cx="0" cy="-{r*0.55:.1f}" rx="{r*0.7:.1f}" ry="{r*0.42:.1f}" fill="{C["purple"]}" opacity="0.8"/>')
    if label:
        o += text_el(0, r + 16, label, 13)
    return _loc(x, y, o)


def centriole(x, y, label=None):
    s = []
    for dx in (-12, 12):
        s.append(f'<rect x="{dx-7}" y="-16" width="14" height="32" rx="3" fill="{C["gray_l"]}" '
                 f'stroke="{DEFAULT_STROKE}" stroke-width="2" transform="rotate({90 if dx<0 else 0} {dx} 0)"/>')
        for k in range(3):
            s.append(f'<line x1="{dx-7}" y1="{-9+k*9}" x2="{dx+7}" y2="{-9+k*9}" stroke="{DEFAULT_STROKE}" stroke-width="1" transform="rotate({90 if dx<0 else 0} {dx} 0)"/>')
    o = "".join(s)
    if label:
        o += text_el(0, 40, label, 14)
    return _loc(x, y, o)


def vesicle(x, y, r=16, fill=None, label=None):
    o = f'<circle r="{r}" fill="{fill or C["teal_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>'
    if label:
        o += text_el(0, r + 17, label, 13)
    return _loc(x, y, o)


def autophagosome(x, y, r=38, inner=None, label=None):
    """双膜自噬体"""
    o = (f'<circle r="{r}" fill="none" stroke="{C["teal"]}" stroke-width="4.5" stroke-dasharray="9 5"/>'
         f'<circle r="{r-6}" fill="none" stroke="{C["teal"]}" stroke-width="3.5"/>'
         f'<circle r="{r*0.45:.1f}" fill="{C["orange_l"]}" stroke="{C["orange"]}" stroke-width="1.6"/>')
    if label:
        o += text_el(0, r + 20, label, 15)
    return _loc(x, y, o)


def chloroplast(x, y, w=95, h=60, label=None):
    s = [f'<ellipse rx="{w/2}" ry="{h/2}" fill="{C["green_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>']
    for i in range(5):
        a = math.pi * 2 * i / 5 + 0.5
        s.append(f'<circle cx="{(w/2-16)*math.cos(a):.1f}" cy="{(h/2-14)*math.sin(a):.1f}" r="8" fill="{C["green"]}" opacity="0.75"/>')
    o = "".join(s)
    if label:
        o += text_el(0, h / 2 + 20, label, 15)
    return _loc(x, y, o)


def cytoskeleton(x, y, length=140, kind="microtubule", angle=0, label=None):
    if kind == "microtubule":
        s = [f'<line x1="{-length/2}" y1="0" x2="{length/2}" y2="0" stroke="{C["purple"]}" stroke-width="7" stroke-linecap="round"/>']
        n = int(length / 12)
        for i in range(n):
            xx = -length / 2 + 6 + i * 12
            s.append(f'<line x1="{xx:.1f}" y1="-3.5" x2="{xx:.1f}" y2="3.5" stroke="#FFFFFF" stroke-width="1.4"/>')
    else:  # actin
        s = [f'<line x1="{-length/2}" y1="0" x2="{length/2}" y2="0" stroke="{C["red"]}" stroke-width="3.4" stroke-linecap="round"/>']
        n = int(length / 14)
        for i in range(n):
            xx = -length / 2 + 7 + i * 14
            s.append(f'<line x1="{xx:.1f}" y1="-4" x2="{xx+7:.1f}" y2="4" stroke="{C["red"]}" stroke-width="3" stroke-linecap="round" opacity="0.7"/>')
    o = "".join(s)
    if label:
        o += text_el(0, 24, label, 13)
    return _loc(x, y, o, rotate=angle)


def membrane_patch(x, y, w=200, h=34, label=None):
    """磷脂双分子层贴片, 以中心为锚"""
    o = _bilayer(w, h)
    if label:
        o += text_el(0, h / 2 + 22, label, 14)
    return _loc(x, y, o)


def cell_generic(x, y, w=220, h=170, label=None, fill=None, membrane_only=False, organelles=False):
    """通用动物细胞(含细胞器简笔)"""
    fill = fill or C["blue_l"]
    s = [f'<ellipse rx="{w/2}" ry="{h/2}" fill="{fill}" stroke="{DEFAULT_STROKE}" stroke-width="3"/>']
    if not membrane_only:
        s.append(f'<ellipse rx="{w/2-5}" ry="{h/2-5}" fill="none" stroke="#FFFFFF" stroke-width="1.4" opacity="0.7"/>')
    if organelles:
        s.append(nucleus(-w * 0.22, -h * 0.1, r=h * 0.2))
        s.append(mitochondrion(w * 0.2, -h * 0.22, w=62, h=34))
        s.append(golgi(w * 0.24, h * 0.18, w=64, h=40))
        s.append(rough_er(-w * 0.3, h * 0.28, w=70, h=34))
    o = "".join(s)
    if label:
        o += text_el(0, -h / 2 - 12, label, 17)
    return _loc(x, y, o)


def cell_wall_plant(x, y, w=200, h=170, label=None):
    s = [f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" rx="16" fill="{C["green_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="3.4"/>',
         f'<rect x="{-w/2+9}" y="{-h/2+9}" width="{w-18}" height="{h-18}" rx="10" fill="none" stroke="{C["green"]}" stroke-width="2.4"/>',
         f'<circle cx="{-w*0.2:.1f}" cy="{-h*0.15:.1f}" r="{h*0.18:.1f}" fill="{C["blue_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>',
         f'<rect x="{w*0.1:.1f}" y="{h*0.05:.1f}" width="{w*0.42:.1f}" height="{h*0.5:.1f}" rx="18" fill="{C["teal_l"]}" stroke="{C["teal"]}" stroke-width="2" opacity="0.85"/>']
    for i in range(4):
        s.append(f'<circle cx="{w*0.18+i*15:.1f}" cy="{h*0.18:.1f}" r="7" fill="{C["green"]}" opacity="0.8"/>')
    o = "".join(s)
    if label:
        o += text_el(0, -h / 2 - 12, label, 16)
    return _loc(x, y, o)


# ---- 核酸 NUCLEIC ACIDS -----------------------------------------------------
def dna_helix(x, y, length=160, width=44, vertical=False, label=None, color=None):
    color = color or C["blue"]
    a, b = [], []
    n = 60
    for i in range(n + 1):
        t = i / n
        ph = t * math.pi * (length / 42.0)
        xx = -length / 2 + t * length
        yy = math.sin(ph) * width / 2
        b.append((xx, -yy))
        a.append((xx, yy))
    def _p(pts):
        return " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)
    s = []
    for i in range(0, n + 1, 6):
        s.append(f'<line x1="{a[i][0]:.1f}" y1="{a[i][1]:.1f}" x2="{b[i][0]:.1f}" y2="{b[i][1]:.1f}" stroke="{color}" stroke-width="2.6" opacity="0.85"/>')
    s.append(f'<polyline points="{_p(a)}" fill="none" stroke="{color}" stroke-width="3.6" stroke-linecap="round"/>')
    s.append(f'<polyline points="{_p(b)}" fill="none" stroke="{color}" stroke-width="3.6" stroke-linecap="round"/>')
    o = "".join(s)
    if label:
        o += text_el(0, width / 2 + 24, label, 15, italic=True)
    tr = f"translate({x},{y})" + (f" rotate({90})" if vertical else "")
    return f'<g transform="{tr}">{o}</g>'


def dna_linear(x, y, length=170, label=None):
    """DNA 平面梯形(双链+碱基对)"""
    s = [f'<line x1="{-length/2}" y1="-13" x2="{length/2}" y2="-13" stroke="{C["blue"]}" stroke-width="3.4"/>',
         f'<line x1="{-length/2}" y1="13" x2="{length/2}" y2="13" stroke="{C["blue"]}" stroke-width="3.4"/>']
    n = int(length / 17)
    cols = [C["red"], C["yellow"], C["green"], C["purple"]]
    for i in range(n):
        xx = -length / 2 + 8 + i * (length - 16) / max(1, n - 1)
        cc = cols[i % 4]
        s.append(f'<line x1="{xx:.1f}" y1="-13" x2="{xx:.1f}" y2="13" stroke="{cc}" stroke-width="3.4"/>')
    o = "".join(s)
    if label:
        o += text_el(0, 36, label, 15, italic=True)
    return _loc(x, y, o)


def mrna(x, y, length=200, label=None):
    """mRNA: 5'帽 - CDS - polyA"""
    s = [f'<circle cx="{-length/2-8}" cy="0" r="7" fill="{C["red"]}" opacity="0.9"/>',
         f'<rect x="{-length/2}" y="-6" width="{length}" height="12" rx="6" fill="{C["teal_l"]}" stroke="{C["teal"]}" stroke-width="2.2"/>']
    n = int(length / 22)
    for i in range(n):
        xx = -length / 2 + 14 + i * (length - 28) / max(1, n - 1)
        s.append(f'<line x1="{xx:.1f}" y1="-6" x2="{xx:.1f}" y2="6" stroke="{C["teal"]}" stroke-width="2"/>')
    for i in range(7):
        xx = length / 2 + 10 + i * 4.2
        s.append(f'<circle cx="{xx:.1f}" cy="0" r="2.6" fill="{C["orange"]}"/>')
    o = "".join(s) + (text_el(-length / 2 - 8, -16, "5′", 13) if True else "")
    o += text_el(length / 2 + 36, 0, "3′", 13)
    if label:
        o += text_el(0, 28, label, 14, italic=True)
    return _loc(x, y, o)


def trna(x, y, size=1.0, label=None):
    """tRNA 三叶草简化形"""
    s = [f'<path d="M 0 0 C -26 -6 -30 -34 -12 -38 C -2 -40 2 -34 0 -26" fill="none" stroke="{C["purple"]}" stroke-width="4"/>',
         f'<path d="M 0 0 C 26 -6 30 -34 12 -38" fill="none" stroke="{C["purple"]}" stroke-width="4"/>',
         f'<path d="M 0 0 C -4 22 -22 26 -20 44" fill="none" stroke="{C["purple"]}" stroke-width="4"/>',
         f'<circle cx="-20" cy="48" r="6" fill="{C["orange_l"]}" stroke="{C["orange"]}" stroke-width="2"/>']
    o = "".join(s)
    if label:
        o += text_el(0, 72, label, 14, italic=True)
    return _loc(x, y, o, scale=size)


def plasmid(x, y, r=62, label=None, genes=("AmpR", "Gene X", "ori")):
    s = [f'<circle r="{r}" fill="none" stroke="{C["blue"]}" stroke-width="9" opacity="0.9"/>']
    n = len(genes)
    for i, gname in enumerate(genes):
        a = math.pi * 2 * i / n - math.pi / 2
        span = math.pi * 2 / n * 0.34
        s.append(f'<path d="M {r*math.cos(a):.1f} {r*math.sin(a):.1f} '
                 f'A {r} {r} 0 0 1 {r*math.cos(a+span):.1f} {r*math.sin(a+span):.1f}" '
                 f'fill="none" stroke="{[C["red"],C["green"],C["yellow"],C["purple"]][i%4]}" stroke-width="9"/>')
        lx, ly = (r + 24) * math.cos(a + span / 2), (r + 24) * math.sin(a + span / 2)
        s.append(text_el(lx, ly + 5, gname, 13))
        s.append(f'<line x1="{(r+4)*math.cos(a+span/2):.1f}" y1="{(r+4)*math.sin(a+span/2):.1f}" '
                 f'x2="{(r+14)*math.cos(a+span/2):.1f}" y2="{(r+14)*math.sin(a+span/2):.1f}" stroke="{C["gray"]}" stroke-width="1.4"/>')
    o = "".join(s)
    if label:
        o += text_el(0, -r - 14, label, 15, italic=True)
    return _loc(x, y, o)


def chromosome(x, y, size=1.0, label=None, color=None):
    color = color or C["purple"]
    a = 13 * size
    def _arm(sx, sy):
        return (f'<rect x="{sx*a - 6*size:.1f}" y="{sy*a - 40*size:.1f}" width="{12*size:.1f}" '
                f'height="{80*size:.1f}" rx="{6*size:.1f}" fill="{color}" opacity="0.9"/>')
    s = []
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        s.append(_arm(sx, sy))
    s.append(f'<circle r="{9*size:.1f}" fill="{C["paper"]}" stroke="{color}" stroke-width="{2.5*size:.1f}"/>')
    o = "".join(s)
    if label:
        o += text_el(0, 62 * size, label, 15)
    return _loc(x, y, o)


def nucleosome(x, y, n=5, spacing=44, label=None):
    """核小体串珠('beads-on-a-string')"""
    s = [f'<line x1="{-n*spacing/2}" y1="0" x2="{n*spacing/2}" y2="0" stroke="{C["blue"]}" stroke-width="2.4"/>']
    for i in range(n):
        cx = -n * spacing / 2 + spacing / 2 + i * spacing
        s.append(f'<circle cx="{cx:.1f}" cy="0" r="13" fill="{C["purple_l"]}" stroke="{C["purple"]}" stroke-width="2.4"/>')
        s.append(f'<line x1="{cx:.1f}" y1="0" x2="{cx+spacing/2:.1f}" y2="0" stroke="{C["blue"]}" stroke-width="2.4"/>')
    o = "".join(s)
    if label:
        o += text_el(0, 36, label, 14)
    return _loc(x, y, o)


def gene_cassette(x, y, w=210, label=None, promoter="P", gene="GOI"):
    """启动子-基因-终止子 表达框"""
    s = [f'<path d="M {-w/2} -14 L {-w/2+34} 0 L {-w/2} 14 Z" fill="{C["red"]}" opacity="0.9"/>',
         text_el(-w / 2 + 17, -22, promoter, 13),
         f'<rect x="{-w/2+40}" y="-15" width="{w*0.52:.0f}" height="30" rx="4" fill="{C["blue_l"]}" stroke="{C["blue"]}" stroke-width="2.4"/>',
         text_el(-w / 2 + 40 + w * 0.26, 6, gene, 15, bold=True),
         f'<line x1="{w/2-26}" y1="0" x2="{w/2}" y2="0" stroke="{C["gray"]}" stroke-width="3"/>',
         f'<line x1="{w/2-8}" y1="-9" x2="{w/2-8}" y2="9" stroke="{C["gray"]}" stroke-width="3"/>',
         f'<line x1="{w/2-16}" y1="-9" x2="{w/2-16}" y2="9" stroke="{C["gray"]}" stroke-width="3"/>']
    o = "".join(s)
    if label:
        o += text_el(0, 42, label, 14)
    return _loc(x, y, o)


# ---- 蛋白 PROTEINS ----------------------------------------------------------
def protein_blob(x, y, r=30, label=None, fill=None, shape="circle"):
    """通用球状蛋白; shape: circle|square|triangle|hexagon|crescent"""
    fill = fill or C["orange_l"]
    stroke = DEFAULT_STROKE
    if shape == "circle":
        o = f'<circle r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2.4"/>'
    elif shape == "square":
        o = f'<rect x="{-r}" y="{-r}" width="{2*r}" height="{2*r}" rx="{r*0.3:.0f}" fill="{fill}" stroke="{stroke}" stroke-width="2.4"/>'
    elif shape == "triangle":
        p = " ".join(f"{r*math.cos(math.pi*2*i/3-math.pi/2):.1f},{r*math.sin(math.pi*2*i/3-math.pi/2):.1f}" for i in range(3))
        o = f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="2.4" stroke-linejoin="round"/>'
    elif shape == "hexagon":
        p = " ".join(f"{r*math.cos(math.pi*i/3):.1f},{r*math.sin(math.pi*i/3):.1f}" for i in range(6))
        o = f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="2.4" stroke-linejoin="round"/>'
    else:  # crescent
        o = (f'<path d="M 0 {-r} A {r} {r} 0 1 0 0 {r} A {r*0.62:.1f} {r*0.62:.1f} 0 1 1 0 {-r} Z" '
             f'fill="{fill}" stroke="{stroke}" stroke-width="2.4"/>')
    if label:
        o += text_el(0, -r - 10, label, 14, halo=4)
    return _loc(x, y, o)


def receptor_tmembrane(x, y, label=None, ligand=True, fill=None, w=46, h=86):
    """跨膜受体(单体, 嵌在膜上)"""
    fill = fill or C["purple_l"]
    s = [f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h*0.42:.0f}" rx="{w*0.34:.0f}" fill="{fill}" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>',
         f'<rect x="{-7}" y="{-h*0.06:.0f}" width="14" height="{h*0.52:.0f}" rx="5" fill="{fill}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>',
         f'<rect x="{-w*0.38:.0f}" y="{h*0.44:.0f}" width="{w*0.76:.0f}" height="{h*0.2:.0f}" rx="7" fill="{fill}" stroke="{DEFAULT_STROKE}" stroke-width="2.2"/>']
    if ligand:
        s.append(f'<circle cx="0" cy="{-h/2-14}" r="11" fill="{C["orange"]}" opacity="0.9"/>')
        s.append(f'<line x1="0" y1="{-h/2-3}" x2="0" y2="{-h/2+4}" stroke="{C["orange"]}" stroke-width="2.4" stroke-dasharray="2 2"/>')
    o = "".join(s)
    if label:
        o += text_el(w / 2 + 12, 8, label, 14, anchor="start", halo=4)
    return _loc(x, y, o)


def gpcr(x, y, label=None, fill=None):
    """G 蛋白偶联受体(7 次跨膜简化)"""
    fill = fill or C["teal_l"]
    s = [f'<rect x="{-34}" y="-30" width="68" height="26" fill="{C["gray_l"]}" opacity="0.55"/>']
    for i in range(7):
        xx = -27 + i * 9
        top = -30 if i % 2 == 0 else -4
        s.append(f'<rect x="{xx-3}" y="{top}" width="6" height="26" rx="3" fill="{fill}" stroke="{DEFAULT_STROKE}" stroke-width="1.4"/>')
    s.append(f'<circle cx="0" cy="-44" r="12" fill="{C["orange"]}" opacity="0.9"/>')
    s.append(f'<path d="M -14 -4 C -20 10 -14 24 -4 30" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="4" stroke-linecap="round"/>')
    o = "".join(s)
    if label:
        o += text_el(0, 52, label, 14)
    return _loc(x, y, o)


def ion_channel(x, y, label=None, open_=True, fill=None):
    fill = fill or C["blue_l"]
    tilt = -8 if open_ else 8
    s = [f'<rect x="{-30}" y="-30" width="60" height="26" fill="{C["gray_l"]}" opacity="0.55"/>']
    for sx in (-1, 1):
        p = (f'{sx*20},{-30} {sx*8},{-30} {sx*6+tilt*sx*0},{-6} {sx*13+tilt},{8} {sx*22+tilt},{30} {sx*11+tilt},{30}')
        s.append(f'<polygon points="{p}" fill="{fill}" stroke="{DEFAULT_STROKE}" stroke-width="2.2" stroke-linejoin="round"/>')
    if open_:
        s.append(f'<circle cx="0" cy="-42" r="7" fill="{C["yellow"]}"/>')
        s.append(f'<circle cx="0" cy="44" r="7" fill="{C["yellow"]}"/>')
    o = "".join(s)
    if label:
        o += text_el(52, 4, label, 14, anchor="start", halo=4)
    return _loc(x, y, o)


def antibody_igg(x, y, size=1.0, label=None, fill=None):
    """IgG 抗体 (Y 形, 含抗原结合位)"""
    fill = fill or C["green_l"]
    s = 42 * size
    s1 = (f'<path d="M 0 {s*0.9:.1f} L 0 {s*0.1:.1f} L {-s*0.85:.1f} {-s*0.9:.1f} L {-s*0.55:.1f} {-s*1.25:.1f} '
          f'L 0 {-s*0.32:.1f} L {s*0.55:.1f} {-s*1.25:.1f} L {s*0.85:.1f} {-s*0.9:.1f} L 0 {s*0.1:.1f} Z" '
          f'fill="{fill}" stroke="{DEFAULT_STROKE}" stroke-width="{2.6*size:.1f}" stroke-linejoin="round"/>')
    for sx in (-0.7, 0.7):
        s1 += f'<circle cx="{sx*s:.1f}" cy="{-s*1.05:.1f}" r="{6*size:.1f}" fill="{C["red"]}" opacity="0.85"/>'
    s1 += (f'<line x1="0" y1="{s*0.1:.1f}" x2="0" y2="{s*0.55:.1f}" stroke="{DEFAULT_STROKE}" '
           f'stroke-width="{2*size:.1f}" stroke-dasharray="4 3"/>')
    o = s1
    if label:
        o += text_el(0, s * 1.5, label, 14)
    return _loc(x, y, o, scale=1.0)


def enzyme_lock_key(x, y, label=None):
    """酶-底物(锁钥模型)"""
    o = (f'<path d="M -34 6 A 34 34 0 1 1 34 6 L 22 6 L 22 20 L 8 20 L 8 6 Z" '
         f'fill="{C["blue_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>'
         f'<rect x="-14" y="-16" width="28" height="16" rx="3" fill="{C["yellow"]}" stroke="{C["yellow"]}" stroke-width="1"/>')
    if label:
        o += text_el(0, 48, label, 14)
    return _loc(x, y, o)


def phosphate(x, y, r=12, label=None):
    o = f'<circle r="{r}" fill="{C["yellow"]}" stroke="{C["yellow"]}" stroke-width="2"/>'
    o += text_el(0, 5, "P", 15, bold=True, fill="#FFFFFF")
    if label:
        o += text_el(0, r + 16, label, 12)
    return _loc(x, y, o)


def atp_adp(x, y, label="ATP", w=46):
    o = (f'<rect x="{-w/2}" y="-15" width="{w}" height="30" rx="8" fill="{C["yellow_l"]}" '
         f'stroke="{C["yellow"]}" stroke-width="2.2"/>'
         + text_el(0, 6, label, 15, bold=True))
    return _loc(x, y, o)


def ion_dot(x, y, symbol="Ca²⁺", color=None, r=15, label=None):
    color = color or C["red"]
    o = f'<circle r="{r}" fill="{color}" opacity="0.9"/>'
    o += text_el(0, 5, symbol, 13, fill="#FFFFFF", bold=True)
    if label:
        o += text_el(0, r + 16, label, 12)
    return _loc(x, y, o)


def ubiquitin_tag(x, y, r=11, label=None):
    o = f'<circle r="{r}" fill="{C["purple"]}" opacity="0.85"/>'
    o += text_el(0, 5, "Ub", 11, fill="#FFFFFF", bold=True)
    if label:
        o += text_el(0, r + 15, label, 12)
    return _loc(x, y, o)


def proteasome(x, y, label=None):
    o = (f'<rect x="-20" y="-40" width="40" height="80" rx="8" fill="{C["gray_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>'
         f'<rect x="-26" y="-18" width="52" height="36" rx="6" fill="{C["blue_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.2"/>'
         f'<line x1="-20" y1="-14" x2="20" y2="-14" stroke="#FFFFFF" stroke-width="1.6"/>'
         f'<line x1="-20" y1="0" x2="20" y2="0" stroke="#FFFFFF" stroke-width="1.6"/>'
         f'<line x1="-20" y1="14" x2="20" y2="14" stroke="#FFFFFF" stroke-width="1.6"/>')
    if label:
        o += text_el(0, 62, label, 14)
    return _loc(x, y, o)


# ---- 细胞 CELLS -------------------------------------------------------------
def cell_epithelial(x, y, w=70, h=110, kind="columnar", label=None, cilia=False, microvilli=False):
    """上皮细胞: squamous|cuboidal|columnar"""
    fill = C["blue_l"]
    if kind == "squamous":
        o = f'<ellipse rx="{w/2}" ry="{h*0.16:.0f}" fill="{fill}" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>'
    elif kind == "cuboidal":
        o = f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h*0.7:.0f}" rx="10" fill="{fill}" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>'
    else:
        o = f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>'
    hh = h * (0.16 if kind == "squamous" else (0.7 if kind == "cuboidal" else 1.0))
    o += f'<circle cx="0" cy="{hh*0.18:.1f}" r="{min(hh*0.24, 16):.1f}" fill="{C["purple_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="1.8"/>'
    if cilia:
        for i in range(5):
            xx = -w / 2 + 8 + i * (w - 16) / 4
            o += f'<line x1="{xx:.1f}" y1="{-h/2}" x2="{xx+4:.1f}" y2="{-h/2-16}" stroke="{C["teal"]}" stroke-width="3" stroke-linecap="round"/>'
    if microvilli:
        for i in range(7):
            xx = -w / 2 + 6 + i * (w - 12) / 6
            o += f'<line x1="{xx:.1f}" y1="{-h/2}" x2="{xx:.1f}" y2="{-h/2-9}" stroke="{C["gray"]}" stroke-width="1.8"/>'
    if label:
        o += text_el(0, hh / 2 + 22, label, 14)
    return _loc(x, y, o)


def fibroblast(x, y, label=None, w=90, h=60):
    o = (f'<path d="M 0 {-h/2} C {w/2} {-h/2-6} {w/2+12} {-4} {w/2-4} {h/2-6} '
         f'C {w/3} {h/2+6} {-w/3} {h/2+6} {-w/2+4} {h/2-6} '
         f'C {-w/2-12} {-4} {-w/2} {-h/2-6} 0 {-h/2} Z" '
         f'fill="{C["teal_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>'
         f'<ellipse cx="-6" cy="-4" rx="14" ry="10" fill="{C["purple_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="1.6"/>')
    if label:
        o += text_el(0, h / 2 + 24, label, 14)
    return _loc(x, y, o)


def adipocyte(x, y, r=52, label=None):
    o = (f'<circle r="{r}" fill="{C["yellow_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>'
         f'<circle r="{r*0.72:.1f}" fill="{C["yellow"]}" opacity="0.55"/>'
         f'<ellipse cx="{-r*0.78:.1f}" cy="{-r*0.5:.1f}" rx="9" ry="6" fill="{C["purple_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="1.4" transform="rotate(-35 {-r*0.78:.1f} {-r*0.5:.1f})"/>')
    if label:
        o += text_el(0, r + 22, label, 14)
    return _loc(x, y, o)


def macrophage(x, y, r=48, label=None):
    """巨噬细胞(伪足不规则形)"""
    pts = []
    n = 14
    for i in range(n):
        a = math.pi * 2 * i / n
        rr = r * (1 + 0.18 * math.sin(i * 2.3) + 0.12 * math.cos(i * 3.1))
        pts.append(f"{rr*math.cos(a):.1f},{rr*math.sin(a):.1f}")
    o = (f'<polygon points="{" ".join(pts)}" fill="{C["teal_l"]}" stroke="{DEFAULT_STROKE}" '
         f'stroke-width="2.4" stroke-linejoin="round"/>'
         f'<path d="M -14 -8 C -4 -20 12 -18 14 -4 C 16 8 2 14 -8 8 C -16 4 -18 -2 -14 -8 Z" '
         f'fill="{C["purple_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="1.6"/>')
    if label:
        o += text_el(0, r + 24, label, 14)
    return _loc(x, y, o)


def neutrophil(x, y, r=38, label=None):
    """中性粒细胞(分叶核)"""
    o = f'<circle r="{r}" fill="{C["blue_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>'
    for cx, cy, rot in ((-14, -10, 20), (12, -14, -25), (0, 12, 60)):
        o += (f'<ellipse cx="{cx}" cy="{cy}" rx="15" ry="10" fill="{C["purple_l"]}" '
              f'stroke="{C["purple"]}" stroke-width="1.8" transform="rotate({rot} {cx} {cy})"/>')
    o += f'<line x1="-12" y1="-4" x2="10" y2="8" stroke="{C["purple"]}" stroke-width="2.4"/>'
    if label:
        o += text_el(0, r + 22, label, 14)
    return _loc(x, y, o)


def lymphocyte(x, y, r=34, label=None, receptor=True):
    o = f'<circle r="{r}" fill="{C["blue_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>'
    o += f'<circle cx="{-4}" cy="-3" r="{r*0.42:.1f}" fill="{C["purple_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="1.6"/>'
    if receptor:
        for a in (-2.2, -1.6, -1.0):
            x1, y1 = (r - 2) * math.cos(a), (r - 2) * math.sin(a)
            x2, y2 = (r + 12) * math.cos(a), (r + 12) * math.sin(a)
            o += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{C["red"]}" stroke-width="3" stroke-linecap="round"/>'
    if label:
        o += text_el(0, r + 22, label, 14)
    return _loc(x, y, o)


def rbc(x, y, r=26, label=None):
    o = (f'<circle r="{r}" fill="{C["red_l"]}" stroke="{C["red"]}" stroke-width="2.4"/>'
         f'<circle r="{r*0.5:.1f}" fill="{C["red"]}" opacity="0.25"/>')
    if label:
        o += text_el(0, r + 20, label, 14)
    return _loc(x, y, o)


def platelet(x, y, r=14, label=None):
    pts = []
    for i in range(9):
        a = math.pi * 2 * i / 9
        rr = r * (1 + 0.16 * math.sin(i * 2.7))
        pts.append(f"{rr*math.cos(a):.1f},{rr*math.sin(a):.1f}")
    o = f'<polygon points="{" ".join(pts)}" fill="{C["yellow_l"]}" stroke="{C["yellow"]}" stroke-width="2"/>'
    if label:
        o += text_el(0, r + 18, label, 13)
    return _loc(x, y, o)


def neuron(x, y, length=280, label=None):
    """神经元: 胞体+树突+轴突+髓鞘+末梢"""
    s = [f'<path d="M -50 0 C -20 -8 -6 -6 0 0 C 6 6 20 8 50 0" fill="none"/>']
    s.append(f'<circle cx="-50" cy="0" r="24" fill="{C["blue_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>')
    s.append(f'<circle cx="-54" cy="-4" r="9" fill="{C["purple_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="1.5"/>')
    for a, L in ((2.5, 46), (2.9, 40), (-2.6, 44), (-2.2, 38), (3.1, 34)):
        x2 = -50 + L * math.cos(a); y2 = L * math.sin(a)
        s.append(f'<line x1="{-50+16*math.cos(a):.1f}" y1="{16*math.sin(a):.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="{DEFAULT_STROKE}" stroke-width="3" stroke-linecap="round"/>')
    s.append(f'<line x1="-26" y1="0" x2="{length-60}" y2="0" stroke="{DEFAULT_STROKE}" stroke-width="5" stroke-linecap="round"/>')
    seg = (length - 90) / 4
    for i in range(4):
        x1 = -14 + i * seg
        s.append(f'<rect x="{x1:.1f}" y="-13" width="{seg*0.78:.1f}" height="26" rx="11" fill="{C["yellow_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>')
    s.append(f'<circle cx="{length-52}" cy="0" r="16" fill="{C["blue_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>')
    for a in (0.6, -0.6):
        x2 = length - 52 + 20 * math.cos(a); y2 = 20 * math.sin(a)
        s.append(f'<line x1="{length-52+12*math.cos(a):.1f}" y1="{12*math.sin(a):.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="{DEFAULT_STROKE}" stroke-width="3.4" stroke-linecap="round"/>')
        s.append(f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="4" fill="{C["orange"]}"/>')
    o = "".join(s)
    if label:
        o += text_el(-50, -46, label, 15)
    return _loc(x, y, o)


def muscle_fiber(x, y, w=170, h=40, kind="skeletal", label=None):
    s = [f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" rx="{h/2}" fill="{C["red_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>']
    n = int(w / 16)
    for i in range(n):
        xx = -w / 2 + 8 + i * 16
        s.append(f'<line x1="{xx:.1f}" y1="{-h/2+4}" x2="{xx:.1f}" y2="{h/2-4}" stroke="{C["red"]}" stroke-width="2.2" opacity="0.7"/>')
    if kind == "cardiac":
        s.append(f'<line x1="{-w*0.1:.0f}" y1="{-h/2}" x2="{-w*0.1:.0f}" y2="{h/2}" stroke="{DEFAULT_STROKE}" stroke-width="2.6" stroke-dasharray="4 3"/>')
    o = "".join(s)
    if label:
        o += text_el(0, h / 2 + 22, label, 14)
    return _loc(x, y, o)


def sperm(x, y, angle=0, label=None):
    o = (f'<ellipse cx="0" cy="0" rx="11" ry="15" fill="{C["blue_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>'
         f'<path d="M 0 15 C 8 40 -8 60 0 92" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="2.6" stroke-linecap="round"/>')
    if label:
        o += text_el(0, 112, label, 13)
    return _loc(x, y, o, rotate=angle - 90)


def oocyte(x, y, r=58, label=None, corona=True):
    o = [f'<circle r="{r}" fill="{C["yellow_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.6"/>',
         f'<circle r="{r*0.78:.1f}" fill="{C["yellow"]}" opacity="0.5"/>',
         f'<circle cx="{-r*0.3:.1f}" cy="{-r*0.3:.1f}" r="{r*0.16:.1f}" fill="{C["purple_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="1.6"/>']
    if corona:
        for i in range(16):
            a = math.pi * 2 * i / 16
            x1, y1 = (r + 2) * math.cos(a), (r + 2) * math.sin(a)
            x2, y2 = (r + 13) * math.cos(a), (r + 13) * math.sin(a)
            o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{C["yellow"]}" stroke-width="2.4" stroke-linecap="round"/>')
    out = "".join(o)
    if label:
        out += text_el(0, r + 30, label, 14)
    return _loc(x, y, out)


def blastocyst(x, y, r=64, label=None):
    """胚泡: 滋养层+内细胞群+囊胚腔"""
    o = [f'<circle r="{r}" fill="{C["blue_l"]}" opacity="0.5" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>']
    for i in range(14):
        a = math.pi * 2 * i / 14
        o.append(f'<circle cx="{(r-8)*math.cos(a):.1f}" cy="{(r-8)*math.sin(a):.1f}" r="8" fill="{C["orange_l"]}" stroke="{C["orange"]}" stroke-width="1.4"/>')
    for dx in (-7, 7):
        for dy in (-7, 7):
            o.append(f'<circle cx="{dx}" cy="{dy}" r="8" fill="{C["teal_l"]}" stroke="{C["teal"]}" stroke-width="1.6"/>')
    out = "".join(o)
    if label:
        out += text_el(0, r + 24, label, 14)
    return _loc(x, y, out)


def cancer_cell(x, y, r=46, label=None):
    pts = []
    for i in range(16):
        a = math.pi * 2 * i / 16
        rr = r * (1 + 0.28 * math.sin(i * 3.3) + 0.1 * math.cos(i * 5.1))
        pts.append(f"{rr*math.cos(a):.1f},{rr*math.sin(a):.1f}")
    o = (f'<polygon points="{" ".join(pts)}" fill="{C["red_l"]}" stroke="{C["red"]}" '
         f'stroke-width="2.6" stroke-linejoin="round"/>'
         f'<circle cx="-6" cy="-4" r="15" fill="{C["purple_l"]}" stroke="{C["purple"]}" stroke-width="1.8"/>')
    if label:
        o += text_el(0, r + 26, label, 14)
    return _loc(x, y, o)


def bacterium(x, y, shape="rod", label=None, color=None):
    color = color or C["teal"]
    if shape == "rod":
        o = f'<rect x="-34" y="-15" width="68" height="30" rx="15" fill="{color}" opacity="0.85" stroke="{DEFAULT_STROKE}" stroke-width="2"/>'
    elif shape == "coccus":
        o = f'<circle r="16" fill="{color}" opacity="0.85" stroke="{DEFAULT_STROKE}" stroke-width="2"/>'
    else:  # spiral
        o = (f'<path d="M -34 8 C -18 -22 0 26 18 -6 C 24 -16 30 -14 34 -4" fill="none" '
             f'stroke="{color}" stroke-width="9" stroke-linecap="round" opacity="0.85"/>'
             f'<path d="M -34 8 C -18 -22 0 26 18 -6 C 24 -16 30 -14 34 -4" fill="none" '
             f'stroke="{DEFAULT_STROKE}" stroke-width="1.6"/>')
    if label:
        o += text_el(0, 38, label, 13, italic=True)
    return _loc(x, y, o)


def virus_enveloped(x, y, r=34, label=None, spikes=12, color=None):
    """有包膜病毒(如冠状病毒)"""
    color = color or C["red"]
    o = [f'<circle r="{r}" fill="{color}" opacity="0.2" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>',
         f'<circle r="{r*0.66:.1f}" fill="{color}" opacity="0.55"/>']
    for i in range(spikes):
        a = math.pi * 2 * i / spikes
        x1, y1 = (r - 2) * math.cos(a), (r - 2) * math.sin(a)
        x2, y2 = (r + 12) * math.cos(a), (r + 12) * math.sin(a)
        o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="4.4" stroke-linecap="round"/>')
        o.append(f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="3.4" fill="{color}"/>')
    out = "".join(o)
    if label:
        out += text_el(0, r + 28, label, 13, italic=True)
    return _loc(x, y, out)


def virus_icosa(x, y, r=30, label=None, color=None):
    color = color or C["blue"]
    p = " ".join(f"{r*math.cos(math.pi*2*i/6+0.5):.1f},{r*math.sin(math.pi*2*i/6+0.5):.1f}" for i in range(6))
    o = f'<polygon points="{p}" fill="{color}" opacity="0.35" stroke="{DEFAULT_STROKE}" stroke-width="2.4" stroke-linejoin="round"/>'
    p2 = " ".join(f"{r*0.55*math.cos(math.pi*2*i/6+0.5):.1f},{r*0.55*math.sin(math.pi*2*i/6+0.5):.1f}" for i in range(6))
    o += f'<polygon points="{p2}" fill="none" stroke="{color}" stroke-width="1.8" stroke-linejoin="round" transform="rotate(30)"/>'
    for i in range(6):
        a = math.pi * 2 * i / 6 + 0.5
        o += f'<line x1="{r*math.cos(a):.1f}" y1="{r*math.sin(a):.1f}" x2="{r*0.55*math.cos(a+0.52):.1f}" y2="{r*0.55*math.sin(a+0.52):.1f}" stroke="{color}" stroke-width="1.8"/>'
    if label:
        o += text_el(0, r + 24, label, 13, italic=True)
    return _loc(x, y, o)


def bacteriophage(x, y, label=None):
    o = [f'<polygon points="0,-52 20,-40 20,-16 -20,-16 -20,-40" fill="{C["blue_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.2" stroke-linejoin="round"/>',
         f'<rect x="-7" y="-16" width="14" height="34" fill="{C["teal_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>',
         f'<rect x="-16" y="18" width="32" height="8" rx="3" fill="{C["teal_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>']
    for sx in (-1, 1):
        o.append(f'<line x1="{sx*14}" y1="24" x2="{sx*34}" y2="46" stroke="{DEFAULT_STROKE}" stroke-width="2.6" stroke-linecap="round"/>')
    out = "".join(o)
    if label:
        out += text_el(0, 68, label, 13, italic=True)
    return _loc(x, y, out)


# ---- 组织/器官 TISSUES & ORGANS ---------------------------------------------
def skin_section(x, y, w=280, h=170, label=None):
    """皮肤分层切片示意"""
    s = [f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h*0.26:.0f}" fill="{C["blue_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="1.6"/>',
         f'<rect x="{-w/2}" y="{-h/2+h*0.26:.0f}" width="{w}" height="{h*0.2:.0f}" fill="{C["blue"]}" opacity="0.3"/>',
         f'<rect x="{-w/2}" y="{-h/2+h*0.46:.0f}" width="{w}" height="{h*0.54:.0f}" fill="{C["yellow_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="1.6"/>']
    for i in range(5):
        xx = -w / 2 + 14 + i * (w - 28) / 4
        s.append(cell_epithelial(xx, -h / 2 + h * 0.13, w=26, h=34, kind="columnar"))
    for i in range(3):
        xx = -w / 2 + 40 + i * (w - 80) / 2
        s.append(f'<circle cx="{xx:.1f}" cy="{h*0.18:.1f}" r="11" fill="{C["purple_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="1.4"/>')
    s.append(f'<path d="M {-w*0.2:.0f} {-h/2+h*0.44:.0f} C {-w*0.24:.0f} {h*0.2:.0f} {w*0.1:.0f} {h*0.26:.0f} {w*0.06:.0f} {-h/2+h*0.44:.0f}" '
             f'fill="none" stroke="{C["red"]}" stroke-width="4"/>')
    o = "".join(s)
    if label:
        o += text_el(0, -h / 2 - 12, label, 15)
    return _loc(x, y, o)


def villus(x, y, w=80, h=170, label=None):
    """小肠绒毛"""
    o = [f'<path d="M 0 {-h/2} C {w*0.42:.0f} {-h*0.3:.0f} {w*0.4:.0f} {h*0.34:.0f} 0 {h/2} '
         f'C {-w*0.4:.0f} {h*0.34:.0f} {-w*0.42:.0f} {-h*0.3:.0f} 0 {-h/2} Z" '
         f'fill="{C["yellow_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>',
         f'<path d="M 0 {-h/2+10} C {w*0.26:.0f} {-h*0.24:.0f} {w*0.24:.0f} {h*0.26:.0f} 0 {h/2-10}" '
         f'fill="none" stroke="{C["red"]}" stroke-width="3.4"/>']
    for i in range(4):
        yy = -h / 2 + 26 + i * (h - 50) / 3
        o.append(f'<circle cx="{(6 if i%2 else -6):.1f}" cy="{yy:.1f}" r="7" fill="{C["purple_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="1.3"/>')
    out = "".join(o)
    if label:
        out += text_el(0, -h / 2 - 12, label, 14)
    return _loc(x, y, out)


def alveolus(x, y, r=52, label=None):
    o = [f'<circle r="{r}" fill="{C["blue_l"]}" opacity="0.45" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>',
         f'<path d="M {-r*0.5:.0f} {-r*0.5:.0f} C {-r*0.1:.0f} {-r*0.1:.0f} {r*0.3:.0f} {r*0.2:.0f} {r*0.55:.0f} {r*0.5:.0f}" '
         f'fill="none" stroke="{C["red"]}" stroke-width="4" stroke-linecap="round"/>',
         f'<path d="M {-r*0.55:.0f} {r*0.4:.0f} C {-r*0.1:.0f} {r*0.15:.0f} {r*0.2:.0f} {-r*0.3:.0f} {r*0.5:.0f} {-r*0.55:.0f}" '
         f'fill="none" stroke="{C["blue"]}" stroke-width="4" stroke-linecap="round"/>']
    out = "".join(o)
    if label:
        out += text_el(0, r + 22, label, 14)
    return _loc(x, y, out)


def nephron(x, y, label=None, w=240, h=120):
    s = [f'<circle cx="{-w/2+30}" cy="{-h/4}" r="26" fill="{C["brown" if "brown" in C else "orange_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.2"/>',
         f'<path d="M {-w/2+52} {-h/4} C {-w/2+90} {-h/4} {-w/2+90} {h/3} {-w/2+130} {h/3} '
         f'C {-w/2+170} {h/3} {-w/2+170} {-h/4} {-w/2+210} {-h/4} L {w/2-20} {-h/4}" '
         f'fill="none" stroke="{C["blue"]}" stroke-width="4" stroke-linecap="round"/>',
         f'<path d="M {-w/2+18} {-h/4-22} C {-w/2-6} {-h/4-30} {-w/2-10} {6} {-w/2+14} {8}" '
         f'fill="none" stroke="{C["red"]}" stroke-width="3.4"/>']
    o = "".join(s)
    if label:
        o += text_el(0, -h / 4 - 46, label, 14)
    return _loc(x, y, o)


def organ_heart(x, y, size=1.0, label=None):
    o = (f'<path d="M 0 46 C -50 6 -58 -34 -30 -48 C -12 -56 0 -40 0 -28 '
         f'C 0 -40 12 -56 30 -48 C 58 -34 50 6 0 46 Z" '
         f'fill="{C["red_l"]}" stroke="{C["red"]}" stroke-width="3"/>')
    if label:
        o += text_el(0, 74, label, 15)
    return _loc(x, y, o, scale=size)


def organ_brain(x, y, size=1.0, label=None):
    s = [f'<path d="M -52 12 C -62 -20 -36 -46 -6 -42 C 22 -50 54 -30 50 0 '
         f'C 58 20 34 40 8 36 C -14 46 -44 36 -52 12 Z" '
         f'fill="{C["purple_l"]}" stroke="{C["purple"]}" stroke-width="2.6"/>']
    for d in ("M -40 -14 C -30 -4 -34 8 -24 16", "M -16 -30 C -6 -18 -12 -2 0 8",
              "M 12 -32 C 22 -18 16 0 26 12", "M 32 -18 C 40 -8 36 4 30 12"):
        s.append(f'<path d="{d}" fill="none" stroke="{C["purple"]}" stroke-width="2" opacity="0.6"/>')
    o = "".join(s)
    if label:
        o += text_el(0, 66, label, 15)
    return _loc(x, y, o, scale=size)


# ---- 实验室 LAB -------------------------------------------------------------
def microtube(x, y, h=70, label=None, fill=None, cap_color=None):
    fill = fill or "none"
    s = [f'<path d="M -13 {-h/2+12} L 13 {-h/2+12} L 9 {h/2-4} L -9 {h/2-4} Z" fill="{fill}" stroke="{DEFAULT_STROKE}" stroke-width="2.2"/>',
         f'<rect x="-11" y="{-h/2-8}" width="22" height="20" rx="4" fill="{cap_color or C["orange"]}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>']
    if fill != "none":
        s.append(f'<path d="M -9 {h/2-20} L 9 {h/2-20} L 9 {h/2-5} L -9 {h/2-5} Z" fill="{fill}" opacity="0.85"/>')
    o = "".join(s)
    if label:
        o += text_el(0, h / 2 + 20, label, 13)
    return _loc(x, y, o)


def petri_dish(x, y, r=56, label=None, colonies=5, fill=None):
    s = [f'<circle r="{r}" fill="{fill or C["yellow_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>',
         f'<circle r="{r-6}" fill="none" stroke="#FFFFFF" stroke-width="1.4" opacity="0.8"/>']
    import random as _r, zlib as _z
    # 用稳定哈希做种子: 内置 hash() 每次进程随机, 会导致同一图每次生成结果不同
    _r.seed(_z.crc32(str(label or "petri").encode("utf-8")))
    for i in range(colonies):
        a = _r.random() * math.pi * 2
        d = _r.random() * (r - 20)
        rr = 4 + _r.random() * 5
        s.append(f'<circle cx="{d*math.cos(a):.1f}" cy="{d*math.sin(a):.1f}" r="{rr:.1f}" fill="{C["gray"]}" opacity="0.7"/>')
    o = "".join(s)
    if label:
        o += text_el(0, r + 22, label, 14)
    return _loc(x, y, o)


def culture_flask(x, y, w=130, h=85, label=None, fill=None):
    o = [f'<path d="M {-w/2+34} {-h/2} L {w/2-8} {-h/2} L {w/2-8} {h/2-16} L {-w/2+10} {h/2-16} L {-w/2+10} {-h/2+18} L {-w/2+34} {-h/2+18} Z" '
         f'fill="none" stroke="{DEFAULT_STROKE}" stroke-width="2.4"/>',
         f'<path d="M {-w/2+13} {-h/2+22} L {w/2-11} {-h/2+22} L {w/2-11} {h/2-19} L {-w/2+13} {h/2-19} Z" '
         f'fill="{fill or C["red_l"]}" opacity="0.8"/>',
         f'<rect x="{-w/2+30}" y="{-h/2-6}" width="14" height="8" fill="{DEFAULT_STROKE}"/>']
    out = "".join(o)
    if label:
        out += text_el(0, h / 2 + 18, label, 13)
    return _loc(x, y, out)


def well_plate(x, y, rows=3, cols=4, r=13, label=None, well_colors=None):
    s = []
    total_w = cols * (2 * r + 9)
    total_h = rows * (2 * r + 9)
    for i in range(rows):
        for j in range(cols):
            cx = -total_w / 2 + r + 4.5 + j * (2 * r + 9)
            cy = -total_h / 2 + r + 4.5 + i * (2 * r + 9)
            cc = (well_colors or {}).get(f"{chr(65+i)}{j+1}", C["blue_l"])
            s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{cc}" stroke="{DEFAULT_STROKE}" stroke-width="1.8"/>')
    o = "".join(s)
    if label:
        o += text_el(0, total_h / 2 + 24, label, 14)
    return _loc(x, y, o)


def syringe(x, y, length=150, angle=0, label=None):
    o = [f'<rect x="{-length/2}" y="-11" width="{length*0.6:.0f}" height="22" rx="4" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="2.2"/>',
         f'<rect x="{length*0.1:.0f}" y="-4" width="{length*0.34:.0f}" height="8" fill="{C["gray"]}"/>',
         f'<rect x="{-length/2-14}" y="-14" width="14" height="28" rx="3" fill="{C["gray_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>',
         f'<line x1="{-length/2-26}" y1="0" x2="{-length/2-12}" y2="0" stroke="{DEFAULT_STROKE}" stroke-width="3.4"/>',
         f'<path d="M {length*0.44:.0f} -6 L {length*0.5:.0f} 0 L {length*0.44:.0f} 6" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="2.2"/>']
    out = "".join(o)
    if label:
        out += text_el(0, -30, label, 13)
    return _loc(x, y, out, rotate=angle)


def gel_lanes(x, y, w=200, h=150, lanes=4, bands=None, label=None):
    """电泳凝胶; bands: {lane_index: [y位置列表(0顶部~1底部)]}"""
    bands = bands or {0: [0.2, 0.55], 1: [0.35, 0.7], 2: [0.2, 0.45, 0.8], 3: [0.6]}
    s = [f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" fill="{C["yellow_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.2"/>']
    lw = w / lanes
    for i in range(lanes):
        xx = -w / 2 + i * lw + lw / 2
        s.append(f'<line x1="{xx:.1f}" y1="{-h/2+8}" x2="{xx:.1f}" y2="{h/2-8}" stroke="{C["gray"]}" stroke-width="1" opacity="0.5"/>')
        for t in bands.get(i, []):
            yy = -h / 2 + 10 + t * (h - 20)
            s.append(f'<rect x="{xx-lw*0.28:.1f}" y="{yy-4:.1f}" width="{lw*0.56:.1f}" height="8" rx="3" fill="{C["ink"]}" opacity="0.82"/>')
    o = "".join(s)
    if label:
        o += text_el(0, -h / 2 - 12, label, 14)
    return _loc(x, y, o)


def microscope(x, y, label=None, h=110):
    o = [f'<path d="M -26 {-h/2+8} C -34 {-h/2+34} -20 {-h/2+52} -2 {-h/2+52}" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="9" stroke-linecap="round"/>',
         f'<rect x="{-14}" y="{-h/2-6}" width="20" height="40" rx="6" fill="{C["gray_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2.2" transform="rotate(18 -4 {-h/2+14})"/>',
         f'<rect x="{-20}" y="{-h/2+40}" width="52" height="10" rx="4" fill="{C["gray_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>',
         f'<rect x="{-34}" y="{-h/2+50}" width="84" height="12" rx="5" fill="{C["gray"]}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>']
    out = "".join(o)
    if label:
        out += text_el(0, h / 2 + 22, label, 13)
    return _loc(x, y, out)


def mouse_lab(x, y, size=1.0, label=None, color=None):
    """实验小鼠(侧视剪影)"""
    color = color or C["gray"]
    o = (f'<path d="M 30 -6 C 38 -18 52 -16 56 -6 C 60 2 54 10 44 10 '
         f'L -18 10 C -30 10 -36 0 -30 -8 C -22 -18 6 -18 16 -8 '
         f'C 20 -12 26 -12 30 -6 Z" fill="{color}" opacity="0.85"/>'
         f'<circle cx="49" cy="-13" r="5" fill="{color}"/>'
         f'<circle cx="50.5" cy="-13.5" r="1.4" fill="#FFFFFF"/>'
         f'<path d="M -30 -6 C -44 -14 -50 -2 -40 6" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round"/>'
         f'<circle cx="36" cy="-4" r="6.5" fill="#FFFFFF" opacity="0.28"/>')
    if label:
        o += text_el(0, 34, label, 13)
    return _loc(x, y, o, scale=size)


def human_silhouette(x, y, h=140, label=None):
    s = h / 140.0
    o = (f'<circle cx="0" cy="{-46*s:.1f}" r="{15*s:.1f}" fill="{C["blue"]}" opacity="0.85"/>'
         f'<path d="M {-13*s:.1f} {-28*s:.1f} C {-24*s:.1f} {-22*s:.1f} {-22*s:.1f} {4*s:.1f} {-18*s:.1f} {30*s:.1f} '
         f'L {-8*s:.1f} {30*s:.1f} L {-8*s:.1f} {62*s:.1f} L {8*s:.1f} {62*s:.1f} L {8*s:.1f} {30*s:.1f} '
         f'L {18*s:.1f} {30*s:.1f} C {22*s:.1f} {4*s:.1f} {24*s:.1f} {-22*s:.1f} {13*s:.1f} {-28*s:.1f} Z" '
         f'fill="{C["blue"]}" opacity="0.85"/>')
    if label:
        o += text_el(0, h / 2 + 22, label, 13)
    return _loc(x, y, o)


def tube_rack(x, y, n=4, label=None):
    s = [f'<rect x="{-n*20-6}" y="-30" width="{n*40+12}" height="62" rx="4" fill="{C["gray_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>']
    cols = [C["orange"], C["teal"], C["red"], C["blue"], C["green"], C["purple"]]
    for i in range(n):
        xx = -n * 20 + 10 + i * 40
        s.append(f'<rect x="{xx-11}" y="-40" width="22" height="52" rx="4" fill="#FFFFFF" stroke="{DEFAULT_STROKE}" stroke-width="1.8"/>')
        s.append(f'<rect x="{xx-8}" y="{4}" width="16" height="8" fill="{cols[i%6]}" opacity="0.85"/>')
    o = "".join(s)
    if label:
        o += text_el(0, 54, label, 13)
    return _loc(x, y, o)


# ---- 寄生虫与病原微生物 PARASITES & MICROBES ---------------------------------
def _poly_leg(pts, color=None, width=2.6):
    """节肢动物分节腿: 折线段"""
    d = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts)
    return f'<path d="{d}" fill="none" stroke="{color or DEFAULT_STROKE}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'


def mite(x, y, w=80, label=None, color=None):
    """螨虫(背视): 卵圆躯体+颚体+4对分节腿, 尘螨/疥螨通用画法"""
    s = w / 80.0
    color = color or "#DDB892"
    o = []
    # 躯体(分前体/后体)
    o.append(f'<ellipse cx="0" cy="0" rx="{34*s:.1f}" ry="{26*s:.1f}" fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="2.2"/>')
    # 横向几丁质纹
    for i in range(5):
        xx = (-20 + i * 10) * s
        o.append(f'<path d="M {xx:.1f} {-20*s:.1f} Q {xx+3*s:.1f} 0 {xx:.1f} {20*s:.1f}" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="1" opacity="0.5"/>')
    # 颚体(口器) + 触肢
    o.append(f'<rect x="{-6*s:.1f}" y="{-34*s:.1f}" width="{12*s:.1f}" height="{10*s:.1f}" rx="{4*s:.1f}" fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>')
    o.append(f'<path d="M {-7*s:.1f} {-30*s:.1f} L {-14*s:.1f} {-36*s:.1f}" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="{2*s:.1f}" stroke-linecap="round"/>')
    o.append(f'<path d="M {7*s:.1f} {-30*s:.1f} L {14*s:.1f} {-36*s:.1f}" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="{2*s:.1f}" stroke-linecap="round"/>')
    # 4 对腿(前对最长, 分节): (根部x, 根部y) -> (肘点x, 肘点y, 足尖x, 足尖y), 相对系数
    legs = ((-24, -14, -44, -34, -52, -12), (-27, -4, -46, -18, -54, 8),
            (-25, 6, -44, 10, -50, 28), (-20, 16, -38, 30, -44, 46))
    for side in (-1, 1):
        for (bx, by, jx, jy, tx, ty) in legs:
            p0 = (side * bx * s, by * s)
            p1 = (side * jx * s, jy * s + by * s * 0.4)
            p2 = (side * tx * s, ty * s)
            o.append(_poly_leg([p0, p1, p2], width=2.4 * s))
    out = "".join(o)
    if label:
        out += text_el(0, 40 * s, label, 13)
    return _loc(x, y, out, scale=s)


def tick(x, y, w=90, label=None, color=None, engorged=False):
    """硬蜱(背视): 扁平假体+盾板+颚体+4对前伸腿; engorged=饱血蜱(躯体膨大)"""
    s = w / 90.0
    color = color or "#B08D57"
    rx, ry = (44 * s, 34 * s) if engorged else (30 * s, 24 * s)
    o = []
    o.append(f'<ellipse cx="{-8*s:.1f}" cy="0" rx="{rx:.1f}" ry="{ry:.1f}" fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="2.2"/>')
    if not engorged:  # 盾板(前背部的几丁质板, 实色近似避免半透明渲染差异)
        o.append(f'<ellipse cx="{-2*s:.1f}" cy="0" rx="{16*s:.1f}" ry="{13*s:.1f}" fill="#8F7A57" stroke="#7C6A4A" stroke-width="1.2"/>')
    else:  # 饱血: 皱褶纹
        for i in range(4):
            xx = (-18 + i * 14) * s
            o.append(f'<path d="M {xx:.1f} {-24*s:.1f} Q {xx+4*s:.1f} 0 {xx:.1f} {24*s:.1f}" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="1" opacity="0.45"/>')
    # 颚体(假头) + 触肢
    o.append(f'<path d="M {-rx-8*s:.1f} {-6*s:.1f} L {-rx-22*s:.1f} {-8*s:.1f} L {-rx-22*s:.1f} {8*s:.1f} L {-rx-8*s:.1f} {6*s:.1f} Z" fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>')
    o.append(f'<path d="M {-rx-20*s:.1f} {-9*s:.1f} L {-rx-30*s:.1f} {-14*s:.1f}" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="2" stroke-linecap="round"/>')
    o.append(f'<path d="M {-rx-20*s:.1f} {9*s:.1f} L {-rx-30*s:.1f} {14*s:.1f}" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="2" stroke-linecap="round"/>')
    # 4 对腿(伸向前方两侧, 蜱的典型姿态): 根部->膝点->足尖
    for side in (-1, 1):
        for (bx, jx, jy, tx, ty) in ((-14, -30, -26, -40, -34), (-4, -24, -12, -34, -18),
                                      (8, -18, 2, -28, 2), (20, -14, 14, -22, 22)):
            p0 = (side * bx * s, 6 * s)
            p1 = (side * jx * s, jy * s)
            p2 = (side * tx * s, ty * s)
            o.append(_poly_leg([p0, p1, p2], width=2.6 * s))
    out = "".join(o)
    if label:
        out += text_el(0, 48 * s, label, 13)
    return _loc(x, y, out, scale=s)


def flea(x, y, h=70, label=None, color=None):
    """跳蚤(侧视): 侧扁体+刺栉+3对腿(后对发达)"""
    s = h / 70.0
    color = color or "#8D6E4B"
    o = []
    # 体: 头小圆 + 胸腹侧扁大弧
    o.append(f'<path d="M -22 {-14*s:.1f} C -34 {-10*s:.1f} -36 {2*s:.1f} -26 {6*s:.1f} '
             f'C -18 {10*s:.1f} 14 {16*s:.1f} 24 {6*s:.1f} '
             f'C 34 {-2*s:.1f} 32 {-18*s:.1f} 16 {-22*s:.1f} '
             f'C 2 {-26*s:.1f} -12 {-20*s:.1f} -22 {-14*s:.1f} Z" '
             f'fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="2.2"/>')
    # 头 + 眼 + 触角
    o.append(f'<circle cx="{-26*s:.1f}" cy="{-4*s:.1f}" r="{7*s:.1f}" fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>')
    o.append(f'<circle cx="{-27*s:.1f}" cy="{-6*s:.1f}" r="{1.6*s:.1f}" fill="{C["ink"]}"/>')
    o.append(f'<path d="M {-22*s:.1f} {-10*s:.1f} Q {-16*s:.1f} {-22*s:.1f} {-8*s:.1f} {-24*s:.1f}" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="1.6" stroke-linecap="round"/>')
    # 颊/前胸刺栉(背缘小棘)
    for i in range(4):
        xx = (-6 + i * 8) * s
        yy = (-22.5 + i * 0.6) * s
        o.append(f'<path d="M {xx:.1f} {yy:.1f} L {xx:.1f} {yy-5*s:.1f}" stroke="{DEFAULT_STROKE}" stroke-width="1.4" stroke-linecap="round"/>')
    # 体节纹
    for i in range(3):
        xx = (4 + i * 9) * s
        o.append(f'<path d="M {xx:.1f} {-20*s:.1f} Q {xx+4*s:.1f} {-4*s:.1f} {xx:.1f} {10*s:.1f}" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="1" opacity="0.5"/>')
    # 3 对腿(后腿最粗大)
    for (bx, by, kx, ky, fx, fy, wd) in ((-20, 4, -26, 16, -12, 22, 2.2), (-10, 8, -12, 22, 4, 28, 2.4),
                                          (6, 8, 2, 24, 20, 30, 3.4)):
        o.append(_poly_leg([(bx * s, by * s), (kx * s, ky * s), (fx * s, fy * s)], width=wd * s))
    out = "".join(o)
    if label:
        out += text_el(0, 46 * s, label, 13)
    return _loc(x, y, out, scale=s)


def mosquito(x, y, h=120, label=None, color=None):
    """蚊子(侧视): 刺吸式长喙+双翅+细长节肢腿"""
    s = h / 120.0
    color = color or C["gray"]
    o = []
    # 腹部(细长带节)
    o.append(f'<path d="M 4 {-6*s:.1f} C 24 {-4*s:.1f} 52 {0} 62 {8*s:.1f} '
             f'C 52 {14*s:.1f} 24 {10*s:.1f} 4 {6*s:.1f} Z" fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>')
    for i in range(5):
        xx = (16 + i * 9) * s
        yy = (-3 + i * 2.4) * s
        o.append(f'<path d="M {xx:.1f} {yy:.1f} L {xx+2*s:.1f} {yy+7*s:.1f}" stroke="{DEFAULT_STROKE}" stroke-width="1" opacity="0.55"/>')
    # 胸 + 头
    o.append(f'<ellipse cx="{-8*s:.1f}" cy="{-4*s:.1f}" rx="{9*s:.1f}" ry="{8*s:.1f}" fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="2.2"/>')
    o.append(f'<circle cx="{-20*s:.1f}" cy="{-8*s:.1f}" r="{6*s:.1f}" fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>')
    # 长喙(刺吸式口器) + 触角
    o.append(f'<path d="M {-25*s:.1f} {-7*s:.1f} L {-46*s:.1f} {-12*s:.1f}" stroke="{DEFAULT_STROKE}" stroke-width="1.8" stroke-linecap="round"/>')
    o.append(f'<path d="M {-23*s:.1f} {-12*s:.1f} Q {-30*s:.1f} {-22*s:.1f} {-38*s:.1f} {-24*s:.1f}" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="1.4" stroke-linecap="round"/>')
    # 翅(两片, 后置)
    o.append(f'<ellipse cx="{6*s:.1f}" cy="{-20*s:.1f}" rx="{20*s:.1f}" ry="{6.5*s:.1f}" fill="{C["gray_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="1.6" transform="rotate(-18 {6*s:.1f} {-20*s:.1f})"/>')
    o.append(f'<ellipse cx="{10*s:.1f}" cy="{-14*s:.1f}" rx="{16*s:.1f}" ry="{5*s:.1f}" fill="{C["gray_l"]}" stroke="{DEFAULT_STROKE}" stroke-width="1.4" transform="rotate(-8 {10*s:.1f} {-14*s:.1f})"/>')
    # 6 条细长腿(前中后, 细折线)
    for (bx, by, pts) in ((-12, 0, [(-24, 8), (-34, 26)]), (-6, 2, [(-10, 22), (-22, 40)]),
                           (0, 3, [(2, 26), (-2, 46)]), (4, 2, [(16, 20), (28, 36)]),
                           (8, 0, [(24, 12), (42, 20)])):
        o.append(_poly_leg([(bx * s, by * s)] + [(px * s, py * s) for px, py in pts], width=1.8 * s))
    out = "".join(o)
    if label:
        out += text_el(0, 62 * s, label, 13)
    return _loc(x, y, out, scale=s)


def roundworm(x, y, w=190, label=None, color=None):
    """蛔虫(线虫): 两端尖细的长圆柱体, 角皮横纹"""
    s = w / 190.0
    color = color or "#E8B88A"
    hw = 7 * s  # 半宽
    o = (f'<path d="M {-95*s:.1f} 0 C {-80*s:.1f} {-hw-3*s:.1f} {-40*s:.1f} {-hw} 0 {-hw} '
         f'C {45*s:.1f} {-hw} {85*s:.1f} {-hw-3*s:.1f} {95*s:.1f} 0 '
         f'C {85*s:.1f} {hw+3*s:.1f} {45*s:.1f} {hw} 0 {hw} '
         f'C {-40*s:.1f} {hw} {-80*s:.1f} {hw+3*s:.1f} {-95*s:.1f} 0 Z" '
         f'fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="2.2"/>')
    for i in range(11):
        xx = (-75 + i * 15) * s
        t = abs(xx) / (95 * s)
        hh = hw * (1 - 0.55 * t * t) - 1.5 * s
        o += f'<path d="M {xx:.1f} {-hh:.1f} L {xx:.1f} {hh:.1f}" stroke="{DEFAULT_STROKE}" stroke-width="1" opacity="0.5"/>'
    # 口部三点 + 排泄孔
    o += (f'<circle cx="{-95*s:.1f}" cy="{-2.5*s:.1f}" r="{1.4*s:.1f}" fill="{DEFAULT_STROKE}"/>'
          f'<circle cx="{-95*s:.1f}" cy="{2.5*s:.1f}" r="{1.4*s:.1f}" fill="{DEFAULT_STROKE}"/>')
    o = o if isinstance(o, str) else "".join(o)
    if label:
        o += text_el(0, 28 * s, label, 13)
    return _loc(x, y, o)


def tapeworm(x, y, w=190, label=None, color=None):
    """绦虫: 头节(吸盘+小钩)+颈节+成熟/孕卵节片链"""
    s = w / 190.0
    color = color or "#EAD9C2"
    o = []
    # 头节: 球形 + 4 吸盘 + 顶突小钩
    o.append(f'<circle cx="{-84*s:.1f}" cy="0" r="{9*s:.1f}" fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>')
    for dx, dy in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
        o.append(f'<circle cx="{(-84+dx)*s:.1f}" cy="{dy*s:.1f}" r="{3*s:.1f}" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="1.2"/>')
    for i in range(5):
        a = -140 + i * 20
        ax = math.radians(a)
        o.append(f'<path d="M {(-84+9*math.cos(ax))*s:.1f} {9*math.sin(ax)*s:.1f} L {(-84+13*math.cos(ax))*s:.1f} {13*math.sin(ax)*s:.1f}" stroke="{DEFAULT_STROKE}" stroke-width="1.2" stroke-linecap="round"/>')
    # 颈节 -> 节片链(宽度渐增, 节片首尾相接成连续 ribbon)
    n = 8
    seg_w = (168 * s) / n
    for i in range(n):
        x0 = -76 * s + i * seg_w
        x1 = x0 + seg_w
        grow = min(1.0, 0.3 + 0.14 * i)
        hh = (4 + 10 * grow) * s
        xm = (x0 + x1) / 2
        o.append(f'<path d="M {x0:.1f} 0 C {(x0+seg_w*0.2):.1f} {-hh:.1f} {(x1-seg_w*0.2):.1f} {-hh:.1f} {x1:.1f} 0 '
                 f'C {(x1-seg_w*0.2):.1f} {hh:.1f} {(x0+seg_w*0.2):.1f} {hh:.1f} {x0:.1f} 0 Z" '
                 f'fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="1.8"/>')
        # 生殖孔 + 孕卵节子宫分枝
        if i < n - 2:
            o.append(f'<circle cx="{xm+seg_w*0.05:.1f}" cy="{(-hh+3)*s:.1f}" r="{1.2*s:.1f}" fill="{DEFAULT_STROKE}"/>')
        else:
            o.append(f'<path d="M {x0+3*s:.1f} 0 L {x1-3*s:.1f} 0 M {x0+7*s:.1f} {-3*s:.1f} L {x1-7*s:.1f} {-3*s:.1f} M {x0+7*s:.1f} {3*s:.1f} L {x1-7*s:.1f} {3*s:.1f}" '
                     f'stroke="{DEFAULT_STROKE}" stroke-width="1" fill="none" opacity="0.6"/>')
    out = "".join(o)
    if label:
        out += text_el(0, 26 * s, label, 13)
    return _loc(x, y, out, scale=s)


def schistosome(x, y, w=150, label=None, color=None):
    """血吸虫(雌雄合抱): 雄虫抱雌沟容纳细长雌虫"""
    s = w / 150.0
    mc = color or "#C9906B"
    fc = "#B06E4E"
    o = []
    # 雄虫: 粗短体, 前端口吸盘/腹吸盘, 体侧展开成抱雌沟
    o.append(f'<path d="M {-75*s:.1f} 0 C {-70*s:.1f} {-14*s:.1f} {-40*s:.1f} {-18*s:.1f} {-10*s:.1f} {-16*s:.1f} '
             f'C {30*s:.1f} {-14*s:.1f} {66*s:.1f} {-10*s:.1f} {70*s:.1f} 0 '
             f'C {66*s:.1f} {10*s:.1f} {30*s:.1f} {14*s:.1f} {-10*s:.1f} {16*s:.1f} '
             f'C {-40*s:.1f} {18*s:.1f} {-70*s:.1f} {14*s:.1f} {-75*s:.1f} 0 Z" '
             f'fill="{mc}" stroke="{DEFAULT_STROKE}" stroke-width="2.2"/>')
    o.append(f'<circle cx="{-62*s:.1f}" cy="0" r="{6*s:.1f}" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="1.6"/>')   # 口吸盘
    o.append(f'<circle cx="{-44*s:.1f}" cy="0" r="{5*s:.1f}" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="1.6"/>')   # 腹吸盘
    # 抱雌沟开口(中线缝隙)
    o.append(f'<path d="M {-30*s:.1f} 0 L {64*s:.1f} 0" stroke="{C["paper"]}" stroke-width="{5*s:.1f}" stroke-linecap="round"/>')
    # 雌虫(细长, 半悬于抱雌沟)
    o.append(f'<path d="M {-36*s:.1f} 0 C {0} {-4*s:.1f} {40*s:.1f} {-2*s:.1f} {76*s:.1f} {-5*s:.1f} '
             f'C {40*s:.1f} {3*s:.1f} {0} {4*s:.1f} {-36*s:.1f} 0 Z" '
             f'fill="{fc}" stroke="{DEFAULT_STROKE}" stroke-width="1.6"/>')
    out = "".join(o)
    if label:
        out += text_el(0, 30 * s, label, 13)
    return _loc(x, y, out, scale=s)


def plasmodium_rbc(x, y, r=32, label=None, n=2, color=None):
    """疟原虫红内期: 红细胞内的环状体(戒指期)"""
    o = [f'<circle cx="0" cy="0" r="{r}" fill="#F6C8C4" stroke="{DEFAULT_STROKE}" stroke-width="2"/>',
         f'<circle cx="0" cy="0" r="{r*0.55:.1f}" fill="#F9DAD7"/>']  # 红细胞凹心
    positions = [(-r * 0.35, -r * 0.25), (r * 0.35, r * 0.3), (-r * 0.3, r * 0.42),
                 (r * 0.42, -r * 0.35), (0, r * 0.55), (0, -r * 0.55)][:max(1, n)]
    rr = r * 0.24
    for i, (cx, cy) in enumerate(positions):
        # 环状体: 细胞质细环 + 环缘上的染色质浓点(经典"戒指"画法)
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rr:.1f}" fill="none" stroke="#7B3FA0" stroke-width="{rr*0.32:.1f}"/>')
        a = math.radians(40 + i * 75)
        o.append(f'<circle cx="{cx+rr*math.cos(a):.1f}" cy="{cy+rr*math.sin(a):.1f}" r="{rr*0.34:.1f}" fill="#7B3FA0"/>')
    out = "".join(o)
    if label:
        out += text_el(0, r + 18, label, 13)
    return _loc(x, y, out)


def giardia(x, y, w=64, label=None, color=None):
    """贾第鞭毛虫滋养体: 梨形+双核+腹吸盘+4对鞭毛"""
    s = w / 64.0
    color = color or "#9FD0B5"
    o = []
    # 梨形虫体(前端宽圆, 后端细尖)
    o.append(f'<path d="M 0 {-24*s:.1f} C {14*s:.1f} {-24*s:.1f} {20*s:.1f} {-8*s:.1f} {13*s:.1f} {18*s:.1f} '
             f'C {9*s:.1f} {30*s:.1f} {-9*s:.1f} {30*s:.1f} {-13*s:.1f} {18*s:.1f} '
             f'C {-20*s:.1f} {-8*s:.1f} {-14*s:.1f} {-24*s:.1f} 0 {-24*s:.1f} Z" '
             f'fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>')
    # 背面双核
    for side in (-1, 1):
        o.append(f'<circle cx="{side*5.5*s:.1f}" cy="{-13*s:.1f}" r="{3.4*s:.1f}" fill="#FFFFFF" stroke="{DEFAULT_STROKE}" stroke-width="1.4"/>')
        o.append(f'<circle cx="{side*5.5*s:.1f}" cy="{-13*s:.1f}" r="{1.3*s:.1f}" fill="{C["ink"]}"/>')
    # 腹吸盘(前腹面圆盘)
    o.append(f'<ellipse cx="0" cy="{-2*s:.1f}" rx="{8.5*s:.1f}" ry="{7*s:.1f}" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="1.4"/>')
    # 中轴(轴柱) + 副基体
    o.append(f'<path d="M 0 {2*s:.1f} L 0 {24*s:.1f}" stroke="{DEFAULT_STROKE}" stroke-width="1.4"/>')
    # 4 对鞭毛(前/中/腹/尾)
    for (x0, y0, x1, y1, x2, y2) in ((-8, -20, -20, -30, -30, -28), (8, -20, 20, -30, 30, -28),
                                      (-10, -2, -24, 8, -34, 6), (10, -2, 24, 8, 34, 6),
                                      (-8, 12, -18, 26, -26, 38), (8, 12, 18, 26, 26, 38),
                                      (-2, 26, -4, 36, -6, 48), (2, 26, 4, 36, 6, 48)):
        o.append(_poly_leg([(x0 * s, y0 * s), (x1 * s, y1 * s), (x2 * s, y2 * s)], width=1.3 * s))
    out = "".join(o)
    if label:
        out += text_el(0, 58 * s, label, 13)
    return _loc(x, y, out, scale=s)


def amoeba(x, y, r=42, label=None, color=None):
    """阿米巴原虫: 不规则外形+伪足+核+食物泡"""
    s = r / 42.0
    color = color or "#A9C7E8"
    o = (f'<path d="M {-20*s:.1f} {-18*s:.1f} C {-34*s:.1f} {-14*s:.1f} {-42*s:.1f} {-26*s:.1f} {-40*s:.1f} {-10*s:.1f} '
         f'C {-39*s:.1f} {0} {-30*s:.1f} {4*s:.1f} {-36*s:.1f} {14*s:.1f} '
         f'C {-42*s:.1f} {24*s:.1f} {-24*s:.1f} {30*s:.1f} {-14*s:.1f} {24*s:.1f} '
         f'C {-4*s:.1f} {18*s:.1f} {6*s:.1f} {34*s:.1f} {16*s:.1f} {30*s:.1f} '
         f'C {26*s:.1f} {26*s:.1f} {20*s:.1f} {12*s:.1f} {30*s:.1f} {6*s:.1f} '
         f'C {42*s:.1f} {-2*s:.1f} {32*s:.1f} {-18*s:.1f} {20*s:.1f} {-16*s:.1f} '
         f'C {10*s:.1f} {-15*s:.1f} {12*s:.1f} {-30*s:.1f} {0} {-28*s:.1f} '
         f'C {-8*s:.1f} {-26*s:.1f} {-12*s:.1f} {-20*s:.1f} {-20*s:.1f} {-18*s:.1f} Z" '
         f'fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="2.2"/>'
         f'<circle cx="{-8*s:.1f}" cy="{-4*s:.1f}" r="{7*s:.1f}" fill="#FFFFFF" stroke="{DEFAULT_STROKE}" stroke-width="1.6"/>'
         f'<circle cx="{-8*s:.1f}" cy="{-4*s:.1f}" r="{2.6*s:.1f}" fill="{C["ink"]}"/>'
         f'<circle cx="{14*s:.1f}" cy="{10*s:.1f}" r="{5*s:.1f}" fill="#FFFFFF" stroke="{DEFAULT_STROKE}" stroke-width="1.2"/>'
         f'<circle cx="{2*s:.1f}" cy="{16*s:.1f}" r="{3.4*s:.1f}" fill="#FFFFFF" stroke="{DEFAULT_STROKE}" stroke-width="1.2"/>')
    if label:
        o += text_el(0, r + 24 * s, label, 13)
    return _loc(x, y, o)


def yeast(x, y, r=26, label=None, budding=True, color=None):
    """酵母菌: 椭圆细胞+芽体+芽痕"""
    s = r / 26.0
    color = color or "#E6D3A3"
    o = [f'<ellipse cx="0" cy="0" rx="{24*s:.1f}" ry="{18*s:.1f}" fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="2.2"/>']
    # 细胞壁内缘 + 核 + 液泡
    o.append(f'<ellipse cx="0" cy="0" rx="{21*s:.1f}" ry="{15*s:.1f}" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="0.8" opacity="0.4"/>')
    o.append(f'<circle cx="{-7*s:.1f}" cy="{-3*s:.1f}" r="{4.6*s:.1f}" fill="#FFFFFF" stroke="{DEFAULT_STROKE}" stroke-width="1.4"/>')
    o.append(f'<circle cx="{-7*s:.1f}" cy="{-3*s:.1f}" r="{1.7*s:.1f}" fill="{C["ink"]}"/>')
    o.append(f'<circle cx="{9*s:.1f}" cy="{4*s:.1f}" r="{5*s:.1f}" fill="#FFFFFF" stroke="{DEFAULT_STROKE}" stroke-width="1.1"/>')
    if budding:  # 出芽
        o.append(f'<ellipse cx="{27*s:.1f}" cy="{-9*s:.1f}" rx="{10*s:.1f}" ry="{8*s:.1f}" fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>')
        o.append(f'<circle cx="{30*s:.1f}" cy="{-11*s:.1f}" r="{2.2*s:.1f}" fill="#FFFFFF" stroke="{DEFAULT_STROKE}" stroke-width="1.1"/>')
        o.append(f'<path d="M {21*s:.1f} {-4*s:.1f} Q {24*s:.1f} {-7*s:.1f} {24*s:.1f} {-10*s:.1f}" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="1.6"/>')
    out = "".join(o)
    if label:
        out += text_el(0, 34 * s, label, 13)
    return _loc(x, y, out, scale=s)


def aspergillus(x, y, h=120, label=None, color=None):
    """曲霉: 足细胞+分生孢子梗+顶囊+放射状分生孢子链"""
    s = h / 120.0
    color = color or "#C7D97B"
    top = -46 * s
    o = [f'<path d="M {-6*s:.1f} {52*s:.1f} Q 0 {30*s:.1f} 0 {top+8*s:.1f}" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="{4.5*s:.1f}" stroke-linecap="round"/>',
         f'<ellipse cx="0" cy="{top:.1f}" rx="{9*s:.1f}" ry="{8*s:.1f}" fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="2"/>']
    # 放射状梗基+孢子链
    for i in range(9):
        a = math.radians(-160 + i * 20)
        for chain in (0, 1):
            a2 = a + (-0.09 if chain == 0 else 0.09)
            x1, y1 = 10 * s * math.cos(a2) * 1.15, top + 10 * s * math.sin(a2) * 1.05
            for k in range(1, 4):
                cx, cy = x1 * (1 + 0.52 * k), y1 + 0 * k
                cx = (10 + 5.2 * k) * s * math.cos(a2)
                cy = top + (10 + 5.2 * k) * s * math.sin(a2) * 1.0
                o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{3.4*s:.1f}" fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="1.2"/>')
    out = "".join(o)
    if label:
        out += text_el(0, 74 * s, label, 13)
    return _loc(x, y, out, scale=s)


def staphylococcus(x, y, r=40, label=None, n=11, color=None):
    """葡萄球菌: 球菌串集成葡萄串状"""
    s = r / 40.0
    color = color or "#C9A7D8"
    # 确定性葡萄串布局(相对半径比例)
    layout = ((0, 0, 9), (14, -6, 8), (-13, 7, 8), (5, 15, 7.5), (-8, -12, 7),
              (16, 9, 7), (-20, -2, 6.5), (10, -18, 6.5), (-4, 24, 6), (24, -14, 5.5), (-19, 18, 5.5))
    o = []
    for i, (cx, cy, cr) in enumerate(layout[:max(3, n)]):
        o.append(f'<circle cx="{cx*s:.1f}" cy="{cy*s:.1f}" r="{cr*s:.1f}" fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="1.8"/>')
        o.append(f'<circle cx="{(cx-2)*s:.1f}" cy="{(cy-2.5)*s:.1f}" r="{1.2*s:.1f}" fill="#FFFFFF" opacity="0.7"/>')
    out = "".join(o)
    if label:
        out += text_el(0, 40 * s, label, 13)
    return _loc(x, y, out, scale=s)


def streptococcus(x, y, length=120, label=None, n=7, color=None):
    """链球菌: 球菌沿弧形链排列"""
    s = length / 120.0
    color = color or "#C9A7D8"
    o = []
    for i in range(max(3, n)):
        t = i / max(1, n - 1)
        # 二次贝塞尔: P0(-52,10) P1(0,-22) P2(52,10)
        cx = ((1-t)**2 * -52 + 2*(1-t)*t * 0 + t**2 * 52) * s
        cy = ((1-t)**2 * 10 + 2*(1-t)*t * -22 + t**2 * 10) * s
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{7.5*s:.1f}" fill="{color}" stroke="{DEFAULT_STROKE}" stroke-width="1.8"/>')
        o.append(f'<circle cx="{(cx-2.2)*s:.1f}" cy="{(cy-2.6)*s:.1f}" r="{1.1*s:.1f}" fill="#FFFFFF" opacity="0.7"/>')
    out = "".join(o)
    if label:
        out += text_el(0, 34 * s, label, 13)
    return _loc(x, y, out, scale=s)


def spirochete(x, y, w=130, label=None, color=None, turns=4):
    """螺旋体(如梅毒螺旋体/钩端螺旋体): 规则螺旋细丝体"""
    s = w / 130.0
    color = color or "#B06E4E"
    pts = []
    for i in range(65):
        t = i / 64.0
        cx = (-60 + 120 * t) * s
        cy = -math.sin(t * math.pi * 2 * turns) * 10 * s
        taper = min(1.0, 0.25 + t * 2.2) if t < 0.4 else min(1.0, 1.0 - (t - 0.75) * 1.8)
        pts.append((cx, cy, max(0.6, 2.6 * taper)))
    o = []
    for i in range(len(pts) - 1):
        x0, y0, w0 = pts[i]
        x1, y1, _ = pts[i + 1]
        o.append(f'<path d="M {x0:.1f} {y0:.1f} L {x1:.1f} {y1:.1f}" stroke="{color}" stroke-width="{w0:.1f}" stroke-linecap="round"/>')
    # 内部轴丝示意
    o.append(f'<path d="M {-52*s:.1f} 0 Q 0 {-26*s:.1f} {52*s:.1f} 0" fill="none" stroke="{DEFAULT_STROKE}" stroke-width="0.9" opacity="0.45"/>')
    out = "".join(o)
    if label:
        out += text_el(0, 28 * s, label, 13)
    return _loc(x, y, out, scale=s)


# ---- 图解元素 DIAGRAM ELEMENTS ----------------------------------------------
def arrow(x, y, x2=None, y2=None, kind="activation", color=None, width=2.4,
          dash=None, label=None, curve=0.0, head_size=9):
    """箭头/信号线。
    kind: activation(实线箭头) | inhibition(T型) | translocation(虚线箭头)
          | bidirectional | binding(两点汇聚) | phosphorylation
    curve: 弯曲度(0=直线, >0 向上/侧弯)
    """
    color = color or DEFAULT_STROKE
    if x2 is None:
        x2, y2 = y, y  # 允许 arrow(x,y,dx=,dy=)? 这里保持显式坐标
        x2, y2 = x, y
    dx, dy = x2 - x, y2 - y
    L = math.hypot(dx, dy)
    ang = math.degrees(math.atan2(dy, dx))
    if curve:
        mx, my = (x + x2) / 2, (y + y2) / 2
        nx, ny = -dy / L, dx / L
        cxp, cyp = mx + nx * curve * L * 0.25, my + ny * curve * L * 0.25
        path = f'M {x} {y} Q {cxp:.1f} {cyp:.1f} {x2} {y2}'
        ang_end = math.degrees(math.atan2(y2 - cyp, x2 - cxp))
        p2 = (x2, y2)
    else:
        path = f'M {x} {y} L {x2} {y2}'
        ang_end = ang
        p2 = (x2, y2)
    s = [f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{width}" '
         f'stroke-linecap="round"' + (f' stroke-dasharray="{dash}"' if dash else "") + "/>"]
    pad = 6
    if kind == "activation":
        p1b, p2b = _line_pts((x, y), p2, 0, pad)
        if curve:
            s.append(_head(*p2, ang_end, head_size, color))
        else:
            s.append(_head(*p2b, ang, head_size, color))
    elif kind == "inhibition":
        if curve:
            tx, ty = p2
        else:
            tx, ty = _line_pts((x, y), p2, 0, pad)[1]
        perp = ang + 90
        for sgn in (1, -1):
            ex = tx + 9 * math.cos(math.radians(perp)) * sgn
            ey = ty + 9 * math.sin(math.radians(perp)) * sgn
            s.append(f'<line x1="{tx:.1f}" y1="{ty:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{color}" stroke-width="{width+0.6}" stroke-linecap="round"/>')
    elif kind == "translocation":
        p1b, p2b = _line_pts((x, y), p2, 0, pad)
        s.append(_head(*p2, ang_end, head_size, color))
    elif kind == "bidirectional":
        p1b, p2b = _line_pts((x, y), p2, pad, pad)
        s.append(_head(*p1b, ang + 180, head_size, color))
        s.append(_head(*p2b, ang, head_size, color))
    elif kind == "binding":
        pass
    out = "".join(s)
    if label:
        mx, my = (x + x2) / 2 + (nx * curve * L * 0.25 if curve else 0), (y + y2) / 2 - 14
        out += text_el(mx, my, label, 14, halo=4)
    return out


def leader_label(x, y, tx, ty, text, size=15, bold=False, color=None, dot=True):
    """带引线的标注"""
    s = [f'<line x1="{x}" y1="{y}" x2="{tx}" y2="{ty}" stroke="{C["gray"]}" stroke-width="1.4"/>']
    if dot:
        s.append(f'<circle cx="{x}" cy="{y}" r="2.6" fill="{C["gray"]}"/>')
    anchor = "start" if tx <= x else "end"
    s.append(text_el(tx + (6 if anchor == "start" else -6), ty + 5, text, size,
                     anchor=anchor, bold=bold, fill=color, halo=4))
    return "".join(s)


def title(x, y, text, size=26, bold=True, color=None, anchor="middle"):
    return text_el(x, y, text, size, bold=bold, fill=color, anchor=anchor)


def legend(x, y, items, size=14, swatch=18, col_gap=None, vertical=True, title_=None):
    """图例; items: [(颜色, 文本), ...]"""
    out = []
    cy = 0
    gap = max(size + 10, 24)
    if title_:
        out.append(text_el(0, 0, title_, size + 2, bold=True, anchor="start"))
        cy += gap + 2
    for color, lab in items:
        out.append(f'<rect x="0" y="{cy-size:.1f}" width="{swatch}" height="{size}" rx="3" fill="{color}" stroke="{C["gray"]}" stroke-width="1"/>')
        out.append(text_el(swatch + 9, cy, lab, size, anchor="start"))
        if vertical:
            cy += gap
        else:
            cx = col_gap or (swatch + 9 + len(str(lab)) * size * 0.62 + 26)
            out[-2] = out[-2]
            cy += 0
    if not vertical:
        pass
    return f'<g transform="translate({x},{y})">{"".join(out)}</g>'


def legend_row(x, y, items, size=14, swatch=18, gap=28, title_=None):
    """横向图例"""
    out, cx = [], 0
    if title_:
        out.append(text_el(0, 0, title_, size + 1, bold=True, anchor="start"))
        cx = (len(str(title_)) + 1) * size * 0.66
    for color, lab in items:
        out.append(f'<rect x="{cx:.1f}" y="{-size+3}" width="{swatch}" height="{size-4}" rx="3" fill="{color}" stroke="{C["gray"]}" stroke-width="1"/>')
        out.append(text_el(cx + swatch + 8, 0, lab, size, anchor="start"))
        cx += swatch + 8 + len(str(lab)) * size * 0.62 + gap
    return f'<g transform="translate({x},{y})">{"".join(out)}</g>'


def group_box(x, y, w, h, label=None, color=None, dash="7 5", fill=None):
    color = color or C["gray"]
    o = (f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" rx="14" fill="{fill or "none"}" '
         f'stroke="{color}" stroke-width="2" stroke-dasharray="{dash}"/>')
    if label:
        o += text_el(0, -h / 2 - 12, label, 15, bold=True, fill=color)
    return _loc(x, y, o)


def panel_letter(x, y, letter="A", size=30):
    return text_el(x, y, letter, size, bold=True, anchor="start")


def step_badge(x, y, n, r=15, color=None):
    color = color or C["blue"]
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>'
            + text_el(x, y + 6, str(n), 16, bold=True, fill="#FFFFFF"))


def scale_bar(x, y, length_px, text="10 μm", size=13):
    return (f'<line x1="{x}" y1="{y}" x2="{x+length_px}" y2="{y}" stroke="{C["ink"]}" stroke-width="2.6"/>'
            + f'<line x1="{x}" y1="{y-6}" x2="{x}" y2="{y+6}" stroke="{C["ink"]}" stroke-width="2.6"/>'
            + f'<line x1="{x+length_px}" y1="{y-6}" x2="{x+length_px}" y2="{y+6}" stroke="{C["ink"]}" stroke-width="2.6"/>'
            + text_el(x + length_px / 2, y - 12, text, size))


def membrane_boundary(x, y, w, h, label=None, rx=None, fill=None, color=None, dash=None):
    """细胞/区室边界框(圆角, 膜色)"""
    color = color or DEFAULT_STROKE
    rx = rx if rx is not None else min(w, h) / 3.2
    o = (f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" rx="{rx:.0f}" '
         f'fill="{fill or C["blue_l"]}" opacity="0.55" stroke="{color}" stroke-width="3"/>')
    if label:
        o += text_el(0, -h / 2 - 12, label, 16, bold=True)
    return _loc(x, y, o)


# ---------------------------------------------------------------- registry
LIBRARY = {
    # 亚细胞
    "nucleus": nucleus, "nucleolus": nucleolus, "mitochondrion": mitochondrion,
    "rough_er": rough_er, "smooth_er": smooth_er, "golgi": golgi,
    "lysosome": lysosome, "peroxisome": peroxisome, "ribosome": ribosome,
    "centriole": centriole, "vesicle": vesicle, "autophagosome": autophagosome,
    "chloroplast": chloroplast, "cytoskeleton": cytoskeleton,
    "membrane_patch": membrane_patch, "cell_generic": cell_generic,
    "cell_wall_plant": cell_wall_plant, "membrane_boundary": membrane_boundary,
    # 核酸
    "dna_helix": dna_helix, "dna_linear": dna_linear, "mrna": mrna, "trna": trna,
    "plasmid": plasmid, "chromosome": chromosome, "nucleosome": nucleosome,
    "gene_cassette": gene_cassette,
    # 蛋白
    "protein_blob": protein_blob, "receptor_tmembrane": receptor_tmembrane,
    "gpcr": gpcr, "ion_channel": ion_channel, "antibody_igg": antibody_igg,
    "enzyme_lock_key": enzyme_lock_key, "phosphate": phosphate,
    "atp_adp": atp_adp, "ion_dot": ion_dot, "ubiquitin_tag": ubiquitin_tag,
    "proteasome": proteasome,
    # 细胞
    "cell_epithelial": cell_epithelial, "fibroblast": fibroblast,
    "adipocyte": adipocyte, "macrophage": macrophage, "neutrophil": neutrophil,
    "lymphocyte": lymphocyte, "rbc": rbc, "platelet": platelet,
    "neuron": neuron, "muscle_fiber": muscle_fiber, "sperm": sperm,
    "oocyte": oocyte, "blastocyst": blastocyst, "cancer_cell": cancer_cell,
    "bacterium": bacterium, "virus_enveloped": virus_enveloped,
    "virus_icosa": virus_icosa, "bacteriophage": bacteriophage,
    "mite": mite, "tick": tick, "flea": flea, "mosquito": mosquito,
    "roundworm": roundworm, "tapeworm": tapeworm, "schistosome": schistosome,
    "plasmodium_rbc": plasmodium_rbc, "giardia": giardia, "amoeba": amoeba,
    "yeast": yeast, "aspergillus": aspergillus, "staphylococcus": staphylococcus,
    "streptococcus": streptococcus, "spirochete": spirochete,
    # 组织/器官
    "skin_section": skin_section, "villus": villus, "alveolus": alveolus,
    "nephron": nephron, "organ_heart": organ_heart, "organ_brain": organ_brain,
    # 实验室
    "microtube": microtube, "petri_dish": petri_dish, "culture_flask": culture_flask,
    "well_plate": well_plate, "syringe": syringe, "gel_lanes": gel_lanes,
    "microscope": microscope, "mouse_lab": mouse_lab,
    "human_silhouette": human_silhouette, "tube_rack": tube_rack,
    # 图解元素
    "group_box": group_box, "leader_label": leader_label, "scale_bar": scale_bar,
    "step_badge": step_badge, "panel_letter": panel_letter, "legend_row": legend_row,
}


def list_components():
    """列出所有可用图形组件及其参数签名"""
    import inspect
    lines = []
    for name, fn in LIBRARY.items():
        try:
            sig = str(inspect.signature(fn))
        except Exception:
            sig = "(...)"
        doc = (inspect.getdoc(fn) or "").strip().split("\n")[0]
        lines.append(f"  {name}{sig}  # {doc}")
    return "\n".join(lines)


# ================================================================ CANVAS
class Canvas:
    """画布: 收集元素 -> 输出 SVG / PDF / PNG / TIFF"""

    def __init__(self, width=1400, height=1050, background="#FFFFFF"):
        self.w, self.h = int(width), int(height)
        self.bg = background
        self.items: list[str] = []
        self._gid = 0

    # -- 添加组件 --
    def add(self, name, x, y, **kw):
        """按名称添加库中组件, 如 c.add('nucleus', 300, 300, r=80, label='细胞核')"""
        if name not in LIBRARY:
            raise KeyError(f"未知组件: {name}\n可用: {', '.join(LIBRARY)}")
        self.items.append(LIBRARY[name](x, y, **kw))
        return self

    def raw(self, svg_fragment):
        self.items.append(svg_fragment)
        return self

    def text(self, x, y, t, **kw):
        self.items.append(text_el(x, y, t, **kw))
        return self

    def arrow(self, x1, y1, x2, y2, **kw):
        self.items.append(arrow(x1, y1, x2, y2, **kw))
        return self

    def line(self, x1, y1, x2, y2, color=None, width=2.2, dash=None):
        self.items.append(_stroke_line((x1, y1), (x2, y2), color, width, dash))
        return self

    def rect(self, x, y, w, h, fill="none", stroke=None, width=2, rx=0, dash=None, opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity is not None else ""
        self.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
                          f'fill="{fill}" stroke="{stroke or "none"}" stroke-width="{width}"{d}{op}/>')
        return self

    def circle(self, cx, cy, r, fill="none", stroke=None, width=2):
        self.items.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
                          f'stroke="{stroke or "none"}" stroke-width="{width}"/>')
        return self

    def path(self, d, fill="none", stroke=None, width=2.2, dash=None, cap="round"):
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(f'<path d="{d}" fill="{fill}" stroke="{stroke or "none"}" '
                          f'stroke-width="{width}" stroke-linecap="{cap}" stroke-linejoin="round"{dd}/>')
        return self

    def title(self, text, size=30, y=52, **kw):
        self.items.append(text_el(self.w / 2, y, text, size, bold=True, **kw))
        return self

    # -- 输出 --
    def svg(self) -> str:
        body = "".join(self.items)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}">\n'
                f'<rect width="{self.w}" height="{self.h}" fill="{self.bg}"/>\n{body}\n</svg>\n')

    def save(self, path):
        """保存 SVG (主交付物, 可在 Illustrator/Inkscape/Figma 中继续编辑)"""
        path = str(path)
        if not path.lower().endswith(".svg"):
            path += ".svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.svg())
        return path

    def export(self, path_stem, formats=("png", "pdf"), dpi=300, transparent=False):
        """导出多种格式。png/tiff 位图按 dpi 光栅化, pdf 为矢量。返回生成的文件列表。

        性能说明: SVG 序列化与 PDF 渲染各只执行一次——正式 PDF 与光栅化共用
        同一份 PDF 字节流(内存中传递, 不落临时文件), 相比旧实现省去一次完整
        PDF 渲染与临时 _r.pdf 的磁盘读写。
        """
        svg_str = self.svg()
        svg_path = path_stem + ".svg"
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_str)
        made = [svg_path]
        formats = tuple(f for f in formats if f != "svg") or ("png",)
        need_raster = [f for f in formats if f in ("png", "tiff", "jpg", "jpeg")]
        need_pdf = "pdf" in formats
        pdf_bytes = None
        if need_pdf or need_raster:
            import io
            try:
                from svglib.svglib import svg2rlg
                d = svg2rlg(io.StringIO(svg_str))
            except ImportError as e:
                print(f"[bio_graphics] 缺少依赖({e}); 仅输出 SVG。"
                      f"安装: pip install svglib reportlab pypdfium2 pillow")
                return made
            from reportlab.graphics import renderPDF
            pdf_bytes = renderPDF.drawToString(d)  # 只渲染一次, PDF 与位图共用
            if need_pdf:
                p = path_stem + ".pdf"
                with open(p, "wb") as f:
                    f.write(pdf_bytes)
                made.append(p)
        if need_raster:
            try:
                import pypdfium2 as pdfium
                from PIL import Image
                pdf = pdfium.PdfDocument(io.BytesIO(pdf_bytes))
                img = pdf[0].render(scale=dpi / 72.0).to_pil()
                pdf.close()
                if transparent and img.mode in ("RGB", "P"):
                    img = img.convert("RGBA")
                for fmt in need_raster:
                    f = fmt if fmt != "jpeg" else "jpg"
                    out = f"{path_stem}.{f}"
                    save_kw = {"dpi": (dpi, dpi)}
                    if f == "jpg":
                        img = img.convert("RGB")
                    if f == "tiff":
                        save_kw["compression"] = "tiff_lzw"
                    if transparent and f in ("png", "tiff"):
                        bg = Image.new("RGBA", img.size, (255, 255, 255, 0))
                        bg.paste(img, mask=img if img.mode == "RGBA" else None)
                        img = bg
                    img.save(out, **save_kw)
                    made.append(out)
            except ImportError as e:
                print(f"[bio_graphics] 光栅化跳过({e}); 已有 SVG/PDF。"
                      f"安装: pip install pypdfium2 pillow")
        return made


def register_cjk_fonts():
    """向 reportlab 注册中文字体(导出 PDF/PNG 前自动调用)"""
    import reportlab.pdfbase.pdfmetrics as pm
    from reportlab.pdfbase.ttfonts import TTFont as RLTTFont
    candidates = [("SimHei", r"C:\Windows\Fonts\simhei.ttf"),
                  ("SimHei", "/System/Library/Fonts/STHeiti Light.ttc"),
                  ("SimHei", "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")]
    for name, path in candidates:
        if os.path.exists(path) and name not in pm.getRegisteredFontNames():
            try:
                pm.registerFont(RLTTFont(name, path))
            except Exception:
                continue


# 导出前钩子: 自动注册字体
_orig_export = Canvas.export
def _export_with_fonts(self, *a, **kw):
    try:
        register_cjk_fonts()
    except Exception:
        pass
    return _orig_export(self, *a, **kw)
Canvas.export = _export_with_fonts


if __name__ == "__main__":
    print("bio_graphics 组件库\n")
    print("可用组件:")
    print(list_components())
    print("\n箭头/图解元素(非 LIBRARY, Canvas 直接方法):")
    print("  c.arrow(x1,y1,x2,y2, kind=activation|inhibition|translocation|bidirectional)")
    print("  c.text(x,y,text) | c.line | c.rect | c.circle | c.path | c.title")
    print("  c.leader_label(x,y,tx,ty,text) | c.legend_row | c.group_box")
    print("  c.panel_letter | c.step_badge | c.scale_bar | c.membrane_boundary")
