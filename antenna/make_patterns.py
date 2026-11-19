"""Build 1:1 sheet-metal templates (SVG document units are millimetres)."""
from math import hypot
from pathlib import Path

HERE = Path(__file__).parent
A, B, W, H, FLARE, GUIDE = 160, 80, 500, 400, 520, 180
STYLE = """<style>text{font:5px sans-serif;fill:#132a39}path,line,rect,circle{fill:none;stroke:#162b38;stroke-width:.35}.axis{stroke:#628798;stroke-dasharray:3 2}.dim{stroke:#628798}</style>"""


def label(x, y, msg):
    return f'<text x="{x}" y="{y}" text-anchor="middle">{msg}</text>'


def write(name, width, height, shapes):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}mm" height="{height}mm" viewBox="0 0 {width} {height}">{STYLE}{shapes}</svg>'
    (HERE / name).write_text(svg, encoding="utf-8")


def panel(name, lower, upper, slant, note, probe=False):
    width = max(upper + 36, 180)
    middle = width / 2
    y = 18 + slant
    shapes = f'<path d="M {middle-upper/2},18 h {upper} L {middle+lower/2},{y} h {-lower} Z"/>'
    shapes += f'<line class="axis" x1="{middle}" x2="{middle}" y1="18" y2="{y}"/>'
    shapes += label(middle, 12, f"{upper} мм")
    shapes += label(middle, y+9, f"{lower} мм")
    shapes += label(middle, 18+slant*.50, note)
    shapes += label(middle, 18+slant*.50+9, f"Высота развёртки {slant:.2f} мм")
    if probe:
        shapes += f'<circle cx="{middle}" cy="{y-70.2}" r="2.05"/>'
        shapes += label(middle, y-60, "Ø4,1 · от дна 70,2")
    shapes += f'<path class="dim" d="M 18,{y+17} v 3 h 100 v -3"/>'
    shapes += label(68, y+27, "контроль печати 100 мм")
    write(name, width, round(y+34, 2), shapes)


if __name__ == "__main__":
    panel("flare-wide.svg", A, W, hypot(FLARE, (H-B)/2), "Широкая панель ×2")
    panel("flare-narrow.svg", B, H, hypot(FLARE, (W-A)/2), "Узкая панель ×2")
    panel("guide-probe.svg", A, A, GUIDE, "Стенка с зондом ×1", True)
    panel("guide-wide.svg", A, A, GUIDE, "Широкая стенка ×1")
    panel("guide-narrow.svg", B, B, GUIDE, "Узкая стенка ×2")
    panel("back.svg", A, A, B, "Короткозамыкатель ×1")

