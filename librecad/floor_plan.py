"""
2D Floor Plan Generator — DXF output for LibreCAD

Creates an architectural floor plan with:
- Exterior and interior walls
- Door swings and window lines
- Room labels and dimensions
- Title block

The output DXF opens directly in LibreCAD (or any DXF-compatible viewer).

Usage:
    pip install ezdxf
    python floor_plan.py

Outputs:
    floor_plan.dxf — 2D drawing file
"""

import ezdxf
from ezdxf import units
from ezdxf.math import Vec2
import math

# ─── Parameters (all in mm) ──────────────────────────────────────────
WALL_THICKNESS = 200
EXT_WALL_THICK = 250

# Room dimensions (interior)
LIVING_W, LIVING_H = 5000, 4000
KITCHEN_W, KITCHEN_H = 3000, 4000
BEDROOM_W, BEDROOM_H = 4000, 3500
BATH_W, BATH_H = 2500, 3500
HALLWAY_W = 1500

# Door/window sizes
DOOR_WIDTH = 900
WINDOW_WIDTH = 1200

# ─── Document Setup ─────────────────────────────────────────────────
doc = ezdxf.new("R2010")
doc.units = units.MM
doc.header['$LWDISPLAY'] = 1  # Enable lineweight display
msp = doc.modelspace()

# ─── Layers ──────────────────────────────────────────────────────────
doc.layers.add("WALLS", color=7, lineweight=50)         # White, 0.50mm
doc.layers.add("WALLS_INT", color=7, lineweight=35)     # White, 0.35mm
doc.layers.add("DOORS", color=3, lineweight=25)         # Green, 0.25mm
doc.layers.add("WINDOWS", color=5, lineweight=25)       # Blue,  0.25mm
doc.layers.add("DIMENSIONS", color=1, lineweight=13)    # Red,   0.13mm
doc.layers.add("TEXT", color=2, lineweight=18)           # Yellow, 0.18mm
doc.layers.add("FURNITURE", color=8, lineweight=13)     # Gray,  0.13mm
doc.layers.add("TITLEBLOCK", color=7, lineweight=18)    # White, 0.18mm

# ─── Helper Functions ────────────────────────────────────────────────

def draw_wall(p1, p2, thickness, layer="WALLS"):
    """Draw a double-line wall between two points."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.sqrt(dx*dx + dy*dy)
    if length == 0:
        return
    # Normal direction (perpendicular)
    nx = -dy / length * thickness / 2
    ny = dx / length * thickness / 2

    # Outer and inner wall lines
    msp.add_line(
        (p1[0] + nx, p1[1] + ny),
        (p2[0] + nx, p2[1] + ny),
        dxfattribs={"layer": layer}
    )
    msp.add_line(
        (p1[0] - nx, p1[1] - ny),
        (p2[0] - nx, p2[1] - ny),
        dxfattribs={"layer": layer}
    )

def draw_rect_walls(x, y, w, h, thickness, layer="WALLS"):
    """Draw rectangular room walls."""
    corners = [
        (x, y), (x + w, y), (x + w, y + h), (x, y + h)
    ]
    for i in range(4):
        draw_wall(corners[i], corners[(i + 1) % 4], thickness, layer)

def draw_door(x, y, width, direction="right", angle=90, layer="DOORS"):
    """Draw a door with swing arc."""
    # Door leaf (line)
    if direction == "right":
        msp.add_line((x, y), (x + width, y), dxfattribs={"layer": layer})
        # Swing arc
        msp.add_arc(
            center=(x, y),
            radius=width,
            start_angle=0,
            end_angle=angle,
            dxfattribs={"layer": layer}
        )
    elif direction == "up":
        msp.add_line((x, y), (x, y + width), dxfattribs={"layer": layer})
        msp.add_arc(
            center=(x, y),
            radius=width,
            start_angle=90,
            end_angle=90 + angle,
            dxfattribs={"layer": layer}
        )
    elif direction == "left":
        msp.add_line((x, y), (x - width, y), dxfattribs={"layer": layer})
        msp.add_arc(
            center=(x, y),
            radius=width,
            start_angle=180,
            end_angle=180 + angle,
            dxfattribs={"layer": layer}
        )
    elif direction == "down":
        msp.add_line((x, y), (x, y - width), dxfattribs={"layer": layer})
        msp.add_arc(
            center=(x, y),
            radius=width,
            start_angle=270,
            end_angle=270 + angle,
            dxfattribs={"layer": layer}
        )

def draw_window(x1, y1, x2, y2, layer="WINDOWS"):
    """Draw a window symbol (three parallel lines)."""
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx*dx + dy*dy)
    if length == 0:
        return
    nx = -dy / length * 50
    ny = dx / length * 50

    for offset in [-1, 0, 1]:
        msp.add_line(
            (x1 + nx * offset, y1 + ny * offset),
            (x2 + nx * offset, y2 + ny * offset),
            dxfattribs={"layer": layer}
        )

def add_room_label(x, y, name, area_sqm):
    """Add centered room label with area."""
    msp.add_text(
        name,
        height=150,
        dxfattribs={"layer": "TEXT", "style": "OpenSans"}
    ).set_placement((x, y + 80), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)

    msp.add_text(
        f"{area_sqm:.1f} m²",
        height=100,
        dxfattribs={"layer": "TEXT", "style": "OpenSans"}
    ).set_placement((x, y - 100), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)

def add_dimension(p1, p2, offset=300):
    """Add a linear dimension."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.sqrt(dx * dx + dy * dy)
    # Determine offset direction
    if abs(dx) > abs(dy):
        # Horizontal dimension
        dim_point = ((p1[0] + p2[0]) / 2, p1[1] - offset)
    else:
        # Vertical dimension
        dim_point = (p1[0] - offset, (p1[1] + p2[1]) / 2)

    dim = msp.add_linear_dim(
        base=dim_point,
        p1=p1,
        p2=p2,
        dxfattribs={"layer": "DIMENSIONS"}
    )
    dim.render()


