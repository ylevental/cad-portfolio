"""
Simple BIM Building — Blender + Bonsai (IfcOpenShell) Script

Creates a small building using IfcOpenShell directly and exports IFC.
Can also be run inside Blender with Bonsai installed for visual inspection.

This script uses IfcOpenShell's pure-Python API to generate a valid IFC file,
demonstrating BIM authoring without requiring the Blender GUI.

Usage (standalone):
    pip install ifcopenshell
    python bim_building.py

Usage (inside Blender with Bonsai):
    Open Blender → Scripting workspace → Run Script
    Then: File → Open IFC Project → select the output .ifc

Outputs:
    bim_building.ifc — IFC4 building model
"""

import os
import sys
import time
import uuid
import math

try:
    import ifcopenshell
    import ifcopenshell.api
except ImportError:
    print("ERROR: ifcopenshell is required.")
    print("  pip install ifcopenshell")
    sys.exit(1)

# ─── Parameters ──────────────────────────────────────────────────────
BUILDING_NAME    = "Demo Pavilion"
ROOM_LENGTH      = 8.0    # meters
ROOM_WIDTH       = 6.0
WALL_HEIGHT      = 3.0
WALL_THICKNESS   = 0.2
SLAB_THICKNESS   = 0.25
ROOF_OVERHANG    = 0.3

DOOR_WIDTH       = 0.9
DOOR_HEIGHT      = 2.1
WINDOW_WIDTH     = 1.5
WINDOW_HEIGHT    = 1.2
WINDOW_SILL_Z    = 0.9

# ─── Create IFC File ────────────────────────────────────────────────
ifc = ifcopenshell.file(schema="IFC4")

# Project
project = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject", name="CAD Portfolio Demo")

# Units (metric)
ifcopenshell.api.run("unit.assign_unit", ifc, length={"is_metric": True, "raw": "METRES"})

# Geometric context
model_context = ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
body_context = ifcopenshell.api.run(
    "context.add_context", ifc,
    context_type="Model",
    context_identifier="Body",
    target_view="MODEL_VIEW",
    parent=model_context
)

# ─── Spatial Hierarchy ───────────────────────────────────────────────
site = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcSite", name="Default Site")
ifcopenshell.api.run("aggregate.assign_object", ifc, relating_object=project, products=[site])

building = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcBuilding", name=BUILDING_NAME)
ifcopenshell.api.run("aggregate.assign_object", ifc, relating_object=site, products=[building])

storey = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcBuildingStorey", name="Ground Floor")
storey.Elevation = 0.0
ifcopenshell.api.run("aggregate.assign_object", ifc, relating_object=building, products=[storey])

# ─── Helper: Extruded Rectangle ─────────────────────────────────────
def make_extruded_rect(context, x, y, z, dx, dy, dz):
    """Create a simple extruded rectangular solid with placement."""
    representation = ifcopenshell.api.run(
        "geometry.add_wall_representation", ifc,
        context=context,
        length=dx,
        height=dz,
        thickness=dy
    ) if False else None  # Wall representation is specialized, use generic instead

    # Build an extruded area solid manually
    point_list = ifc.createIfcCartesianPointList2D(
        [[0.0, 0.0], [dx, 0.0], [dx, dy], [0.0, dy]]
    )
    polyline_idx = ifc.createIfcIndexedPolyCurve(point_list, [ifc.createIfcLineIndex([1,2]),
                                                               ifc.createIfcLineIndex([2,3]),
                                                               ifc.createIfcLineIndex([3,4]),
                                                               ifc.createIfcLineIndex([4,1])])
    profile = ifc.createIfcArbitraryClosedProfileDef("AREA", None, polyline_idx)

    direction = ifc.createIfcDirection([0.0, 0.0, 1.0])
    solid = ifc.createIfcExtrudedAreaSolid(profile, None, direction, dz)

    representation = ifc.createIfcShapeRepresentation(
        context, "Body", "SweptSolid", [solid]
    )
    product_shape = ifc.createIfcProductDefinitionShape(None, None, [representation])

    return product_shape, (x, y, z)


def create_wall(name, x, y, length, thickness, height, angle_deg=0):
    """Create an IfcWall with extruded geometry."""
    wall = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall", name=name)

    # Create geometry (all numeric args must be float for ifcopenshell)
    profile = ifc.createIfcRectangleProfileDef("AREA", None, None, float(length), float(thickness))
    direction = ifc.createIfcDirection([0.0, 0.0, 1.0])
    solid = ifc.createIfcExtrudedAreaSolid(profile, None, direction, float(height))

    representation = ifc.createIfcShapeRepresentation(body_context, "Body", "SweptSolid", [solid])
    product_shape = ifc.createIfcProductDefinitionShape(None, None, [representation])
    wall.Representation = product_shape

    # Placement
    angle_rad = math.radians(float(angle_deg))
    origin = ifc.createIfcCartesianPoint([float(x), float(y), 0.0])
    dir_z = ifc.createIfcDirection([0.0, 0.0, 1.0])
    dir_x = ifc.createIfcDirection([math.cos(angle_rad), math.sin(angle_rad), 0.0])
    axis2 = ifc.createIfcAxis2Placement3D(origin, dir_z, dir_x)
    placement = ifc.createIfcLocalPlacement(None, axis2)
    wall.ObjectPlacement = placement

    ifcopenshell.api.run("spatial.assign_container", ifc, relating_structure=storey, products=[wall])
    return wall


