import xml.etree.ElementTree as E
from pathlib import Path
from xml.sax.saxutils import escape
import math
out=Path(__file__).resolve().parent
def tag(p,t,**kw):return E.SubElement(p,t,{k:str(v) for k,v in kw.items()})
def wire(p,a,b,l,w):return tag(p,'wire',x1=a[0],y1=a[1],x2=b[0],y2=b[1],layer=l,width=w)
def txt(p,x,y,s,l,size):tag(p,'text',x=x,y=y,size=size,layer=l,ratio=14).text=s
def base():
 root=E.Element('eagle',version='9.6.2');draw=tag(root,'drawing');tag(draw,'settings'); layers=tag(draw,'layers')
 for i,n in [(1,'Top'),(16,'Bottom'),(17,'Pads'),(18,'Vias'),(19,'Unrouted'),(20,'Dimension'),(21,'tPlace'),(25,'tNames'),(27,'tValues'),(29,'tStop'),(30,'bStop'),(31,'tCream'),(44,'Drills'),(45,'Holes'),(51,'tDocu'),(91,'Nets'),(92,'Busses'),(93,'Pins'),(94,'Symbols'),(95,'Names'),(96,'Values')]:
  tag(layers,'layer',number=i,name=n,color=1 if i==1 else 4,fill=1,visible='yes',active='yes')
 return root,draw
def save(root,name):
 E.indent(root);(out/name).write_bytes(b'<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE eagle SYSTEM "eagle.dtd">\n'+E.tostring(root,encoding='utf-8'))
# local package pads: x,y,width,height
pads={'CAP':{'1':(-.8,0,.9,.95),'2':(.8,0,.9,.95)},'CHOKE':{'1':(0,-.8,.95,.9),'2':(0,.8,.95,.9)},'MMIC':{'1':(-1.5,-1.6,.85,1.55),'2':(0,-1.6,.95,1.55),'3':(1.5,-1.6,.85,1.55),'4':(0,.65,1.9,2.35)},'COAX':{'1':(0,0,2,2),'2':(0,-3,3,2)},'POWER':{'1':(0,0,2,2),'2':(0,3,2,2)}}
pins={'CAP':{'1':(-5.08,0),'2':(5.08,0)},'CHOKE':{'1':(0,-5.08),'2':(0,5.08)},'MMIC':{'1':(-7.62,0),'3':(7.62,0),'2':(-2.54,-7.62),'4':(2.54,-7.62)},'COAX':{'1':(5.08,0),'2':(0,-5.08)},'POWER':{'1':(5.08,0),'2':(0,-5.08)}}
def lib(parent,full):
 l=tag(parent,'library',name='RT');pk=tag(l,'packages')
 for k,ps in pads.items():
  p=tag(pk,'package',name=k)
  for number,(x,y,w,h) in ps.items():tag(p,'smd',name=number,x=x,y=y,dx=w,dy=h,layer=1)
  name_xy = {'CAP': (1.8, 1.3), 'CHOKE': (-1.8, 1.6), 'MMIC': (-3.8, 3.4), 'POWER': (-4.5, 1), 'COAX': (-1, 2)}
  txt(p,*name_xy[k],'>NAME',25,1.05)
 if not full:return
 sy=tag(l,'symbols');ds=tag(l,'devicesets')
 for k,ps in pins.items():
  s=tag(sy,'symbol',name=k)
  if k=='CAP':lines=[[(-5.08,0),(-.6,0)],[(-.6,-1.8),(-.6,1.8)],[(.6,-1.8),(.6,1.8)],[(.6,0),(5.08,0)]]
  elif k=='CHOKE':lines=[[(0,-5.08),(0,-3)]+[(.95*math.sin(i*math.pi/4),-3+i*.375) for i in range(17)]+[(0,5.08)]]
  elif k=='MMIC':lines=[[(-5,-4),(-5,4),(5,0),(-5,-4)],[(-7.62,0),(-5,0)],[(5,0),(7.62,0)],[(-2.54,-3),(-2.54,-7.62)],[(2.54,-1),(2.54,-7.62)]]
  else:lines=[[(-2,-2),(-2,2),(2,2),(2,-2),(-2,-2)],[(2,0),(5.08,0)],[(0,-2),(0,-5.08)]]
  for line in lines:
   for a,b in zip(line,line[1:]):
    if a!=b:wire(s,a,b,94,.254)
  txt(s,-3,6,'>NAME',95,1.5);txt(s,-3,4.25,'>VALUE',96,1.25)
  for n,(x,y) in ps.items():tag(s,'pin',name=n,x=x,y=y,length='point',visible='pad',direction=('in' if k=='MMIC' and n=='1' else 'out' if k=='MMIC' and n=='3' else 'pas'))
  d=tag(ds,'deviceset',name=k,uservalue='yes');g=tag(d,'gates');tag(g,'gate',name='G$1',symbol=k,x=0,y=0)
  dv=tag(tag(d,'devices'),'device',name='',package=k);cs=tag(dv,'connects')
  for n in ps:tag(cs,'connect',gate='G$1',pin=n,pad=n)
  tag(tag(dv,'technologies'),'technology',name='')
