# OpenSCAD Models

[OpenSCAD](https://openscad.org/) is a programmer's CAD tool — geometry is defined entirely through code. There is no interactive modeling; the `.scad` source file *is* the model.

## Files

### `parametric_bracket.scad`

A configurable L-shaped mounting bracket with:
- Adjustable base/wall dimensions and thickness
- Mounting holes with configurable count and diameter
- Corner fillet reinforcement
- Triangular gusset stiffeners

All parameters are exposed via OpenSCAD's **Customizer** panel (Window → Customizer). Change a value, press F5 (Preview) or F6 (Render), and the model updates.

### `spur_gear.scad`

An involute-approximation spur gear with:
- Configurable tooth count, module, and pressure angle
- Central bore with keyway
- Hub extension
- Lightening holes (auto-enabled for larger gears)

Prints derived values (pitch diameter, outer diameter, root diameter) to the console.

## Screenshots

| Parametric Bracket | Spur Gear |
|---|---|
| ![Parametric Bracket](../screenshots/openscad_bracket.png) | ![Spur Gear](../screenshots/openscad_gear.png) |

## Running

```bash
# GUI
openscad parametric_bracket.scad

# Command-line render to STL
openscad -o bracket.stl parametric_bracket.scad

# Command-line render to PNG
openscad -o bracket.png --camera=40,20,30,0,0,0 parametric_bracket.scad

# Override parameters from command line
openscad -o custom_bracket.stl -D 'base_length=120' -D 'hole_diameter=8' parametric_bracket.scad
```

## Dependencies

- OpenSCAD (`sudo dnf install openscad`)
- No external libraries needed
