// Parametric Involute Spur Gear Generator
// The entire gear profile is traced as ONE continuous polygon.
// No boolean unions between teeth — avoids all OpenSCAD rendering artifacts.
// All dimensions in mm.

/* [Gear Parameters] */
num_teeth       = 20;       // Number of teeth
module_size     = 2.5;      // Gear module (pitch diameter / num_teeth)
pressure_angle  = 20;       // Standard pressure angle in degrees
gear_thickness  = 10;       // Face width
bore_diameter   = 10;       // Central bore for shaft
hub_diameter    = 20;       // Hub around the bore
hub_height      = 5;        // Hub extension beyond gear face

/* [Keyway] */
keyway_width    = 3;
keyway_depth    = 1.5;

/* [Quality] */
inv_steps       = 15;       // Points per involute flank (higher = smoother)
root_arc_steps  = 5;        // Points along root arc between teeth

/* [Rendering] */
$fn = 128;

// ─── Derived geometry ───────────────────────────────────────────────
pitch_r    = num_teeth * module_size / 2;
outer_r    = pitch_r + module_size;
root_r     = pitch_r - 1.25 * module_size;
base_r     = pitch_r * cos(pressure_angle);
tooth_angle = 360 / num_teeth;

// ─── Involute function ─────────────────────────────────────────────
// inv(α) = tan(α) - α, with α in degrees.
// tan() in OpenSCAD takes degrees and returns a dimensionless ratio.
// α must be converted to radians for subtraction, then result to degrees.
function inv(a_deg) = (tan(a_deg) - a_deg * PI / 180) * 180 / PI;

// Half-tooth thickness angle at the pitch circle (degrees)
half_thick = 90 / num_teeth + inv(pressure_angle);

// ─── Flank angle functions ──────────────────────────────────────────
// For a tooth centered at angle `c`, the involute flank at radius `r`:
//   Left flank (counterclockwise side):  angle increases toward tip
//   Right flank (clockwise side):        angle increases toward root

function left_flank_angle(r, c) =
    c - half_thick + inv(acos(base_r / r));

function right_flank_angle(r, c) =
    c + half_thick - inv(acos(base_r / r));

// ─── Points for one tooth + root gap (counterclockwise winding) ────
function tooth_points(c) =
    let(
        a_left_base  = c - half_thick,       // left flank angle at base
        a_right_base = c + half_thick,       // right flank angle at base
        a_next_left  = c + tooth_angle - half_thick  // next tooth's left base
    )
    concat(
        // 1. Radial line: root circle up to base circle (left side)
        [[root_r * cos(a_left_base), root_r * sin(a_left_base)]],

        // 2. Left involute flank going UP (base_r → outer_r)
        //    Angle increases from (c - half_thick) toward (c - half_thick + inv_tip)
        [for (s = [0 : inv_steps])
            let(
                r = base_r + (outer_r - base_r) * s / inv_steps,
                a = left_flank_angle(r, c)
            )
            [r * cos(a), r * sin(a)]
        ],

        // 3. Tip arc center point (smooths the tooth tip)
        [[outer_r * cos(c), outer_r * sin(c)]],

        // 4. Right involute flank going DOWN (outer_r → base_r)
        //    Angle increases from (c + half_thick - inv_tip) toward (c + half_thick)
        [for (s = [0 : inv_steps])
            let(
                r = outer_r - (outer_r - base_r) * s / inv_steps,
                a = right_flank_angle(r, c)
            )
            [r * cos(a), r * sin(a)]
        ],

        // 5. Radial line: base circle down to root circle (right side)
        [[root_r * cos(a_right_base), root_r * sin(a_right_base)]],

        // 6. Root arc to the next tooth's left flank
        [for (s = [1 : root_arc_steps - 1])
            let(a = a_right_base + (a_next_left - a_right_base) * s / root_arc_steps)
            [root_r * cos(a), root_r * sin(a)]
        ]
    );

// ─── Full gear outline: concatenate all teeth ───────────────────────
gear_outline = [
    for (i = [0 : num_teeth - 1])
        each tooth_points(i * tooth_angle)
];

// ─── 2D gear profile ────────────────────────────────────────────────
module gear_profile_2d() {
    difference() {
        polygon(gear_outline);
        circle(d = bore_diameter);
    }
}

// ─── Keyway cut ─────────────────────────────────────────────────────
module keyway() {
    translate([bore_diameter/2 - keyway_depth, -keyway_width/2, -1])
        cube([keyway_depth + 1, keyway_width, gear_thickness + hub_height + 2]);
}

// ─── Lightening holes ───────────────────────────────────────────────
module lightening_holes() {
    if (num_teeth > 15) {
        n = 4;
        hr = (root_r + bore_diameter/2) / 2;
        hd = (root_r - bore_diameter/2) / 2 - 3;
        if (hd > 3) {
            for (i = [0 : n - 1])
                rotate([0, 0, i * 360/n + 45])
                    translate([hr, 0, -1])
                        cylinder(d = hd, h = gear_thickness + 2);
        }
    }
}

// ─── Full 3D gear ───────────────────────────────────────────────────
module spur_gear() {
    difference() {
        union() {
            linear_extrude(height = gear_thickness)
                gear_profile_2d();
            // Hub
            translate([0, 0, gear_thickness])
                difference() {
                    cylinder(d = hub_diameter, h = hub_height);
                    cylinder(d = bore_diameter, h = hub_height + 1);
                }
        }
        keyway();
        lightening_holes();
    }
}

spur_gear();

// ─── Info ───────────────────────────────────────────────────────────
echo(str("Pitch Diameter: ", pitch_r * 2, " mm"));
echo(str("Outer Diameter: ", outer_r * 2, " mm"));
echo(str("Root Diameter:  ", root_r * 2, " mm"));
echo(str("Base Diameter:  ", base_r * 2, " mm"));
echo(str("Tooth half-angle at pitch: ", half_thick, " deg"));
echo(str("Total polygon points: ", len(gear_outline)));
