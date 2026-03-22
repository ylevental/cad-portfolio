# LibreCAD — 2D DXF Drafting

[LibreCAD](https://librecad.org/) is a free 2D CAD application that works with DXF files. Since LibreCAD's scripting is limited, this project uses the Python [`ezdxf`](https://ezdxf.readthedocs.io/) library to generate DXF files programmatically, which are then opened in LibreCAD for viewing and editing.

## Files

### `floor_plan.py`

A 2-bedroom apartment floor plan with:
- Exterior walls (250mm) and interior partition walls (200mm)
- Door swings with 90° arcs
- Window symbols (triple-line convention)
- Room labels with calculated areas
- Linear dimensions
- Title block with project info
- Organized layers: `WALLS`, `DOORS`, `WINDOWS`, `DIMENSIONS`, `TEXT`, `TITLEBLOCK`

**Output:** `floor_plan.dxf`

## Screenshot

![Floor Plan in LibreCAD](../screenshots/librecad_floor_plan.png)

## Room Layout

```
+------------------+-------------+
|                  |             |
|   Living Room    |   Kitchen   |
|   5.0 × 4.0m    |  3.0 × 4.0m|
|                  |             |
+--------+---------+------+------+
         |    Hallway     |
+--------+---------+------+------+
|                  |             |
|    Bedroom       |  Bathroom   |
|   4.0 × 3.5m    | 2.5 × 3.5m |
|                  |             |
+------------------+-------------+
```

## Running

```bash
# Generate the DXF
pip install ezdxf
python floor_plan.py

# Open in LibreCAD
librecad floor_plan.dxf
```

## Tips for LibreCAD

- Use **View → Zoom → Auto** to fit the full drawing
- Toggle layers in the **Layer List** panel to isolate walls, doors, etc.
- The drawing uses mm units at 1:100 implied scale

## Dependencies

- `ezdxf` (`pip install ezdxf`)
- LibreCAD (`sudo dnf install librecad`) for viewing
