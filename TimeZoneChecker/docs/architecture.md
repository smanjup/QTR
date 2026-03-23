# TimeZoneChecker — system architecture

Overview of how the app is structured: **React (Vite) frontend**, **FastAPI backend**, and **dev-time proxy**. There is **no database**; city choices come from a **static list** in the frontend, and conversion uses **IANA timezones** via Python’s `zoneinfo` (with the **`tzdata`** package on Windows).

## High-level diagram

```mermaid
flowchart LR
  subgraph Browser["Browser (localhost:5174)"]
    UI["React app (Vite)"]
    DATA["majorCities.js\n(static IANA list)"]
    UI --> DATA
  end

  subgraph DevProxy["Vite dev server"]
    P["Proxy: /api → 127.0.0.1:8001"]
  end

  subgraph Backend["FastAPI (uvicorn :8001)"]
    API["/api/*"]
    Z["zoneinfo + tzdata\n(IANA zones)"]
    API --> Z
  end

  UI -->|"POST /api/convert\nJSON body"| P
  P --> API

  subgraph Optional["Optional / unused by current UI"]
    OM["Open-Meteo Geocoding API"]
  end

  API -.->|"GET /api/cities/search\n(httpx)"| OM
```

## Convert flow (main path)

```mermaid
sequenceDiagram
  participant U as User
  participant R as React (App.jsx)
  participant V as Vite proxy
  participant F as FastAPI
  participant TZ as zoneinfo/tzdata

  U->>R: Pick cities + date/time
  R->>R: Build local_datetime + IANA zones (from majorCities.js)
  R->>V: POST /api/convert
  V->>F: forward to :8001
  F->>TZ: Parse wall time in from_timezone, convert to UTC + target zones
  TZ-->>F: UTC instant + local rows
  F-->>R: JSON (utc_iso, reference_local, results)
  R-->>U: Table in compare & local times section
```

## Components

| Piece | Role |
|--------|------|
| **React + Vite** | UI; city pickers use **`frontend/src/data/majorCities.js`** only (no network for city lists). |
| **Vite `proxy`** | In dev, **`/api` → `http://127.0.0.1:8001`** (see `frontend/vite.config.js`) so the client can call `fetch('/api/convert')`. |
| **FastAPI** | **`POST /api/convert`** performs timezone math with IANA names via **`zoneinfo`** (install **`tzdata`** on Windows). |
| **`GET /api/cities/search`** | Proxies to **Open-Meteo**; the **current UI does not use it** after switching to the static major-cities list. |
| **`GET /api/health`** | Liveness check for the API process. |

## Production note

For a production build, serve `frontend/dist` behind a host that **reverse-proxies `/api`** to the FastAPI service, or configure a full API base URL in the client if origins differ.
