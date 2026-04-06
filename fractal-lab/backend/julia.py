"""Vectorized Julia set escape-time: z_{n+1} = z_n^2 + c with fixed c, z_0 = pixel."""

from __future__ import annotations

import numpy as np


def julia_counts(
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
    width: int,
    height: int,
    max_iter: int,
    cx: float,
    cy: float,
) -> np.ndarray:
    """
    Return HxW array of escape iteration counts.
    Points in the filled Julia set (never escaped) get max_iter.
    """
    width = max(1, width)
    height = max(1, height)
    max_iter = max(1, min(max_iter, 50_000))

    x = np.linspace(xmin, xmax, width, dtype=np.float64)
    y = np.linspace(ymin, ymax, height, dtype=np.float64)
    X, Y = np.meshgrid(x, y)
    c = complex(cx, cy)
    Z = X + 1j * Y

    counts = np.zeros(Z.shape, dtype=np.int32)
    mask = np.ones(Z.shape, dtype=bool)

    for i in range(max_iter):
        Z[mask] = Z[mask] ** 2 + c
        escaped = np.abs(Z) > 2.0
        newly = escaped & mask
        counts[newly] = i + 1
        mask &= ~escaped

    counts[mask] = max_iter
    return counts
