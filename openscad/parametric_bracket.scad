// Parametric Mounting Bracket
// A configurable L-bracket with mounting holes and fillet reinforcement.
// All dimensions in mm.

/* [Main Dimensions] */
base_length = 80;       // Length of the horizontal base
base_width  = 40;       // Width (depth) of the bracket
wall_height = 60;       // Height of the vertical wall
thickness   = 5;        // Material thickness

/* [Mounting Holes] */
hole_diameter   = 5.5;  // M5 clearance holes
hole_inset      = 12;   // Distance from edges to hole centers
num_base_holes  = 2;    // Holes along the base
num_wall_holes  = 2;    // Holes on the vertical wall

/* [Reinforcement] */
fillet_radius   = 15;   // Corner fillet radius
gusset_size     = 20;   // Triangular gusset reinforcement size

/* [Rendering] */
$fn = 64;               // Facet count for smooth curves

module base_plate() {
    cube([base_length, base_width, thickness]);
}

module vertical_wall() {
    translate([0, 0, thickness])
        cube([thickness, base_width, wall_height - thickness]);
}

module fillet_reinforcement() {
    translate([thickness, 0, thickness])
        rotate([-90, 0, 0])
            difference() {
                cube([fillet_radius, fillet_radius, base_width]);
                translate([fillet_radius, fillet_radius, -1])
                    cylinder(r=fillet_radius, h=base_width + 2);
            }
}

module gusset() {
    translate([thickness, 0, thickness])
        linear_extrude(height=base_width)
            polygon(points=[
                [0, 0],
                [gusset_size, 0],
                [0, gusset_size]
            ]);
    
    // Mirror gusset on the other side
    translate([thickness, base_width, thickness])
        rotate([90, 0, 0])
            linear_extrude(height=base_width)
                polygon(points=[
                    [0, 0],
                    [gusset_size, 0],
                    [0, gusset_size]
                ]);
}

module base_holes() {
    for (i = [0 : num_base_holes - 1]) {
        x = hole_inset + i * (base_length - 2 * hole_inset) / max(num_base_holes - 1, 1);
        translate([x, base_width / 2, -1])
            cylinder(d=hole_diameter, h=thickness + 2);
    }
}

module wall_holes() {
    for (i = [0 : num_wall_holes - 1]) {
        z = thickness + hole_inset + i * (wall_height - thickness - 2 * hole_inset) / max(num_wall_holes - 1, 1);
        translate([-1, base_width / 2, z])
            rotate([0, 90, 0])
                cylinder(d=hole_diameter, h=thickness + 2);
    }
}

// --- Assembly ---
module bracket() {
    difference() {
        union() {
            base_plate();
            vertical_wall();
            fillet_reinforcement();
        }
        base_holes();
        wall_holes();
    }
}

bracket();

// Uncomment below to render a mirrored pair:
// translate([base_length + 10, 0, 0])
//     mirror([1, 0, 0]) bracket();