def create_slab(name, x, y, z, length, width, thickness):
    """Create an IfcSlab."""
    slab = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcSlab", name=name)

    profile = ifc.createIfcRectangleProfileDef("AREA", None, None, float(length), float(width))
    direction = ifc.createIfcDirection([0.0, 0.0, 1.0])
    solid = ifc.createIfcExtrudedAreaSolid(profile, None, direction, float(thickness))

    representation = ifc.createIfcShapeRepresentation(body_context, "Body", "SweptSolid", [solid])
    product_shape = ifc.createIfcProductDefinitionShape(None, None, [representation])
    slab.Representation = product_shape

    origin = ifc.createIfcCartesianPoint([float(x), float(y), float(z)])
    axis2 = ifc.createIfcAxis2Placement3D(origin, None, None)
    placement = ifc.createIfcLocalPlacement(None, axis2)
    slab.ObjectPlacement = placement

    ifcopenshell.api.run("spatial.assign_container", ifc, relating_structure=storey, products=[slab])
    return slab


# ─── Build the Model ────────────────────────────────────────────────
print(f"Creating: {BUILDING_NAME}")
print(f"  Dimensions: {ROOM_LENGTH}m × {ROOM_WIDTH}m × {WALL_HEIGHT}m")

# Walls (centered on their length, positioned at midpoints)
# South wall
wall_s = create_wall("Wall_South",
    x=ROOM_LENGTH/2, y=0,
    length=ROOM_LENGTH, thickness=WALL_THICKNESS,
    height=WALL_HEIGHT, angle_deg=0)

# North wall
wall_n = create_wall("Wall_North",
    x=ROOM_LENGTH/2, y=ROOM_WIDTH,
    length=ROOM_LENGTH, thickness=WALL_THICKNESS,
    height=WALL_HEIGHT, angle_deg=0)

# East wall
wall_e = create_wall("Wall_East",
    x=ROOM_LENGTH, y=ROOM_WIDTH/2,
    length=ROOM_WIDTH, thickness=WALL_THICKNESS,
    height=WALL_HEIGHT, angle_deg=90)

# West wall
wall_w = create_wall("Wall_West",
    x=0, y=ROOM_WIDTH/2,
    length=ROOM_WIDTH, thickness=WALL_THICKNESS,
    height=WALL_HEIGHT, angle_deg=90)

# Floor slab
floor_slab = create_slab("Floor_Slab",
    x=ROOM_LENGTH/2, y=ROOM_WIDTH/2, z=-SLAB_THICKNESS,
    length=ROOM_LENGTH + 2*WALL_THICKNESS,
    width=ROOM_WIDTH + 2*WALL_THICKNESS,
    thickness=SLAB_THICKNESS)

# Roof slab (with overhang)
roof_slab = create_slab("Roof_Slab",
    x=ROOM_LENGTH/2, y=ROOM_WIDTH/2, z=WALL_HEIGHT,
    length=ROOM_LENGTH + 2*ROOF_OVERHANG,
    width=ROOM_WIDTH + 2*ROOF_OVERHANG,
    thickness=SLAB_THICKNESS)

# ─── Add Property Sets ──────────────────────────────────────────────
# Material for walls
concrete = ifcopenshell.api.run("material.add_material", ifc, name="Concrete C30/37")
for wall in [wall_s, wall_n, wall_e, wall_w]:
    ifcopenshell.api.run("material.assign_material", ifc, products=[wall], material=concrete)

# Custom properties
for wall in [wall_s, wall_n, wall_e, wall_w]:
    pset = ifcopenshell.api.run("pset.add_pset", ifc, product=wall, name="Pset_WallCommon")
    ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={
        "IsExternal": True,
        "FireRating": "REI 60",
        "ThermalTransmittance": 0.25,
    })

# ─── Export ──────────────────────────────────────────────────────────
output_dir = os.path.dirname(os.path.abspath(__file__))
ifc_path = os.path.join(output_dir, "bim_building.ifc")

ifc.write(ifc_path)
print(f"\nSaved: {ifc_path}")
print(f"Open in Blender+Bonsai: File → Open IFC Project → {ifc_path}")
print(f"\nIFC entities created: {len(ifc.by_type('IfcProduct'))}")
print(f"  Walls: {len(ifc.by_type('IfcWall'))}")
print(f"  Slabs: {len(ifc.by_type('IfcSlab'))}")
