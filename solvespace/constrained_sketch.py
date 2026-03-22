"""
Constraint-Based 2D Sketch — Pure Python Implementation

Demonstrates parametric constraint solving by building an L-bracket profile
defined entirely by geometric constraints (distances, horizontal/vertical
alignment) rather than explicit coordinates.

Includes a minimal 2D constraint solver using Newton-Raphson iteration —
the same mathematical approach used by SolveSpace's core engine.

No external dependencies required. Outputs SVG and DXF files.
The DXF can be imported into SolveSpace for further editing.

Usage:
    python constrained_sketch.py

Outputs:
    bracket_profile.svg  — Visual render of the solved sketch
    bracket_profile.dxf  — DXF import for SolveSpace / LibreCAD
"""

import math
import os

# ═════════════════════════════════════════════════════════════════════
# MINIMAL 2D CONSTRAINT SOLVER
# Uses Newton-Raphson iteration to find point positions that satisfy
# all geometric constraints simultaneously.
# ═════════════════════════════════════════════════════════════════════

class Point2D:
    """A 2D point with x, y as free variables."""
    def __init__(self, name, x_guess, y_guess):
        self.name = name
        self.x = float(x_guess)
        self.y = float(y_guess)

    def __repr__(self):
        return f"{self.name}({self.x:.2f}, {self.y:.2f})"


class Constraint:
    """Base constraint — subclasses define error() and jacobian()."""
    def error(self):
        raise NotImplementedError

    def jacobian(self, variables):
        """Partial derivatives of error with respect to each variable."""
        raise NotImplementedError


class FixedConstraint(Constraint):
    """Pin a point to exact coordinates."""
    def __init__(self, point, x, y):
        self.point = point
        self.tx, self.ty = x, y

    def error(self):
        return [(self.point.x - self.tx), (self.point.y - self.ty)]

    def jacobian(self, variables):
        rows = []
        for target_attr in [(self.point, 'x'), (self.point, 'y')]:
            row = []
            for (pt, attr) in variables:
                row.append(1.0 if (pt is target_attr[0] and attr == target_attr[1]) else 0.0)
            rows.append(row)
        return rows


class HorizontalConstraint(Constraint):
    """Two points share the same y-coordinate."""
    def __init__(self, p1, p2):
        self.p1, self.p2 = p1, p2

    def error(self):
        return [self.p1.y - self.p2.y]

    def jacobian(self, variables):
        row = []
        for (pt, attr) in variables:
            if pt is self.p1 and attr == 'y':
                row.append(1.0)
            elif pt is self.p2 and attr == 'y':
                row.append(-1.0)
            else:
                row.append(0.0)
        return [row]


class VerticalConstraint(Constraint):
    """Two points share the same x-coordinate."""
    def __init__(self, p1, p2):
        self.p1, self.p2 = p1, p2

    def error(self):
        return [self.p1.x - self.p2.x]

    def jacobian(self, variables):
        row = []
        for (pt, attr) in variables:
            if pt is self.p1 and attr == 'x':
                row.append(1.0)
            elif pt is self.p2 and attr == 'x':
                row.append(-1.0)
            else:
                row.append(0.0)
        return [row]


class DistanceConstraint(Constraint):
    """Distance between two points equals a target value."""
    def __init__(self, p1, p2, dist):
        self.p1, self.p2 = p1, p2
        self.dist = dist

    def error(self):
        dx = self.p1.x - self.p2.x
        dy = self.p1.y - self.p2.y
        actual = math.sqrt(dx*dx + dy*dy)
        return [actual - self.dist]

    def jacobian(self, variables):
        dx = self.p1.x - self.p2.x
        dy = self.p1.y - self.p2.y
        d = math.sqrt(dx*dx + dy*dy)
        if d < 1e-12:
            d = 1e-12
        row = []
        for (pt, attr) in variables:
            if pt is self.p1 and attr == 'x':
                row.append(dx / d)
            elif pt is self.p1 and attr == 'y':
                row.append(dy / d)
            elif pt is self.p2 and attr == 'x':
                row.append(-dx / d)
            elif pt is self.p2 and attr == 'y':
                row.append(-dy / d)
            else:
                row.append(0.0)
        return [row]


class HDistanceConstraint(Constraint):
    """Horizontal distance (x difference) between two points."""
    def __init__(self, p1, p2, dist):
        self.p1, self.p2 = p1, p2
        self.dist = dist

    def error(self):
        return [self.p1.x - self.p2.x - self.dist]

    def jacobian(self, variables):
        row = []
        for (pt, attr) in variables:
            if pt is self.p1 and attr == 'x':
                row.append(1.0)
            elif pt is self.p2 and attr == 'x':
                row.append(-1.0)
            else:
                row.append(0.0)
        return [row]


