# -*- coding: utf-8 -*-
"""
make_figure.py — 命令行生成医学科研插图
用法:
  python make_figure.py spec.json -o out/figure --dpi 300 --format png,pdf,tiff
spec.json 结构:
{
  "canvas": {"width": 1400, "height": 1050, "background": "#FFFFFF"},
  "title": "图1 细胞凋亡信号通路",
  "elements": [
    {"type": "nucleus", "x": 300, "y": 300, "r": 80, "label": "细胞核"},
    {"type": "arrow", "x1": 380, "y1": 300, "x2": 520, "y2": 300, "kind": "activation", "label": "激活"},
    {"type": "text", "x": 100, "y": 60, "text": "注释", "size": 18, "bold": true},
    {"type": "legend_row", "x": 100, "y": 1000,
     "items": [["#D6E8F7", "细胞质"], ["#E9C46A", "线粒体"]]},
    {"type": "leader_label", "x": 300, "y": 300, "tx": 420, "ty": 180, "text": "核膜"},
    {"type": "raw", "svg": "<circle .../>"},
    {"type": "scale_bar", "x": 1000, "y": 1000, "length_px": 90, "text": "10 μm"}
  ]
}
支持 types: LIBRARY 中全部图形组件名 + arrow/text/legend/legend_row/leader_label/
group_box/panel_letter/step_badge/scale_bar/membrane_boundary/raw
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bio_graphics import Canvas, LIBRARY, arrow, text_el, leader_label, legend_row, legend


def build(spec: dict) -> Canvas:
    cv = spec.get("canvas", {})
    c = Canvas(cv.get("width", 1400), cv.get("height", 1050),
               cv.get("background", "#FFFFFF"))
    if spec.get("title"):
        c.title(spec["title"])
    for el in spec.get("elements", []):
        t = el.pop("type")
        if t in LIBRARY:
            c.add(t, el.pop("x"), el.pop("y"), **el)
        elif t == "arrow":
            c.arrow(el.pop("x1"), el.pop("y1"), el.pop("x2"), el.pop("y2"), **el)
        elif t == "text":
            c.text(el.pop("x"), el.pop("y"), el.pop("text"), **el)
        elif t in ("leader_label", "label"):
            c.raw(leader_label(el["x"], el["y"], el["tx"], el["ty"],
                               el["text"], **{k: v for k, v in el.items()
                                              if k not in ("x", "y", "tx", "ty", "text")}))
        elif t in ("legend", "legend_row"):
            fn = legend_row if t == "legend_row" else legend
            items = [tuple(i) if isinstance(i, (list, tuple)) else i for i in el["items"]]
            rest = {k: v for k, v in el.items() if k != "items"}
            c.raw(fn(el["x"], el["y"], items, **rest))
        elif t == "group_box":
            c.raw(__import__("bio_graphics").group_box(
                el["x"], el["y"], el["w"], el["h"],
                **{k: v for k, v in el.items() if k not in ("x", "y", "w", "h")}))
        elif t == "panel_letter":
            c.raw(text_el(el["x"], el["y"], el.get("letter", "A"),
                          el.get("size", 30), bold=True, anchor="start"))
        elif t == "step_badge":
            import bio_graphics
            c.raw(bio_graphics.step_badge(el["x"], el["y"], el.get("n", 1), **{
                k: v for k, v in el.items() if k not in ("x", "y", "n")}))
        elif t == "scale_bar":
            import bio_graphics
            c.raw(bio_graphics.scale_bar(el["x"], el["y"], el["length_px"],
                                         el.get("text", "10 μm"),
                                         el.get("size", 13)))
        elif t == "membrane_boundary":
            c.raw(__import__("bio_graphics").membrane_boundary(
                el["x"], el["y"], el["w"], el["h"],
                **{k: v for k, v in el.items() if k not in ("x", "y", "w", "h")}))
        elif t == "raw":
            c.raw(el["svg"])
        else:
            raise KeyError(f"未知元素类型: {t}")
    return c


def main():
    ap = argparse.ArgumentParser(description="生成医学科研插图")
    ap.add_argument("spec", help="JSON spec 文件路径")
    ap.add_argument("-o", "--out", default=None, help="输出路径主干(不含扩展名)")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--format", default="svg,png,pdf")
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8"))
    out = a.out or os.path.splitext(a.spec)[0]
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    c = build(spec)
    formats = tuple(f.strip().lower() for f in a.format.split(",") if f.strip())
    files = c.export(out, formats=formats, dpi=a.dpi)
    for f in files:
        print(f"  生成: {f}")


if __name__ == "__main__":
    main()
