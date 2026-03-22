"""
Simple Building — FreeCAD BIM / IFC Script

Creates a small single-room building with:
- Four walls with a door opening and window opening
- A floor slab
- A flat roof slab
- IFC export

Usage:
    freecad.cmd simple_building.py

Requires:
    FreeCAD with Arch/BIM workbench (included by default)

Outputs:
    simple_building.FCStd — Native FreeCAD file
    simple_building.ifc   — IFC2x3 export
"""

import sys
import os

try:
    import FreeCAD
    import Part
    import Arch
    import Draft
except ImportError:
    FREECAD_PATH = "/usr/lib/freecad/lib"
    if os.path.exists(FREECAD_PATH):
        sys.path.append(FREECAD_PATH)
    import FreeCAD
    import Part
    import Arch
    import Draft

# ─── Parameters ──────────────────────────────────────────────────────
ROOM_LENGTH     = 6000.0   # mm (6 meters)
ROOM_WIDTH      = 4000.0   # mm (4 meters)
WALL_HEIGHT     = 2800.0   # mm (2.8 meters)
WALL_THICKNESS  = 200.0    # mm (200mm masonry)
SLAB_THICKNESS  = 200.0    # mm

DOOR_WIDTH      = 900.0
DOOR_HEIGHT     = 2100.0
WINDOW_WIDTH    = 1200.0
WINDOW_HEIGHT   = 1000.0
WINDOW_SILL     = 900.0    # Sill height from floor

# ─── Document Setup ─────────────────────────────────────────────────
doc = FreeCAD.newDocument("SimpleBuilding")

# ─── Helper: Create a wall from two points ───────────────────────────
def make_wall(p1, p2, name="Wall"):
    """Create an Arch Wall between two points."""
    line = Draft.makeLine(
        FreeCAD.Vector(p1[0], p1[1], 0),
        FreeCAD.Vector(p2[0], p2[1], 0)
    )
    wall = Arch.makeWall(line, length=None, width=WALL_THICKNESS, height=WALL_HEIGHT)
    wall.Label = name
    return wall

# ─── Create Walls ───────────────────────────────────────────────────
# Wall layout (exterior corners):
#  (0,W) ────── (L,W)
#   |              |
#   |    room      |
#   |              |
#  (0,0) ────── (L,0)

wall_south = make_wall((0, 0), (ROOM_LENGTH, 0), "Wall_South")
wall_east  = make_wall((ROOM_LENGTH, 0), (ROOM_LENGTH, ROOM_WIDTH), "Wall_East")
wall_north = make_wall((ROOM_LENGTH, ROOM_WIDTH), (0, ROOM_WIDTH), "Wall_North")
wall_west  = make_wall((0, ROOM_WIDTH), (0, 0), "Wall_West")

doc.recompute()

# ─── Door Opening (in south wall) ───────────────────────────────────
# Position door at 1/4 of south wall length
door_x = ROOM_LENGTH * 0.25 - DOOR_WIDTH / 2

door_sketch = Draft.makeRectangle(DOOR_WIDTH, DOOR_HEIGHT)
door_sketch.Placement = FreeCAD.Placement(
    FreeCAD.Vector(door_x, -WALL_THICKNESS/2, 0),
    FreeCAD.Rotation(0, 0, 0)
)

# Use Arch Window to create the door opening
try:
    door = Arch.makeWindowPreset(
        "Simple door",
        width=DOOR_WIDTH,
        height=DOOR_HEIGHT,
        h1=100, h2=100, h3=100,
        w1=50, w2=50,
        o1=0, o2=0,
        host=wall_south
    )
    door.Label = "FrontDoor"
    # Position the door
    door.Placement.Base = FreeCAD.Vector(door_x, 0, 0)
except Exception as e:
    print(f"Note: Door preset not available in headless mode: {e}")
    print("  Door opening will need to be added manually in the GUI.")

doc.recompute()

# ─── Window Opening (in east wall) ──────────────────────────────────
window_y = ROOM_WIDTH * 0.5 - WINDOW_WIDTH / 2

try:
    window = Arch.makeWindowPreset(
        "Open 1-pane",
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        h1=100, h2=100, h3=100,
        w1=50, w2=50,
        o1=0, o2=0,
        host=wall_east
    )
    window.Label = "EastWindow"
    window.Placement.Base = FreeCAD.Vector(ROOM_LENGTH, window_y, WINDOW_SILL)
except Exception as e:
    print(f"Note: Window preset not available in headless mode: {e}")

doc.recompute()

# ─── Floor Slab ─────────────────────────────────────────────────────
floor_rect = Draft.makeRectangle(ROOM_LENGTH, ROOM_WIDTH)
floor_rect.Placement.Base = FreeCAD.Vector(0, 0, -SLAB_THICKNESS)

floor_slab = Arch.makeStructure(floor_rect, height=SLAB_THICKNESS)
floor_slab.Label = "FloorSlab"

# ─── Roof Slab ──────────────────────────────────────────────────────
roof_rect = Draft.makeRectangle(
    ROOM_LENGTH + 400,  # 200mm overhang each side
    ROOM_WIDTH + 400
)
roof_rect.Placement.Base = FreeCAD.Vector(-200, -200, WALL_HEIGHT)

roof_slab = Arch.makeStructure(roof_rect, height=SLAB_THICKNESS)
roof_slab.Label = "RoofSlab"

doc.recompute()

# ─── Create Building Hierarchy ───────────────────────────────────────
site    = Arch.makeSite([], name="Site")
building = Arch.makeBuilding([], name="Building")
floor   = Arch.makeFloor([], name="GroundFloor")

# Add elements to floor
floor.addObjects([wall_south, wall_east, wall_north, wall_west, floor_slab, roof_slab])
building.addObject(floor)
site.addObject(building)

doc.recompute()

# ─── Export ──────────────────────────────────────────────────────────
output_dir = os.path.dirname(os.path.abspath(__file__))

fcstd_path = os.path.join(output_dir, "simple_building.FCStd")
ifc_path   = os.path.join(output_dir, "simple_building.ifc")

doc.saveAs(fcstd_path)
print(f"Saved: {fcstd_path}")

# IFC export
try:
    import exportIFC
    exportIFC.export([site], ifc_path)
    print(f"Saved: {ifc_path}")
except ImportError:
    try:
        import ifcopenshell
        Arch.exportIFC([site], ifc_path)
        print(f"Saved: {ifc_path}")
    except Exception as e:
        print(f"IFC export requires ifcopenshell: {e}")
        print("  Install with: pip install ifcopenshell")

print(f"\nBuilding: {ROOM_LENGTH/1000}m x {ROOM_WIDTH/1000}m")
print(f"Wall height: {WALL_HEIGHT/1000}m, thickness: {WALL_THICKNESS}mm")

FreeCAD.closeDocument("SimpleBuilding")
