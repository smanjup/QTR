"""
TimeZoneChecker API — city search (Open-Meteo geocoding) and timezone conversion.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

OPEN_METEO_GEO = "https://geocoding-api.open-meteo.com/v1/search"


def _zoneinfo(name: str) -> ZoneInfo:
    """Load IANA zone; needs the ``tzdata`` package on Windows and many CI images."""
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        raise HTTPException(status_code=400, detail=f"Unknown timezone: {name}") from None
    except OSError as e:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Could not load timezone data for {name!r}. "
                "Install IANA data: pip install tzdata"
            ),
        ) from e

app = FastAPI(title="TimeZoneChecker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CityHit(BaseModel):
    id: int | None = None
    name: str
    country: str | None = None
    admin1: str | None = Field(None, description="State/region")
    latitude: float
    longitude: float
    timezone: str
    label: str


class ConvertRequest(BaseModel):
    """Interpret local_datetime as wall time in from_timezone (IANA)."""

    from_timezone: str
    local_datetime: str = Field(
        ...,
        description="ISO-like string without offset, e.g. 2026-03-22T16:00 or 2026-03-22T16:00:00",
    )
    to_timezones: list[str] = Field(..., min_length=1)


class ConvertedRow(BaseModel):
    timezone: str
    local_datetime: str
    offset_label: str


class ConvertResponse(BaseModel):
    utc_iso: str
    reference_local: str
    results: list[ConvertedRow]


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/cities/search", response_model=dict[str, Any])
async def search_cities(
    q: str = Query(..., min_length=1),
    count: int = Query(10, ge=1, le=25),
) -> dict[str, Any]:
    q = q.strip()
    if len(q) < 2:
        return {"results": []}

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            OPEN_METEO_GEO,
            params={"name": q, "count": count, "language": "en"},
        )
        r.raise_for_status()
        data = r.json()

    raw = data.get("results") or []
    results: list[CityHit] = []
    for item in raw:
        tz = item.get("timezone")
        if not tz:
            continue
        name = item.get("name") or ""
        country = item.get("country")
        admin1 = item.get("admin1")
        lat = item.get("latitude")
        lon = item.get("longitude")
        if lat is None or lon is None:
            continue
        parts = [name]
        if admin1:
            parts.append(admin1)
        if country:
            parts.append(country)
        label = ", ".join(parts)
        results.append(
            CityHit(
                id=item.get("id"),
                name=name,
                country=country,
                admin1=admin1,
                latitude=float(lat),
                longitude=float(lon),
                timezone=tz,
                label=label,
            )
        )

    return {"results": [r.model_dump() for r in results]}


def _parse_local_in_zone(local_str: str, tz_name: str) -> datetime:
    z = _zoneinfo(tz_name)

    s = local_str.strip().replace("Z", "")
    if "T" not in s:
        raise HTTPException(
            status_code=400,
            detail="local_datetime must include date and time, e.g. 2026-03-22T16:00",
        )

    date_part, _, time_part = s.partition("T")
    try:
        y, m, d = (int(x) for x in date_part.split("-"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date in local_datetime") from e

    time_bits = time_part.split(":")
    try:
        hh = int(time_bits[0])
        mm = int(time_bits[1]) if len(time_bits) > 1 else 0
        ss = int(time_bits[2]) if len(time_bits) > 2 else 0
    except (ValueError, IndexError) as e:
        raise HTTPException(status_code=400, detail="Invalid time in local_datetime") from e

    try:
        return datetime(y, m, d, hh, mm, ss, tzinfo=z)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid local clock time for {tz_name}: {local_str}",
        ) from e


def _format_offset(dt: datetime) -> str:
    off = dt.utcoffset()
    if off is None:
        return ""
    total = int(off.total_seconds())
    sign = "+" if total >= 0 else "-"
    total = abs(total)
    h, rem = divmod(total, 3600)
    m, _ = divmod(rem, 60)
    return f"UTC{sign}{h:02d}:{m:02d}"




@app.post("/api/convert", response_model=ConvertResponse)
def convert_time(req: ConvertRequest) -> ConvertResponse:
    dt_ref = _parse_local_in_zone(req.local_datetime, req.from_timezone)
    utc = dt_ref.astimezone(_zoneinfo("UTC"))

    ref_label = dt_ref.strftime("%Y-%m-%d %H:%M:%S")
    rows: list[ConvertedRow] = []

    for tz_name in req.to_timezones:
        z = _zoneinfo(tz_name)
        local = dt_ref.astimezone(z)
        rows.append(
            ConvertedRow(
                timezone=tz_name,
                local_datetime=local.strftime("%Y-%m-%d %H:%M:%S"),
                offset_label=_format_offset(local),
            )
        )

    return ConvertResponse(
        utc_iso=utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        reference_local=f"{ref_label} ({req.from_timezone})",
        results=rows,
    )
