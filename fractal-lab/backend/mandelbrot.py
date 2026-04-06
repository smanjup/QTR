"""Vectorized Mandelbrot escape-time for a rectangular view of the complex plane."""

from __future__ import annotations

import numpy as np


def mandelbrot_counts(
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
    width: int,
    height: int,
    max_iter: int,
) -> np.ndarray:
    """
    Return HxW array of escape iteration counts (0 .. max_iter inclusive).
    Points in the set get max_iter.
    """
    width = max(1, width)
    height = max(1, height)
    max_iter = max(1, min(max_iter, 50_000))

    x = np.linspace(xmin, xmax, width, dtype=np.float64)
    y = np.linspace(ymin, ymax, height, dtype=np.float64)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y

    Z = np.zeros_like(C, dtype=np.complex128)
    counts = np.zeros(C.shape, dtype=np.int32)
    mask = np.ones(C.shape, dtype=bool)

    for i in range(max_iter):
        Z[mask] = Z[mask] ** 2 + C[mask]
        escaped = np.abs(Z) > 2.0
        newly = escaped & mask
        counts[newly] = i + 1
        mask &= ~escaped

    # Interior (never escaped): still True in mask
    counts[mask] = max_iter
    return counts


def counts_to_rgb(counts: np.ndarray, max_iter: int) -> np.ndarray:
    """Map iteration counts to RGB uint8 image (H, W, 3)."""
    max_iter = max(1, max_iter)
    hue = (np.log1p(counts) / np.log1p(max_iter)) % 1.0
    s = 0.85
    v = np.where(counts >= max_iter, 0.0, 0.95)

    h6 = hue * 6.0
    i = np.floor(h6).astype(np.int32)
    f = h6 - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t2 = v * (1.0 - s * (1.0 - f))

    r = np.zeros_like(hue)
    g = np.zeros_like(hue)
    b = np.zeros_like(hue)

    m0 = i % 6 == 0
    r[m0], g[m0], b[m0] = v[m0], t2[m0], p[m0]
    m1 = i % 6 == 1
    r[m1], g[m1], b[m1] = q[m1], v[m1], p[m1]
    m2 = i % 6 == 2
    r[m2], g[m2], b[m2] = p[m2], v[m2], t2[m2]
    m3 = i % 6 == 3
    r[m3], g[m3], b[m3] = p[m3], q[m3], v[m3]
    m4 = i % 6 == 4
    r[m4], g[m4], b[m4] = t2[m4], p[m4], v[m4]
    m5 = i % 6 == 5
    r[m5], g[m5], b[m5] = v[m5], p[m5], q[m5]

    inside = counts >= max_iter
    r[inside], g[inside], b[inside] = 0.0, 0.0, 0.0

    rgb = np.stack([r, g, b], axis=-1)
    return (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
