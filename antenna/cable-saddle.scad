// Седло для разгрузки кабеля RG316 на деревянной рейке вне ВЧ-тракта.
// Нейлоновая стяжка через два окна проходит поперёк кабеля.
length = 38;
width = 22;
height = 8;
cable_diameter = 2.8;
screw_diameter = 3.4;
$fn = 48;
difference() {
    cube([length,width,height]);
    translate([-1,width/2,height]) rotate([0,90,0])
        cylinder(h=length+2,d=cable_diameter+0.5);
    for (p=[[5,5],[length-5,width-5]])
        translate([p.x,p.y,-1]) cylinder(h=height+2,d=screw_diameter);
    // Сквозной тоннель для стяжки 3,6 мм, под канавкой.
    translate([length/2-2.25,-1,2]) cube([4.5,width+2,2.3]);
}
