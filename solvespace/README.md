# SolveSpace — Constraint-Based Parametric Sketching

[SolveSpace](https://solvespace.com/) is a lightweight parametric 2D/3D CAD tool built around a geometric constraint solver. This project uses [`python-solvespace`](https://pypi.org/project/python-solvespace/), a Python binding to SolveSpace's core solver library, to build constrained sketches programmatically.

## Files

### `constrained_sketch.py`

An L-bracket profile defined entirely by geometric constraints:
- 7 vertices forming a stepped L-shape
- Horizontal and vertical constraints on all edges
- Distance constraints for dimensions (80mm × 60mm overall)
- A mounting hole positioned by distance constraints from edges
- SVG export of the solved geometry

**Output:** `bracket_profile.svg`

## Screenshot

![SolveSpace Bracket Profile](../screenshots/solvespace_bracket.svg)

## How Constraint Solving Works

Instead of specifying coordinates directly, you define *relationships*:

```
"This line is horizontal"
"These two points are 80mm apart"
"This line is perpendicular to that one"
"This circle is 10mm from the bottom edge"
```

The solver finds coordinates that satisfy all constraints simultaneously. Change one dimension and the entire sketch adapts — this is the core of parametric CAD.

## Running

```bash
pip install python-solvespace
python constrained_sketch.py
```

Expected output:
```
Constraint system solved successfully!

Solved point coordinates:
  p1: (80.00, 0.00)
  p2: (0.00, 0.00)
  p3: (0.00, 60.00)
  ...
  hole: (40.00, 10.00)

Saved: bracket_profile.svg
```

## SolveSpace GUI

The SolveSpace GUI application is a separate tool for interactive constraint-based modeling. Install it via Flatpak:

```bash
flatpak install flathub com.solvespace.SolveSpace
flatpak run com.solvespace.SolveSpace
```

The GUI uses the same constraint solver demonstrated in this script.

## Dependencies

- `python-solvespace` (`pip install python-solvespace`)
- SolveSpace GUI is optional (`flatpak install flathub com.solvespace.SolveSpace`)
