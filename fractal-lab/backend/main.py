"""Fractal Lab API — PNG Mandelbrot, Julia, trees, Barnsley fern, etc."""

from __future__ import annotations

import io

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from PIL import Image

from julia import julia_counts
from mandelbrot import counts_to_rgb, mandelbrot_counts
from tree_fractal import render_tree_png
from barnsley_fern import render_barnsley_fern_png
from treewithlove import render_treewithlove_png

app = FastAPI(title="Fractal Lab API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/fractal.png")
def fractal_png(
    xmin: float = Query(-2.2, description="Left bound (real)"),
    xmax: float = Query(0.8, description="Right bound (real)"),
    ymin: float = Query(-1.15, description="Bottom bound (imag)"),
    ymax: float = Query(1.15, description="Top bound (imag)"),
    width: int = Query(800, ge=64, le=2048, description="Image width in pixels"),
    height: int = Query(600, ge=64, le=2048, description="Image height in pixels"),
    max_iter: int = Query(256, ge=16, le=5000, description="Maximum iterations"),
) -> Response:
    if xmin >= xmax or ymin >= ymax:
        raise HTTPException(status_code=400, detail="Invalid bounds: need xmin < xmax and ymin < ymax.")

    counts = mandelbrot_counts(xmin, xmax, ymin, ymax, width, height, max_iter)
    rgb = counts_to_rgb(counts, max_iter)
    img = Image.fromarray(rgb, mode="RGB")

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")


@app.get("/api/julia.png")
def julia_png(
    xmin: float = Query(-2.0, description="Left bound (real)"),
    xmax: float = Query(2.0, description="Right bound (real)"),
    ymin: float = Query(-2.0, description="Bottom bound (imag)"),
    ymax: float = Query(2.0, description="Top bound (imag)"),
    cx: float = Query(-0.8, description="Julia constant — real part"),
    cy: float = Query(0.156, description="Julia constant — imaginary part"),
    width: int = Query(800, ge=64, le=2048, description="Image width in pixels"),
    height: int = Query(600, ge=64, le=2048, description="Image height in pixels"),
    max_iter: int = Query(256, ge=16, le=5000, description="Maximum iterations"),
) -> Response:
    if xmin >= xmax or ymin >= ymax:
        raise HTTPException(status_code=400, detail="Invalid bounds: need xmin < xmax and ymin < ymax.")

    counts = julia_counts(xmin, xmax, ymin, ymax, width, height, max_iter, cx, cy)
    rgb = counts_to_rgb(counts, max_iter)
    img = Image.fromarray(rgb, mode="RGB")

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")


@app.get("/api/tree.png")
def tree_png(
    width: int = Query(800, ge=64, le=2048, description="Image width in pixels"),
    height: int = Query(600, ge=64, le=2048, description="Image height in pixels"),
    depth: int = Query(10, ge=1, le=16, description="Recursion depth (branch levels)"),
    branch_angle: float = Query(
        28.0,
        ge=5.0,
        le=85.0,
        description="Angle (degrees) between trunk and each child branch",
    ),
    length_scale: float = Query(
        0.72,
        ge=0.35,
        le=0.92,
        description="Length of child branches relative to parent",
    ),
    trunk_frac: float = Query(
        0.22,
        ge=0.05,
        le=0.45,
        description="Initial trunk length as a fraction of image height",
    ),
    origin_x: float = Query(0.5, ge=0.05, le=0.95, description="Trunk base x as fraction of width"),
    origin_y: float = Query(0.92, ge=0.5, le=0.99, description="Trunk base y as fraction of height"),
) -> Response:
    img = render_tree_png(
        width,
        height,
        depth=depth,
        branch_angle_deg=branch_angle,
        length_scale=length_scale,
        trunk_frac=trunk_frac,
        origin_x_frac=origin_x,
        origin_y_frac=origin_y,
    )
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")


@app.get("/api/treewithlove.png")
def treewithlove_png(
    width: int = Query(800, ge=64, le=2048, description="Image width in pixels"),
    height: int = Query(600, ge=64, le=2048, description="Image height in pixels"),
    length: float = Query(100.0, ge=10.0, le=300.0, description="Initial branch length (turtle units)"),
    angle: float = Query(30.0, ge=5.0, le=80.0, description="Branch angle in degrees"),
    backward: float = Query(200.0, ge=0.0, le=400.0, description="Turtle backward() before tree (positions the root)"),
    min_length: float = Query(9.0, ge=2.0, le=50.0, description="Recursion stops when branch length is below this"),
) -> Response:
    img = render_treewithlove_png(
        width,
        height,
        length=length,
        angle=angle,
        backward=backward,
        min_length=min_length,
    )
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")


@app.get("/api/barnsley.png")
def barnsley_png(
    width: int = Query(800, ge=64, le=2048, description="Image width in pixels"),
    height: int = Query(600, ge=64, le=2048, description="Image height in pixels"),
    points: int = Query(350_000, ge=10_000, le=2_000_000, description="IFS points after burn-in"),
    skip: int = Query(50, ge=0, le=50_000, description="Initial iterations discarded"),
    xmin: float = Query(-2.2, description="View left (real)"),
    xmax: float = Query(2.7, description="View right (real)"),
    ymin: float = Query(0.0, description="View bottom"),
    ymax: float = Query(10.1, description="View top"),
    seed: int | None = Query(None, description="Optional RNG seed for reproducible renders"),
) -> Response:
    if xmin >= xmax or ymin >= ymax:
        raise HTTPException(status_code=400, detail="Invalid bounds: need xmin < xmax and ymin < ymax.")

    img = render_barnsley_fern_png(
        width,
        height,
        points=points,
        skip=skip,
        xmin=xmin,
        xmax=xmax,
        ymin=ymin,
        ymax=ymax,
        seed=seed,
    )
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")