class VDistanceConstraint(Constraint):
    """Vertical distance (y difference) between two points."""
    def __init__(self, p1, p2, dist):
        self.p1, self.p2 = p1, p2
        self.dist = dist

    def error(self):
        return [self.p1.y - self.p2.y - self.dist]

    def jacobian(self, variables):
        row = []
        for (pt, attr) in variables:
            if pt is self.p1 and attr == 'y':
                row.append(1.0)
            elif pt is self.p2 and attr == 'y':
                row.append(-1.0)
            else:
                row.append(0.0)
        return [row]


def solve(points, constraints, max_iter=100, tol=1e-10):
    """
    Newton-Raphson solver for 2D geometric constraints.

    Builds the Jacobian matrix and error vector, then iteratively
    adjusts point coordinates until all constraints are satisfied.
    """
    # Collect all free variables: (point, 'x') and (point, 'y')
    variables = []
    for p in points:
        variables.append((p, 'x'))
        variables.append((p, 'y'))

    n_vars = len(variables)

    for iteration in range(max_iter):
        # Build error vector and Jacobian
        errors = []
        jac_rows = []
        for c in constraints:
            errs = c.error()
            jrows = c.jacobian(variables)
            errors.extend(errs)
            jac_rows.extend(jrows)

        n_eqs = len(errors)

        # Check convergence
        max_err = max(abs(e) for e in errors)
        if max_err < tol:
            print(f"  Converged in {iteration} iterations (max error: {max_err:.2e})")
            return True

        # Solve J * delta = -error using least-squares (J^T J delta = J^T (-error))
        # This handles over/under-determined systems gracefully.
        JtJ = [[0.0]*n_vars for _ in range(n_vars)]
        Jte = [0.0]*n_vars

        for i in range(n_eqs):
            for j in range(n_vars):
                Jte[j] -= jac_rows[i][j] * errors[i]
                for k in range(n_vars):
                    JtJ[j][k] += jac_rows[i][j] * jac_rows[i][k]

        # Add small damping for numerical stability (Levenberg-Marquardt style)
        for j in range(n_vars):
            JtJ[j][j] += 1e-8

        # Solve via Gaussian elimination
        delta = gauss_solve(JtJ, Jte)
        if delta is None:
            print("  WARNING: Singular Jacobian")
            return False

        # Apply corrections
        for idx, (pt, attr) in enumerate(variables):
            setattr(pt, attr, getattr(pt, attr) + delta[idx])

    print(f"  WARNING: Did not converge after {max_iter} iterations (max error: {max_err:.2e})")
    return False


def gauss_solve(A, b):
    """Solve A*x = b via Gaussian elimination with partial pivoting."""
    n = len(b)
    # Augmented matrix
    M = [A[i][:] + [b[i]] for i in range(n)]

    for col in range(n):
        # Partial pivot
        max_row = col
        for row in range(col+1, n):
            if abs(M[row][col]) > abs(M[max_row][col]):
                max_row = row
        M[col], M[max_row] = M[max_row], M[col]

        if abs(M[col][col]) < 1e-15:
            return None

        # Eliminate
        for row in range(col+1, n):
            factor = M[row][col] / M[col][col]
            for j in range(col, n+1):
                M[row][j] -= factor * M[col][j]

    # Back-substitute
    x = [0.0]*n
    for i in range(n-1, -1, -1):
        x[i] = M[i][n]
        for j in range(i+1, n):
            x[i] -= M[i][j] * x[j]
        x[i] /= M[i][i]

    return x


# ═════════════════════════════════════════════════════════════════════
# BRACKET PROFILE DEFINITION
# ═════════════════════════════════════════════════════════════════════
#
#   p4 ─────── p3
#   |           |
#   |           p5
#   |            |
#   |            p6 ──── p7
#   |                     |
#   p1 ────────────────── p8
#
#   Plus a mounting hole at p_hole.

print("=" * 60)
print("2D Constraint Solver — L-Bracket Profile")
print("=" * 60)

# Points with initial guesses (solver will adjust these)
p1 = Point2D("p1",  0,  0)
p4 = Point2D("p4",  0, 55)    # Guess slightly off from target
p3 = Point2D("p3", 18, 55)
p5 = Point2D("p5", 18, 18)
p6 = Point2D("p6", 58, 18)
p7 = Point2D("p7", 78, 18)
p8 = Point2D("p8", 78,  0)

# Mounting hole center
p_hole = Point2D("hole", 45, 9)

points = [p1, p4, p3, p5, p6, p7, p8, p_hole]

