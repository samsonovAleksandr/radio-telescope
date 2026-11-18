from make_lna import *
def render(name,view,title,body):
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}" width="960"><title>{title}</title><rect x="-100" y="-100" width="500" height="500" fill="white"/>{body}</svg>'
 (out/name).write_text(svg,encoding='utf8')
def line(a,b,col,w):
 return f'<path d="M{a[0]} {a[1]} L{b[0]} {b[1]}" fill="none" stroke="{col}" stroke-width="{w}"/>'
def label(x,y,t,size=1.7):return f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="#172635">{escape(t)}</text>'
def point(e,j):return float(e.get('x'+j)),float(e.get('y'+j))
sch=E.parse(out/'LNA.sch');body=label(3,4,'LNA-1420   /   SPF5189Z',2.6)+label(3,8,'A1   •   External supply +5 V   •   RF ports 50 Ω')
for e in sch.findall('.//net/segment/wire'):
 a,b=[point(e,j) for j in ['1','2']];body+=line((a[0],85-a[1]),(b[0],85-b[1]),'#196248',.32)
for e in sch.findall('.//junction'):
 x,y=point(e,'');body+=f'<circle cx="{x}" cy="{85-y}" r=".55" fill="#196248"/>'
for r,(k,v,(x,y),_) in parts.items():
 for e in sch.findall(f'.//symbol[@name="{k}"]/wire'):
  a,b=[point(e,j) for j in ['1','2']];m=-1 if r=='J2' else 1
  body+=line((x+m*a[0],85-y-a[1]),(x+m*b[0],85-y-b[1]),'#172635',.32)
 body+=label(x+(1.5 if r=='L1' else -3.2),85-y-(0 if r=='L1' else 5.7),r+' '+v)
for ref in nets['GND']:
 r,i=ref.split('.');k,v,(x,y),_=parts[r];a,b=pins[k][i];x+=a;y=85-y-b+2.54
 for j in range(3):body+=line((x-1.3+j*.4,y+j*.45),(x+1.3-j*.4,y+j*.45),'#196248',.25)
body+=label(3,72,'U1: 1 RF IN     2, 4 GND     3 RF OUT / DC',1.8)
render('schematic.svg','0 0 104 77','LNA schematic',body)
body='<rect width="30" height="25" fill="#d6e4d9"/>'
for n,lines in tracks.items():
 for ll in lines:
  for a,b in zip(ll,ll[1:]):body+=line((a[0],25-a[1]),(b[0],25-b[1]),'#bf5928',1.4 if n in ['IN','OUT'] else .45)
for r,(k,v,_,(x,y)) in parts.items():
 for i,(a,b,w,h) in pads[k].items():body+=f'<rect x="{x+a-w/2}" y="{25-y-b-h/2}" width="{w}" height="{h}" fill="#806023"/>'
 body+=label(x-1.2,25-y+(3.6 if r in ['C1','U1','C2'] else -1.3),r,.95)
for e in E.parse(out/'LNA.brd').findall('.//via'):
 x,y=point(e,'');body+=f'<circle cx="{x}" cy="{25-y}" r=".31" fill="#456578"/>'
render('layout.svg','-1 -1 32 27','Top side, 30 × 25 mm',body)
# Prove sheet endpoints match pin coordinates; compare PCB pad membership.
br=E.parse(out/'LNA.brd')
for n,refs in nets.items():
 segs=sch.findall(f'.//net[@name="{n}"]/segment')
 for seg in segs:
  ends={point(e,j) for e in seg.findall('wire') for j in ['1','2']}
  for p in seg.findall('pinref'):
   r=p.get('part');i=p.get('pin');k,_,(x,y),_=parts[r];a,b=pins[k][i]
   assert (round(x+(-a if r=='J2' else a),2),round(y+b,2)) in ends,(r,i)
 assert sorted(refs)==sorted(e.get('element')+'.'+e.get('pad') for e in br.findall(f'.//signal[@name="{n}"]/contactref'))
print('Validated 6 nets, 9 devices, graphical exports')
