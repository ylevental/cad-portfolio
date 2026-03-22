# FreeCAD Mechanical Models

[FreeCAD](https://www.freecad.org/) is an open-source parametric 3D modeler with a full Python API. These scripts create mechanical parts programmatically using the `Part` workbench.

## Files

### `bearing_block.py`

A flanged pillow-block bearing housing with:
- Rectangular base plate with 4× counterbored mounting holes
- Cylindrical housing with central bearing bore
- Top and bottom bore chamfers for shaft insertion
- Fused base-to-housing geometry

**Exports:** `.FCStd` (native), `.step` (interchange), `.stl` (3D printing)

### `hex_nut.py`

An ISO 4032-style M10 hex nut with:
- Hexagonal prism body (17mm across flats)
- Simplified thread grooves via torus cuts at each pitch
- Top and bottom corner chamfers
- Keyway slot in the bore

**Exports:** `.FCStd`, `.step`

## Screenshots

![Bearing Block](../screenshots/freecad_bearing_block.png)
![Hex Nut](../screenshots/freecad_hex_nut.png)

## Running

```bash
# Via Flatpak (Fedora)
flatpak run org.freecad.FreeCAD --console bearing_block.py
flatpak run org.freecad.FreeCAD --console hex_nut.py

# If FreeCAD is on PATH
freecad.cmd bearing_block.py

# Or open FreeCAD GUI → Macro → Execute Macro → select the .py file
```

## Dependencies

- FreeCAD 0.21+ (`flatpak install flathub org.freecad.FreeCAD`)
- No pip packages needed — uses FreeCAD's built-in `Part` and `Mesh` modules
