"""
Barnsley fern — iterated function system (classic four-map IFS).

Probabilities: 1%, 85%, 7%, 7%. Points are accumulated into a density grid and
colored with a green palette on a dark background.
"""

from __future__ import annotations

import numpy as np
from PIL import Image

# Background (slate) — matches other fractal-lab views
BG = np.array([15, 23, 42], dtype=np.uint8)


def _iterate_ifs(n: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Sequential IFS; start at origin."""
    x = np.empty(n, dtype=np.float64)
    y = np.empty(n, dtype=np.float64)
    x[0] = 0.0
    y[0] = 0.0
    for i in range(1, n):
        r = rng.random()
        xi = x[i - 1]
        yi = y[i - 1]
        if r < 0.01:
            x[i] = 0.0
            y[i] = 0.16 * yi
        elif r < 0.86:
            x[i] = 0.85 * xi + 0.04 * yi
            y[i] = -0.04 * xi + 0.85 * yi + 1.6
        elif r < 0.93:
            x[i] = 0.2 * xi - 0.26 * yi
            y[i] = 0.23 * xi + 0.22 * yi + 1.6
        else:
            x[i] = -0.15 * xi + 0.28 * yi
            y[i] = 0.26 * xi + 0.29 * yi + 0.44
    return x, y


def _density_to_rgb(counts: np.ndarray) -> np.ndarray:
    """Log-scaled green fern on dark background."""
    c = np.log1p(counts.astype(np.float64))
    vmax = float(c.max()) if c.size else 0.0
    if vmax <= 0:
        t = np.zeros_like(c)
    else:
        t = c / vmax
    t = np.clip(t, 0.0, 1.0)
    # Blend BG toward fern green
    r = (BG[0] * (1.0 - t) + 74.0 * t).astype(np.uint8)
    g = (BG[1] * (1.0 - t) + 222.0 * t).astype(np.uint8)
    b = (BG[2] * (1.0 - t) + 128.0 * t).astype(np.uint8)
    return np.stack([r, g, b], axis=-1)


def render_barnsley_fern_png(
    width: int,
    height: int,
    *,
    points: int,
    skip: int,
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
    seed: int | None,
) -> Image.Image:
    if xmin >= xmax or ymin >= ymax:
        raise ValueError("Invalid bounds")
    rng = np.random.default_rng(seed)
    total = max(points + skip, skip + 1)
    x, y = _iterate_ifs(total, rng)
    xu = x[skip:]
    yu = y[skip:]

    counts = np.zeros((height, width), dtype=np.int32)
    w = xmax - xmin
    h = ymax - ymin
    px = np.floor((xu - xmin) / w * width).astype(np.int64)
    py = np.floor((ymax - yu) / h * height).astype(np.int64)
    mask = (px >= 0) & (px < width) & (py >= 0) & (py < height)
    px = px[mask]
    py = py[mask]
    np.add.at(counts, (py, px), 1)

    rgb = _density_to_rgb(counts)
    return Image.fromarray(rgb, mode="RGB")
