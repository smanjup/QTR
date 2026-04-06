"""Recursive fractal tree — line segments drawn with Pillow."""

from __future__ import annotations

import math

from PIL import Image, ImageDraw

# Dark slate background, soft green branches (similar vibe to other fractal views)
BG = (15, 23, 42)
LEAF_TIP = (187, 247, 208)
TRUNK = (74, 222, 128)


def _lerp_color(t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    return (
        int(TRUNK[0] + (LEAF_TIP[0] - TRUNK[0]) * t),
        int(TRUNK[1] + (LEAF_TIP[1] - TRUNK[1]) * t),
        int(TRUNK[2] + (LEAF_TIP[2] - TRUNK[2]) * t),
    )


def _branch(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    angle: float,
    length: float,
    remaining: int,
    branch_angle: float,
    scale: float,
    max_depth: int,
) -> None:
    if remaining <= 0 or length < 0.35:
        return
    x2 = x + length * math.cos(angle)
    y2 = y + length * math.sin(angle)
    depth_index = max_depth - remaining
    t = depth_index / max(1, max_depth)
    color = _lerp_color(t)
    lw = max(1, min(10, remaining))
    draw.line([(x, y), (x2, y2)], fill=color, width=lw)
    _branch(draw, x2, y2, angle - branch_angle, length * scale, remaining - 1, branch_angle, scale, max_depth)
    _branch(draw, x2, y2, angle + branch_angle, length * scale, remaining - 1, branch_angle, scale, max_depth)


def render_tree_png(
    width: int,
    height: int,
    *,
    depth: int,
    branch_angle_deg: float,
    length_scale: float,
    trunk_frac: float,
    origin_x_frac: float,
    origin_y_frac: float,
) -> Image.Image:
    """Draw a binary fractal tree; trunk grows upward (negative y)."""
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)
    start_x = width * origin_x_frac
    start_y = height * origin_y_frac
    trunk_len = height * trunk_frac
    # Upward in screen coordinates
    start_angle = -math.pi / 2
    branch_rad = math.radians(branch_angle_deg)
    _branch(
        draw,
        start_x,
        start_y,
        start_angle,
        trunk_len,
        depth,
        branch_rad,
        length_scale,
        depth,
    )
    return img
