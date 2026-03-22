# Open-Source CAD Portfolio

Scripted parametric models demonstrating proficiency with open-source CAD tools. Each project is fully code-defined — no manual GUI clicks required to reproduce the geometry.

## Tools & Projects

### OpenSCAD — Pure Code CAD

| File | Description |
|------|-------------|
| [`openscad/parametric_bracket.scad`](openscad/parametric_bracket.scad) | Configurable L-bracket with mounting holes, fillets, and gusset reinforcement. All parameters exposed via OpenSCAD's Customizer. |
| [`openscad/spur_gear.scad`](openscad/spur_gear.scad) | Involute spur gear generator with configurable tooth count, module, bore, keyway, and lightening holes. |

**Run:** `openscad parametric_bracket.scad` or open in OpenSCAD GUI and use the Customizer panel.

![Parametric Bracket](screenshots/openscad_bracket.png)
![Spur Gear](screenshots/openscad_gear.png)

---

### FreeCAD — Python-Scripted Mechanical Parts

| File | Description |
|------|-------------|
| [`freecad/bearing_block.py`](freecad/bearing_block.py) | Flanged pillow-block bearing housing with bore chamfers, counterbored mounting holes. Exports STEP + STL. |
| [`freecad/hex_nut.py`](freecad/hex_nut.py) | ISO 4032-style M10 hex nut with thread grooves, chamfers, and keyway. Exports STEP. |

**Run:** `freecad.cmd bearing_block.py` (Flatpak: `flatpak run org.freecad.FreeCAD --console bearing_block.py`)

![Bearing Block](screenshots/freecad_bearing_block.png)
![Hex Nut](screenshots/freecad_hex_nut.png)

---

### FreeCAD BIM / IFC — Architectural Modeling

| File | Description |
|------|-------------|
| [`freecad-bim/simple_building.py`](freecad-bim/simple_building.py) | Single-room building with walls, door/window openings, floor slab, and roof. Uses the Arch workbench and exports IFC. |

**Run:** `freecad.cmd simple_building.py`

![FreeCAD BIM Building](screenshots/freecad_bim_building.png)

---

### LibreCAD — 2D DXF Drafting (via `ezdxf`)

| File | Description |
|------|-------------|
| [`librecad/floor_plan.py`](librecad/floor_plan.py) | Complete 2-bedroom apartment floor plan with layered walls, door swings, window symbols, room labels, and dimensions. |

**Run:** `python floor_plan.py && librecad floor_plan.dxf`

![Floor Plan in LibreCAD](screenshots/librecad_floor_plan.png)

---

### Blender + Bonsai — BIM / IFC4 Authoring

| File | Description |
|------|-------------|
| [`blender-bonsai/bim_building.py`](blender-bonsai/bim_building.py) | IFC4 pavilion with walls, slabs, material assignments, and property sets (`Pset_WallCommon`). Uses IfcOpenShell's API directly. |

**Run:** `python bim_building.py` then open the `.ifc` in Blender via File → Open IFC Project.

![Bonsai BIM Building](screenshots/blender_bonsai_building.png)

---

### SolveSpace — Constraint-Based Parametric Sketching

| File | Description |
|------|-------------|
| [`solvespace/constrained_sketch.py`](solvespace/constrained_sketch.py) | L-bracket profile built entirely from geometric constraints (horizontal, vertical, distance). Demonstrates the SolveSpace constraint solver via `python-solvespace`. Exports SVG. |

**Run:** `python constrained_sketch.py`

![SolveSpace Bracket Profile](screenshots/solvespace_bracket.svg)

---

## Installation (Fedora 43)

```bash
# Core packages
sudo dnf install openscad librecad blender

# Flatpak packages (FreeCAD and SolveSpace are not in Fedora repos)
flatpak install flathub org.freecad.FreeCAD
flatpak install flathub com.solvespace.SolveSpace

# Bonsai (BlenderBIM): install from Blender's extension browser
#   Edit → Preferences → Get Extensions → search "Bonsai" → Install

# Python dependencies
pip install ezdxf ifcopenshell python-solvespace
```

## File Formats Produced

| Format | Tool | Purpose |
|--------|------|---------|
| `.scad` | OpenSCAD | Source code IS the model |
| `.FCStd` | FreeCAD | Native parametric file |
| `.step` / `.stp` | FreeCAD | Industry-standard 3D exchange |
| `.stl` | FreeCAD | 3D printing mesh |
| `.ifc` | FreeCAD BIM, Bonsai | Building Information Model |
| `.dxf` | ezdxf → LibreCAD | 2D CAD drawing exchange |
| `.svg` | python-solvespace | 2D vector visualization |

## Design Philosophy

Every model in this portfolio is **code-first**: geometry is defined programmatically through scripts, not through manual GUI interaction. This approach enables:

- **Version control** — diffs show exactly what changed in the design
- **Parametric flexibility** — change a variable, regenerate the model
- **Reproducibility** — anyone with the tools can rebuild from source
- **Automation** — batch generation, CI/CD integration, testing

## License

MIT
