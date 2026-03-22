# FreeCAD BIM / IFC Models

[FreeCAD's Arch/BIM workbench](https://wiki.freecad.org/BIM_Workbench) provides tools for architectural modeling and IFC (Industry Foundation Classes) export. These scripts use the `Arch` and `Draft` modules to create building elements programmatically.

## Files

### `simple_building.py`

A single-room building demonstrating BIM workflows:
- 4 exterior walls (200mm masonry) created from Draft lines
- Door opening in the south wall
- Window opening in the east wall
- Floor slab and roof slab with overhang
- Full IFC spatial hierarchy: Site → Building → Floor → Elements

**Exports:** `.FCStd` (native), `.ifc` (IFC2x3 via `exportIFC`)

## Screenshot

![FreeCAD BIM Building](../screenshots/freecad_bim_building.png)

## IFC Spatial Hierarchy

```
IfcSite
  └── IfcBuilding
        └── IfcBuildingStorey (Ground Floor)
              ├── IfcWall × 4
              ├── IfcSlab (floor)
              └── IfcSlab (roof)
```

## Running

```bash
# Via Flatpak
flatpak run org.freecad.FreeCAD --console simple_building.py

# Or open in FreeCAD GUI and run as macro
```

## Dependencies

- FreeCAD 0.21+ with Arch workbench (included by default)
- Optional: `ifcopenshell` for IFC export (`pip install ifcopenshell`)

## Note

Door and window presets may not fully resolve in headless/console mode. Run in the FreeCAD GUI for the complete model with openings.