# schematic coordinates, board coordinates
parts={'J1':('COAX','RF IN',(10.16,30.48),(3,10)),'C1':('CAP','10p',(25.4,30.48),(9,10)),'U1':('MMIC','SPF5189Z',(45.72,30.48),(14,11.6)),'C2':('CAP','100p',(71.12,30.48),(21,10)),'J2':('COAX','RF OUT',(91.44,30.48),(27,10)),'L1':('CHOKE','47n',(58.42,45.72),(18,14)),'C3':('CAP','100p',(78.74,55.88),(20.5,17)),'C4':('CAP','100n',(78.74,68.58),(20.5,20)),'J3':('POWER','5V',(30.48,68.58),(17,20))}
nets={'IN':['J1.1','C1.1'],'AMP_IN':['C1.2','U1.1'],'BIAS_RF':['U1.3','L1.1','C2.1'],'OUT':['C2.2','J2.1'],'VCC':['J3.1','L1.2','C3.1','C4.1'],'GND':['J1.2','J2.2','U1.2','U1.4','J3.2','C3.2','C4.2']}
root,d=base();s=tag(d,'schematic');lib(tag(s,'libraries'),True);tag(s,'attributes');tag(s,'variantdefs')
def classes(p):tag(tag(p,'classes'),'class',**{'number':0,'name':'default','width':0,'drill':0})
classes(s);pp=tag(s,'parts');sheet=tag(tag(s,'sheets'),'sheet');tag(sheet,'plain');ins=tag(sheet,'instances')
for r,(k,v,(x,y),_) in parts.items():
 tag(pp,'part',name=r,library='RT',deviceset=k,device='',value=v);tag(ins,'instance',part=r,gate='G$1',x=x,y=y,rot='MR0' if r=='J2' else 'R0')
sn=tag(sheet,'nets')
paths={'IN':[[(15.24,30.48),(20.32,30.48)]],'AMP_IN':[[(30.48,30.48),(38.1,30.48)]],'BIAS_RF':[[(53.34,30.48),(58.42,30.48),(66.04,30.48)],[(58.42,30.48),(58.42,40.64)]],'OUT':[[(76.2,30.48),(86.36,30.48)]],'VCC':[[(35.56,68.58),(58.42,68.58),(73.66,68.58)],[(58.42,68.58),(58.42,55.88),(58.42,50.8)],[(58.42,55.88),(73.66,55.88)]]}
for n,refs in nets.items():
 net=tag(sn,'net',name=n,**{'class':0})
 groups=[[i] for i in refs] if n=='GND' else [refs]
 for group in groups:
  seg=tag(net,'segment')
  for ref in group:
   r,i=ref.split('.');tag(seg,'pinref',part=r,gate='G$1',pin=i)
  if n=='GND':
   k,v,(x,y),_=parts[r];a,b=pins[k][i];x=round(x+a,2);y=round(y+b,2);wire(seg,(x,y),(x,y-2.54),91,.1524);tag(seg,'label',x=x,y=y-2.54,size=1.2,layer=95)
  else:
   for line in paths[n]:
    for a,b in zip(line,line[1:]):wire(seg,a,b,91,.1524)
   for x,y in {'BIAS_RF':[(58.42,30.48)],'VCC':[(58.42,68.58),(58.42,55.88)]}.get(n,[]):tag(seg,'junction',x=x,y=y)
save(root,'LNA.sch')
root,d=base();board=tag(d,'board');pl=tag(board,'plain')
for a,b in zip([(0,0),(30,0),(30,25),(0,25)],[(30,0),(30,25),(0,25),(0,0)]):wire(pl,a,b,20,0)
lib(tag(board,'libraries'),False);tag(board,'attributes');tag(board,'variantdefs');classes(board);rules=tag(board,'designrules',name='FR4-0.8');tag(rules,'param',name='mtIsolate',value='0.71mm');tag(rules,'param',name='layerSetup',value='(1*16)');els=tag(board,'elements')
for r,(k,v,_,(x,y)) in parts.items():tag(els,'element',name=r,library='RT',package=k,value=v,x=x,y=y)
sg=tag(board,'signals')
def pos(ref):
 r,i=ref.split('.');k,v,_,(x,y)=parts[r];a,b,*_=pads[k][i];return (round(x+a,3),round(y+b,3))
tracks={'IN':[[pos('J1.1'),pos('C1.1')]],'AMP_IN':[[pos('C1.2'),pos('U1.1')]],'BIAS_RF':[[pos('U1.3'),(18,10),pos('C2.1')],[(18,10),pos('L1.1')]],'OUT':[[pos('C2.2'),pos('J2.1')]],'VCC':[[pos('L1.2'),(18,17),pos('C3.1')],[(18,17),(18,20),pos('C4.1')],[pos('J3.1'),(18,20)]]}
for n,refs in nets.items():
 sig=tag(sg,'signal',name=n)
 for ref in refs:
  r,i=ref.split('.');tag(sig,'contactref',element=r,pad=i)
 if n!='GND':
  for line in tracks[n]:
   for a,b in zip(line,line[1:]):wire(sig,a,b,1,1.4 if n in ['IN','AMP_IN','OUT'] or (n=='BIAS_RF' and a[1]==b[1]) else .45)
 else:
  for layer in [1,16]:
   p=tag(sig,'polygon',width=.2,layer=layer,isolate=.6,thermals='no')
   for x,y in [(.35,.35),(29.65,.35),(29.65,24.65),(.35,24.65)]:tag(p,'vertex',x=x,y=y)
  for x,y in [(14,8.7),(14,13.7),(13.1,13.7),(14.9,13.7),(13.1,14.6),(14,14.6),(14.9,14.6),(22.2,17),(22.2,20),(17,23),(3,7),(27,7)]+[(x,y) for x in range(2,30,3) for y in [2,6,14.8,24] if not (11<=x<=23 and y==14.8)]:tag(sig,'via',x=x,y=y,extent='1-16',drill=.35,diameter=.75)
  for ref,end in [('U1.2',(14,8.7)),('U1.4',(14,13.7)),('C3.2',(22.2,17)),('C4.2',(22.2,20))]:wire(sig,pos(ref),end,1,.5)
save(root,'LNA.brd')
