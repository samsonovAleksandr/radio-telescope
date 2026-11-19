"""Convert this project's self-contained EAGLE sheet to native KiCad symbols and wires."""
from pathlib import Path
import uuid
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
source = ET.parse(HERE / "LNA.sch")
library = source.find(".//library")
font = "(effects (font (size 1.27 1.27)))"
stroke = "(stroke (width 0.25) (type default))"
sheet_id = str(uuid.uuid5(uuid.NAMESPACE_URL, "radio-telescope/LNA"))


def ident(name):
    return str(uuid.uuid5(uuid.UUID(sheet_id), name))


def xy(x, y):
    return f"{76.2 + float(x):.3f} {152.4 - float(y):.3f}"


def symbol_shape(symbol):
    name = symbol.get("name")
    graphics = []
    for w in symbol.findall("wire"):
        pts = f'(xy {w.get("x1")} {w.get("y1")}) (xy {w.get("x2")} {w.get("y2")})'
        graphics.append(f"(polyline (pts {pts}) {stroke} (fill (type none)))")
    pin_names = {"MMIC": {"1":"RF_IN","2":"GND","3":"RF_OUT/VD","4":"PADDLE"}, "COAX":{"1":"RF","2":"SHIELD"}, "POWER":{"1":"+5V","2":"GND"}}
    for pin in symbol.findall("pin"):
        number = pin.get("name")
        name_text = pin_names.get(name, {}).get(number, "~")
        x,y = map(float, (pin.get("x"), pin.get("y")))
        angle = 270 if y > 0 else 90 if y < 0 else 180 if x > 0 else 0
        length = 1.27
        direction = {"in":"input","out":"output","pas":"passive"}[pin.get("direction")]
        graphics.append(f'(pin {direction} line (at {x} {y} {angle}) (length {length}) (name "{name_text}" {font}) (number "{number}" {font}))')
    properties = []
    ref_prefix = {"MMIC":"U","COAX":"J","POWER":"J","CAP":"C","CHOKE":"L"}[name]
    for field,value,y in [("Reference",ref_prefix,7.62),("Value",name,5.08)]:
        properties.append(f'(property "{field}" "{value}" (at 0 {y} 0) {font})')
    return (f'(symbol "{name}" (pin_names (hide yes)) (in_bom yes) (on_board yes) '
            + " ".join(properties) + f' (symbol "{name}_1_1" ' + " ".join(graphics) + "))")


symbols = [symbol_shape(s) for s in library.findall("./symbols/symbol")]
(HERE/"RT.kicad_sym").write_text("(kicad_symbol_lib (version 20241209) (generator kicad_symbol_editor)\n"+"\n".join(symbols)+")\n")
(HERE/"sym-lib-table").write_text('(sym_lib_table (version 7) (lib (name "RT")(type "KiCad")(uri "${KIPRJMOD}/RT.kicad_sym")(options "")(descr "")))\n')
(HERE/"fp-lib-table").write_text('(fp_lib_table (version 7) (lib (name "RT")(type "KiCad")(uri "${KIPRJMOD}/RT.pretty")(options "")(descr "")))\n')
embedded = [s.replace('(symbol "', '(symbol "RT:',1) for s in symbols]
out = [f'(kicad_sch (version 20250114) (generator eeschema) (uuid "{sheet_id}") (paper "A4") (lib_symbols', *embedded, ')']
for part in source.findall(".//parts/part"):
    ref,kind,value = (part.get(k) for k in ["name","deviceset","value"])
    instance = source.find(f'.//instances/instance[@part="{ref}"]')
    x,y = float(instance.get('x')),float(instance.get('y'))
    mirror = '(mirror y)' if instance.get('rot')=='MR0' else ''
    out.append(f'(symbol (lib_id "RT:{kind}") (at {xy(x,y)} 0) {mirror} (unit 1) (in_bom yes) (on_board yes) (uuid "{ident(ref)}")')
    for field,val,dy in [('Reference',ref,6.35),('Value',value,4.445),('Footprint','RT:'+kind,0)]:
        hidden = '(hide yes)' if field=='Footprint' else ''
        dx = -6.35 if kind=='CHOKE' else 0
        out.append(f'(property "{field}" "{val}" (at {xy(x+dx,y+dy)} 0) (effects (font (size 1.27 1.27)) {hidden}))')
    out.append(f'(instances (project "LNA" (path "/{sheet_id}" (reference "{ref}") (unit 1)))))')
for net in source.findall('.//sheet/nets/net'):
    name=net.get('name')
    for idx,seg in enumerate(net.findall('segment')):
        wires=seg.findall('wire')
        for j,w in enumerate(wires):
            a,b=[xy(w.get('x'+n),w.get('y'+n)) for n in ['1','2']]
            if name in {"IN", "AMP_IN", "OUT"} and j == 0:
                # Give the short RF nets room for a vertical label away from pin numbers.
                label_x = float(w.get("x1")) + 2.54
                middle = xy(label_x, w.get("y1"))
                out.append(f'(wire (pts (xy {a}) (xy {middle})) (stroke (width 0) (type default)) (uuid "{ident(name + "/split")}"))')
                a = middle
            out.append(f'(wire (pts (xy {a}) (xy {b})) (stroke (width 0) (type default)) (uuid "{ident(f"{name}/{idx}/w{j}")}"))')
        for j,node in enumerate(seg.findall('junction')):
            out.append(f'(junction (at {xy(node.get("x"),node.get("y"))}) (diameter 0) (color 0 0 0 0) (uuid "{ident(f"{name}/{idx}/j{j}")}"))')
        w=wires[-1] if name=="GND" else wires[0]
        x,y = w.get('x2'),w.get('y2')
        angle = 0
        if name in {"IN", "AMP_IN", "OUT"}:
            x = float(w.get("x1")) + 2.54
            angle = 90
        where = xy(x,y)
        out.append(f'(label "{name}" (at {where} {angle}) (effects (font (size 1.1 1.1)) (justify left bottom)) (uuid "{ident(f"{name}/{idx}/label")}"))')
out.append('(sheet_instances (path "/" (page "1"))) (embedded_fonts no))')
(HERE/"LNA.kicad_sch").write_text("\n".join(out)+"\n")