# ─── Constraints ─────────────────────────────────────────────────────
constraints = [
    # Fix origin
    FixedConstraint(p1, 0, 0),

    # Horizontal edges
    HorizontalConstraint(p1, p8),    # Bottom edge
    HorizontalConstraint(p4, p3),    # Top edge
    HorizontalConstraint(p5, p6),    # Inner step horizontal
    HorizontalConstraint(p6, p7),    # Lower step horizontal

    # Vertical edges
    VerticalConstraint(p1, p4),      # Left edge
    VerticalConstraint(p3, p5),      # Inner vertical
    VerticalConstraint(p7, p8),      # Right edge

    # Dimensional constraints (mm)
    HDistanceConstraint(p8, p1, 80),   # Overall width
    VDistanceConstraint(p4, p1, 60),   # Overall height
    HDistanceConstraint(p3, p4, 20),   # Top flange width
    VDistanceConstraint(p3, p5, 40),   # Inner wall height
    VDistanceConstraint(p7, p8, 20),   # Step height (right side)

    # Hole positioning
    HDistanceConstraint(p_hole, p1, 40),   # 40mm from left
    VDistanceConstraint(p_hole, p1, 10),   # 10mm from bottom
]

# ─── Solve ───────────────────────────────────────────────────────────
print(f"\nPoints: {len(points)} ({len(points)*2} unknowns)")
print(f"Constraints: {len(constraints)} ({sum(len(c.error()) for c in constraints)} equations)")
print(f"\nSolving...\n")

success = solve(points, constraints)

if success:
    print("\n✓ All constraints satisfied!")
else:
    print("\n✗ Solver failed")
    exit(1)

print("\nSolved coordinates:")
for p in points:
    print(f"  {p}")

# ═════════════════════════════════════════════════════════════════════
# SVG EXPORT
# ═════════════════════════════════════════════════════════════════════

def export_svg(points_dict, edges, hole, filename):
    """Generate an SVG visualization of the bracket profile."""
    margin = 30
    scale = 5

    all_x = [p[0] for p in points_dict.values()]
    all_y = [p[1] for p in points_dict.values()]
    max_y = max(all_y)
    w = (max(all_x) - min(all_x)) * scale + 2 * margin + 120
    h = (max(all_y) - min(all_y)) * scale + 2 * margin + 50

    # Convert model coords to screen coords (flip Y)
    def to_screen(mx, my):
        return margin + mx * scale, h - margin - my * scale

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}">',
        f'  <rect width="100%" height="100%" fill="#1a1a2e"/>',
    ]

    # Draw edges
    for (a, b) in edges:
        sx1, sy1 = to_screen(*points_dict[a])
        sx2, sy2 = to_screen(*points_dict[b])
        lines.append(
            f'  <line x1="{sx1}" y1="{sy1}" x2="{sx2}" y2="{sy2}" '
            f'stroke="#00d4ff" stroke-width="3" stroke-linecap="round"/>'
        )

    # Draw mounting hole
    hx, hy = points_dict[hole]
    shx, shy = to_screen(hx, hy)
    lines.append(f'  <circle cx="{shx}" cy="{shy}" r="{4*scale}" fill="none" '
                 f'stroke="#ff6b6b" stroke-width="2"/>')
    lines.append(f'  <line x1="{shx-8}" y1="{shy}" x2="{shx+8}" y2="{shy}" '
                 f'stroke="#ff6b6b" stroke-width="1.5"/>')
    lines.append(f'  <line x1="{shx}" y1="{shy-8}" x2="{shx}" y2="{shy+8}" '
                 f'stroke="#ff6b6b" stroke-width="1.5"/>')

    # Draw point markers
    for name, (x, y) in points_dict.items():
        if name == hole:
            continue
        sx, sy = to_screen(x, y)
        lines.append(f'  <circle cx="{sx}" cy="{sy}" r="4" fill="#ffd93d"/>')

    # Draw dimension labels (in screen space, so text renders correctly)
    dim_pairs = [
        ("p1", "p8", "80mm", 0, 20),       # below: overall width
        ("p1", "p4", "60mm", -25, 0),       # left: overall height
        ("p4", "p3", "20mm", 0, -12),       # above: top flange width
        ("p7", "p8", "20mm", 22, 0),        # right: step height
        ("p3", "p5", "40mm", 18, 0),        # inner wall height
    ]
    for (a, b, label, dx, dy) in dim_pairs:
        sx1, sy1 = to_screen(*points_dict[a])
        sx2, sy2 = to_screen(*points_dict[b])
        mx, my = (sx1+sx2)/2 + dx, (sy1+sy2)/2 + dy
        lines.append(
            f'  <text x="{mx}" y="{my}" fill="#ffd93d" '
            f'font-family="monospace" font-size="13" '
            f'text-anchor="middle" dominant-baseline="middle">{label}</text>'
        )

    # Draw dimension lines (thin dashed lines alongside the labels)
    for (a, b, label, dx, dy) in dim_pairs:
        sx1, sy1 = to_screen(*points_dict[a])
        sx2, sy2 = to_screen(*points_dict[b])
        # Offset the dimension line in the same direction as the label
        ox = dx * 0.6
        oy = dy * 0.6
        lines.append(
            f'  <line x1="{sx1+ox}" y1="{sy1+oy}" x2="{sx2+ox}" y2="{sy2+oy}" '
            f'stroke="#ffd93d" stroke-width="0.8" stroke-dasharray="4,3" opacity="0.5"/>'
        )

    # Title
    lines.append(
        f'  <text x="{margin}" y="22" fill="#eee" font-family="monospace" '
        f'font-size="15" font-weight="bold">Constraint Solver Demo — L-Bracket Profile</text>'
    )
    lines.append(
        f'  <text x="{margin}" y="40" fill="#888" font-family="monospace" '
        f'font-size="11">Pure Python Newton-Raphson · {len(points_dict)} points '
        f'· {len(constraints)} constraints</text>'
    )

    lines.append('</svg>')
    return "\n".join(lines)


