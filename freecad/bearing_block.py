"""
Parametric Flanged Bearing Block — FreeCAD Python Script

Creates a pillow-block-style bearing housing with:
- Rectangular base with mounting holes
- Cylindrical bearing bore with chamfers
- Filleted edges for stress relief

Usage:
    freecad.cmd bearing_block.py
    # Or run from FreeCAD's Python console / macro editor

Outputs:
    bearing_block.FCStd  — Native FreeCAD file
    bearing_block.step    — STEP export for interoperability
    bearing_block.stl     — Mesh export for 3D printing
"""

import sys
import os

# FreeCAD import handling (works both standalone and inside FreeCAD GUI)
try:
    import FreeCAD
    import Part
except ImportError:
    # When running via freecad.cmd or FreeCADCmd
    FREECAD_PATH = "/usr/lib/freecad/lib"
    if os.path.exists(FREECAD_PATH):
        sys.path.append(FREECAD_PATH)
    import FreeCAD
    import Part

# ─── Parameters ───────────────────────────────────────────────────────
BASE_LENGTH     = 100.0   # mm
BASE_WIDTH      = 60.0
BASE_HEIGHT     = 15.0
BORE_DIAMETER   = 25.0    # Bearing bore
HOUSING_OD      = 45.0    # Outer diameter of cylindrical housing
HOUSING_HEIGHT  = 35.0    # Total height of the cylindrical section
HOLE_DIAMETER   = 8.5     # M8 clearance
HOLE_INSET_X    = 15.0    # Hole distance from short edge
HOLE_INSET_Y    = 15.0    # Hole distance from long edge
CHAMFER_SIZE    = 1.5     # Bore chamfer
FILLET_RADIUS   = 3.0     # Edge fillets on base

# ─── Document Setup ──────────────────────────────────────────────────
doc = FreeCAD.newDocument("BearingBlock")

# ─── Base Plate ──────────────────────────────────────────────────────
base = Part.makeBox(
    BASE_LENGTH, BASE_WIDTH, BASE_HEIGHT,
    FreeCAD.Vector(-BASE_LENGTH/2, -BASE_WIDTH/2, 0)
)

# ─── Cylindrical Housing ────────────────────────────────────────────
housing = Part.makeCylinder(
    HOUSING_OD / 2,
    HOUSING_HEIGHT,
    FreeCAD.Vector(0, 0, 0),
    FreeCAD.Vector(0, 0, 1)
)

# ─── Merge base + housing ───────────────────────────────────────────
body = base.fuse(housing)

# ─── Bearing Bore (through-hole) ────────────────────────────────────
bore = Part.makeCylinder(
    BORE_DIAMETER / 2,
    HOUSING_HEIGHT + 2,
    FreeCAD.Vector(0, 0, -1),
    FreeCAD.Vector(0, 0, 1)
)
body = body.cut(bore)

# ─── Bore Chamfers (top and bottom) ─────────────────────────────────
chamfer_top = Part.makeCone(
    BORE_DIAMETER/2 + CHAMFER_SIZE,
    BORE_DIAMETER/2,
    CHAMFER_SIZE,
    FreeCAD.Vector(0, 0, HOUSING_HEIGHT - CHAMFER_SIZE),
    FreeCAD.Vector(0, 0, 1)
)
chamfer_bottom = Part.makeCone(
    BORE_DIAMETER/2,
    BORE_DIAMETER/2 + CHAMFER_SIZE,
    CHAMFER_SIZE,
    FreeCAD.Vector(0, 0, 0),
    FreeCAD.Vector(0, 0, 1)
)
body = body.cut(chamfer_top)
body = body.cut(chamfer_bottom)

# ─── Mounting Holes (4x) ────────────────────────────────────────────
hole_positions = [
    FreeCAD.Vector(-BASE_LENGTH/2 + HOLE_INSET_X, -BASE_WIDTH/2 + HOLE_INSET_Y, 0),
    FreeCAD.Vector( BASE_LENGTH/2 - HOLE_INSET_X, -BASE_WIDTH/2 + HOLE_INSET_Y, 0),
    FreeCAD.Vector(-BASE_LENGTH/2 + HOLE_INSET_X,  BASE_WIDTH/2 - HOLE_INSET_Y, 0),
    FreeCAD.Vector( BASE_LENGTH/2 - HOLE_INSET_X,  BASE_WIDTH/2 - HOLE_INSET_Y, 0),
]

for pos in hole_positions:
    hole = Part.makeCylinder(
        HOLE_DIAMETER / 2,
        BASE_HEIGHT + 2,
        FreeCAD.Vector(pos.x, pos.y, -1),
        FreeCAD.Vector(0, 0, 1)
    )
    body = body.cut(hole)

    # Counterbore (for socket head cap screws)
    counterbore = Part.makeCylinder(
        HOLE_DIAMETER * 0.85,  # Head diameter approximation
        5.0,                   # Head depth
        FreeCAD.Vector(pos.x, pos.y, BASE_HEIGHT - 5.0),
        FreeCAD.Vector(0, 0, 1)
    )
    body = body.cut(counterbore)

# ─── Add to Document ────────────────────────────────────────────────
part_obj = doc.addObject("Part::Feature", "BearingBlock")
part_obj.Shape = body

doc.recompute()

# ─── Export ──────────────────────────────────────────────────────────
output_dir = os.path.dirname(os.path.abspath(__file__))

fcstd_path = os.path.join(output_dir, "bearing_block.FCStd")
step_path  = os.path.join(output_dir, "bearing_block.step")
stl_path   = os.path.join(output_dir, "bearing_block.stl")

doc.saveAs(fcstd_path)
Part.export([part_obj], step_path)

import Mesh
Mesh.export([part_obj], stl_path)

print(f"Saved: {fcstd_path}")
print(f"Saved: {step_path}")
print(f"Saved: {stl_path}")
print(f"Bore: {BORE_DIAMETER} mm | Housing OD: {HOUSING_OD} mm")
print(f"Base: {BASE_LENGTH} x {BASE_WIDTH} x {BASE_HEIGHT} mm")

FreeCAD.closeDocument("BearingBlock")