# ─── Layout Coordinates ─────────────────────────────────────────────
# Floor plan layout:
#
#  +------------------+-------------+
#  |                  |             |
#  |   Living Room    |   Kitchen   |
#  |   5.0 x 4.0m    |  3.0 x 4.0m|
#  |                  |             |
#  +--------+---------+------+------+
#           | Hallway        |
#  +--------+---------+------+------+
#  |                  |             |
#  |    Bedroom       |  Bathroom   |
#  |   4.0 x 3.5m    | 2.5 x 3.5m |
#  |                  |             |
#  +------------------+-------------+

ORIGIN_X = 0
ORIGIN_Y = 0

# Y coordinates
y_bottom = ORIGIN_Y
y_hall_bottom = y_bottom + BEDROOM_H
y_hall_top = y_hall_bottom + HALLWAY_W
y_top = y_hall_top + LIVING_H

# X coordinates
x_left = ORIGIN_X
x_mid = x_left + LIVING_W
x_right = x_mid + KITCHEN_W

# ─── Draw Exterior Walls ────────────────────────────────────────────
ext_corners = [
    (x_left, y_bottom),
    (x_right, y_bottom),
    (x_right, y_top),
    (x_left, y_top),
]
for i in range(4):
    draw_wall(ext_corners[i], ext_corners[(i + 1) % 4], EXT_WALL_THICK, "WALLS")

# ─── Draw Interior Walls ────────────────────────────────────────────
# Horizontal wall between bedroom row and hallway
draw_wall((x_left, y_hall_bottom), (x_right, y_hall_bottom), WALL_THICKNESS, "WALLS_INT")

# Horizontal wall between hallway and living row
draw_wall((x_left, y_hall_top), (x_right, y_hall_top), WALL_THICKNESS, "WALLS_INT")

# Vertical wall: living/bedroom | kitchen/bathroom
draw_wall((x_mid, y_bottom), (x_mid, y_top), WALL_THICKNESS, "WALLS_INT")

# ─── Doors ───────────────────────────────────────────────────────────
# Living room door (from hallway)
draw_door(x_left + 1500, y_hall_top, DOOR_WIDTH, "up")

