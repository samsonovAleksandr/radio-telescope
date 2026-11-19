"""Geometric acceptance checks for the exported templates and print part."""
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
from math import hypot

root = Path(__file__).parent
for name in ["assembly","back","guide-narrow","guide-wide","guide-probe","flare-narrow","flare-wide"]:
    svg = ET.parse(root / f"{name}.svg").getroot()
    assert svg.tag.endswith("svg")
    if name != "assembly":
        assert svg.get("width").endswith("mm") and svg.get("height").endswith("mm")
        assert "100 мм" in "".join(svg.itertext())
    print(f"{name}.svg: XML OK")

face_h = hypot(520,160)
face_e = hypot(520,170)
assert abs(hypot(face_h,170)-hypot(face_e,160)) < 1e-8
print(f"Common seam: {hypot(face_h,170):.2f} mm")
vertices = [tuple(map(float,line.split()[1:])) for line in (root/"cable-saddle.stl").read_text().splitlines() if line.strip().startswith("vertex ")]
assert len(vertices) > 0 and len(vertices) % 3 == 0
edges = Counter()
for i in range(0,len(vertices),3):
    a,b,c = vertices[i:i+3]
    assert len({a,b,c}) == 3
    for p,q in [(a,b),(b,c),(c,a)]:
        edges[tuple(sorted((p,q)))] += 1
assert set(edges.values()) == {2}
extent = tuple(max(v[i] for v in vertices)-min(v[i] for v in vertices) for i in range(3))
assert extent == (38,22,8)
print(f"STL: {len(vertices)//3} facets, two facets on every edge, envelope {extent} mm")