# Build point dict and edge list
pts = {p.name: (p.x, p.y) for p in points}
outline_edges = [
    ("p1", "p8"), ("p8", "p7"), ("p7", "p6"),
    ("p6", "p5"), ("p5", "p3"), ("p3", "p4"),
    ("p4", "p1"),
]

output_dir = os.path.dirname(os.path.abspath(__file__))

# Write SVG
svg_content = export_svg(pts, outline_edges, "hole", "bracket_profile.svg")
svg_path = os.path.join(output_dir, "bracket_profile.svg")
with open(svg_path, "w") as f:
    f.write(svg_content)
print(f"\nSaved: {svg_path}")


# ═════════════════════════════════════════════════════════════════════
# DXF EXPORT (minimal, no dependencies)
# ═════════════════════════════════════════════════════════════════════

def export_dxf(points_dict, edges, hole_center, hole_radius, filename):
    """Generate a minimal DXF file (R12 format) that SolveSpace can import."""
    lines = [
        "0", "SECTION",
        "2", "ENTITIES",
    ]

    # Outline edges
    for (a, b) in edges:
        x1, y1 = points_dict[a]
        x2, y2 = points_dict[b]
        lines.extend([
            "0", "LINE",
            "8", "OUTLINE",     # Layer
            "10", f"{x1:.6f}",  # Start X
            "20", f"{y1:.6f}",  # Start Y
            "30", "0.0",        # Start Z
            "11", f"{x2:.6f}",  # End X
            "21", f"{y2:.6f}",  # End Y
            "31", "0.0",        # End Z
        ])

    # Mounting hole
    hx, hy = points_dict[hole_center]
    lines.extend([
        "0", "CIRCLE",
        "8", "HOLES",
        "10", f"{hx:.6f}",
        "20", f"{hy:.6f}",
        "30", "0.0",
        "40", f"{hole_radius:.6f}",
    ])

    lines.extend([
        "0", "ENDSEC",
        "0", "EOF",
    ])

    return "\n".join(lines)


dxf_content = export_dxf(pts, outline_edges, "hole", 4.0, "bracket_profile.dxf")
dxf_path = os.path.join(output_dir, "bracket_profile.dxf")
with open(dxf_path, "w") as f:
    f.write(dxf_content)
print(f"Saved: {dxf_path}")

print(f"\nOpen in SolveSpace:  flatpak run com.solvespace.SolveSpace {dxf_path}")
print(f"Open in LibreCAD:    librecad {dxf_path}")

# ═════════════════════════════════════════════════════════════════════
# DEMONSTRATE PARAMETRIC FLEXIBILITY
# ═════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("Parametric demo: changing overall width from 80mm to 120mm")
print("=" * 60)

# Reset points to new guesses
p1.x, p1.y = 0, 0
p4.x, p4.y = 0, 55
p3.x, p3.y = 18, 55
p5.x, p5.y = 18, 18
p6.x, p6.y = 58, 18
p7.x, p7.y = 118, 18
p8.x, p8.y = 118, 0
p_hole.x, p_hole.y = 60, 9

# Replace the width constraint
constraints[8] = HDistanceConstraint(p8, p1, 120)  # Was 80mm

print("\nRe-solving with new width...")
success = solve(points, constraints)

if success:
    print("\n✓ Parametric update succeeded!")
    print("\nNew coordinates:")
    for p in points:
        print(f"  {p}")
    print("\nOnly the width-dependent points moved — the constraint solver")
    print("automatically propagated the change through the design.")