# Kitchen door (from hallway)
draw_door(x_mid + 500, y_hall_top, DOOR_WIDTH, "up")

# Bedroom door (from hallway)
draw_door(x_left + 1500, y_hall_bottom, DOOR_WIDTH, "down")

# Bathroom door (from hallway)
draw_door(x_mid + 500, y_hall_bottom, DOOR_WIDTH, "down")

# Front door (exterior, south wall)
draw_door(x_left + LIVING_W / 2, y_bottom, DOOR_WIDTH, "up")

# ─── Windows ─────────────────────────────────────────────────────────
# Living room — west wall window
draw_window(x_left, y_hall_top + 1400, x_left, y_hall_top + 1400 + WINDOW_WIDTH)

# Living room — north wall window
draw_window(x_left + 1900, y_top, x_left + 1900 + WINDOW_WIDTH, y_top)

# Kitchen — north wall window
draw_window(x_mid + 900, y_top, x_mid + 900 + WINDOW_WIDTH, y_top)

# Bedroom — west wall window
draw_window(x_left, y_bottom + 1200, x_left, y_bottom + 1200 + WINDOW_WIDTH)

# Bedroom — south wall window
draw_window(x_left + 1000, y_bottom, x_left + 1000 + WINDOW_WIDTH, y_bottom)

# Bathroom — east wall window (small)
draw_window(x_right, y_bottom + 1500, x_right, y_bottom + 1500 + 800)

# ─── Room Labels ─────────────────────────────────────────────────────
add_room_label(x_left + LIVING_W/2, y_hall_top + LIVING_H/2, "LIVING ROOM",
               LIVING_W * LIVING_H / 1e6)
add_room_label(x_mid + KITCHEN_W/2, y_hall_top + KITCHEN_H/2, "KITCHEN",
               KITCHEN_W * KITCHEN_H / 1e6)
add_room_label(x_left + BEDROOM_W/2, y_bottom + BEDROOM_H/2, "BEDROOM",
               BEDROOM_W * BEDROOM_H / 1e6)
add_room_label(x_mid + BATH_W/2, y_bottom + BATH_H/2, "BATHROOM",
               BATH_W * BATH_H / 1e6)
add_room_label((x_left + x_right)/2, y_hall_bottom + HALLWAY_W/2, "HALLWAY",
               (x_right - x_left) * HALLWAY_W / 1e6)

# ─── Dimensions ──────────────────────────────────────────────────────
# Overall width
add_dimension((x_left, y_bottom), (x_right, y_bottom), offset=600)
# Overall height
add_dimension((x_left, y_bottom), (x_left, y_top), offset=600)
# Living room width
add_dimension((x_left, y_top), (x_mid, y_top), offset=-400)
# Kitchen width
add_dimension((x_mid, y_top), (x_right, y_top), offset=-400)

# ─── Title Block ─────────────────────────────────────────────────────
tb_x = x_right + 1000
tb_y = y_bottom

msp.add_text(
    "FLOOR PLAN — 2 BEDROOM APARTMENT",
    height=200,
    dxfattribs={"layer": "TITLEBLOCK"}
).set_placement((tb_x, tb_y + 1200))

msp.add_text(
    f"Total Area: {(x_right-x_left) * (y_top-y_bottom) / 1e6:.1f} m²",
    height=120,
    dxfattribs={"layer": "TITLEBLOCK"}
).set_placement((tb_x, tb_y + 900))

msp.add_text(
    "Scale: 1:100  |  Units: mm",
    height=100,
    dxfattribs={"layer": "TITLEBLOCK"}
).set_placement((tb_x, tb_y + 650))

msp.add_text(
    "Generated with ezdxf for LibreCAD",
    height=80,
    dxfattribs={"layer": "TITLEBLOCK"}
).set_placement((tb_x, tb_y + 450))

# ─── Save ────────────────────────────────────────────────────────────
import os
output_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(output_dir, "floor_plan.dxf")
doc.saveas(output_path)

print(f"Saved: {output_path}")
print(f"Open in LibreCAD: librecad {output_path}")
print(f"Total floor area: {(x_right-x_left) * (y_top-y_bottom) / 1e6:.1f} m²")
