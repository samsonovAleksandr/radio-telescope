"""Cross-check manufactured drill coordinates, profile, layer manifest and netlists."""
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

here = Path(__file__).resolve().parent
cam = here / 'fabrication'
eagle = ET.parse(here / 'LNA.brd')
sheet = ET.parse(here / 'checks/netlist.xml')
expected = {
    signal.get('name'): {(p.get('element'),p.get('pad')) for p in signal.findall('contactref')}
    for signal in eagle.findall('.//signals/signal')
}
actual = {
    net.get('name').lstrip('/'): {(n.get('ref'),n.get('pin')) for n in net.findall('node')}
    for net in sheet.findall('.//nets/net')
}
assert expected == actual
holes = {(float(v.get('x')),float(v.get('y'))) for v in eagle.findall('.//via')}
drill = (cam/'LNA.drl').read_text()
points = [(float(x),float(y)) for x,y in re.findall(r'^X([.\d]+)Y([.\d]+)$',drill,re.M)]
assert len(points) == len(holes) == 47 and set(points) == holes
assert 'T1C0.350' in drill
job = json.loads((cam/'LNA-job.gbrjob').read_text())
assert job['GeneralSpecs']['BoardThickness'] == 0.8
assert len(job['FilesAttributes']) == 6
for entry in job['FilesAttributes']:
    data = (cam/entry['Path']).read_text()
    assert data.rstrip().endswith('M02*') and '%MOMM*%' in data
edges = (cam/'LNA-Edge_Cuts.gm1').read_text()
vertices = [(int(x)/1e6,int(y)/1e6,int(op)) for x,y,op in re.findall(r'X(-?\d+)Y(-?\d+)D(0[12])\*',edges)]
segments = set()
for i in range(0,len(vertices),2):
    a,b = vertices[i:i+2]
    assert (a[2],b[2]) == (2,1)
    segments.add(frozenset((a[:2],b[:2])))
corners = [(0,0),(30,0),(30,25),(0,25)]
assert segments == {frozenset((p,corners[(i+1)%4])) for i,p in enumerate(corners)}
print(f"KiCad/EAGLE: {len(expected)} nets, {sum(map(len,actual.values()))} pad assignments identical.")
print("Gerber: six complete metric layers, 30 x 25 mm rectangular profile; job stack 0.8 mm.")
print(f"Excellon: {len(points)} distinct 0.35 mm plated vias; every coordinate matches EAGLE.")
