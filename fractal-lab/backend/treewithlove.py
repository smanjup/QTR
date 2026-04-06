"""
Tree with love — same recursion as the user's turtle script, rendered to PNG.

Original turtle logic (ported; no turtle runtime on the server):
  left(90); backward(200); tree(100, 30)
  tree: if length < 9: return; else green forward; right; tree(0.8*L); left(2a); tree(0.8*L); right; brown backward
"""

from __future__ import annotations

import math

from PIL import Image, ImageDraw

# Match typical turtle colors
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
BG = (255, 250, 240)


def _turtle_to_pil(
    tx: float,
    ty: float,
    width: int,
    height: int,
    margin: float,
    scale: float,
    root_ty: float,
) -> tuple[float, float]:
    """Turtle coords: x right, y up. Root at (0, root_ty). PIL y increases down."""
    px = width / 2 + tx * scale
    py = (height - margin) - (ty - root_ty) * scale
    return px, py


def _draw_seg(
    draw: ImageDraw.ImageDraw,
    t1: tuple[float, float],
    t2: tuple[float, float],
    color: tuple[int, int, int],
    width: int,
    height: int,
    margin: float,
    scale: float,
    root_ty: float,
    line_width: int,
) -> None:
    p1 = _turtle_to_pil(t1[0], t1[1], width, height, margin, scale, root_ty)
    p2 = _turtle_to_pil(t2[0], t2[1], width, height, margin, scale, root_ty)
    draw.line([p1, p2], fill=color, width=max(1, line_width))


def _tree(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    heading_deg: float,
    length: float,
    angle: float,
    min_length: float,
    width: int,
    height: int,
    margin: float,
    scale: float,
    root_ty: float,
    line_width: int,
) -> None:
    """heading_deg: 0 = east, 90 = north (turtle convention, CCW)."""
    if length < min_length:
        return
    h_rad = math.radians(heading_deg)
    x2 = x + length * math.cos(h_rad)
    y2 = y + length * math.sin(h_rad)
    _draw_seg(draw, (x, y), (x2, y2), GREEN, width, height, margin, scale, root_ty, line_width)

    h1 = heading_deg - angle
    lw = max(1, line_width - 1)
    _tree(draw, x2, y2, h1, length * 0.8, angle, min_length, width, height, margin, scale, root_ty, lw)
    h2 = h1 + 2 * angle
    _tree(draw, x2, y2, h2, length * 0.8, angle, min_length, width, height, margin, scale, root_ty, lw)

    _draw_seg(draw, (x2, y2), (x, y), BROWN, width, height, margin, scale, root_ty, line_width)


def render_treewithlove_png(
    width: int,
    height: int,
    *,
    length: float,
    angle: float,
    backward: float,
    min_length: float,
) -> Image.Image:
    """
    Replicate draw_fractal(): face north, move backward `backward`, then tree(length, angle).
    Root y in turtle space is -backward (same as turtle after backward(200) from origin).
    """
    margin = 36.0
    # Fit typical drawing (~400 logical span) into the canvas
    scale = min(width, height) / 480.0

    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    root_ty = -backward
    # Start at (0, root_ty), heading 90° (north), matching turtle after left(90) and backward(backward)
    tx, ty = 0.0, root_ty
    heading = 90.0
    lw = max(2, int(length / 18))

    _tree(draw, tx, ty, heading, length, angle, min_length, width, height, margin, scale, root_ty, lw)
    return img
