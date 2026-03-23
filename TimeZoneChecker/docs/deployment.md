# TimeZoneChecker — deployment

This app ships as a **static React (Vite) frontend** plus a **FastAPI** API. For [Vercel](https://vercel.com/), both are deployed from this folder using `vercel.json`: the UI is built to `frontend/dist`, and `/api/*` is handled by a Python serverless function that imports the same `backend/main.py` app.

## What gets deployed

| Piece | Role |
|--------|------|
| `frontend/` | `npm ci` + `npm run build` → static assets in `frontend/dist` |
| `api/index.py` | ASGI entry: `from main import app` (FastAPI in `backend/main.py`) |
| `requirements.txt` | Python deps at the **TimeZoneChecker** root (for Vercel’s `api/` runtime) |
| `vercel.json` | Build commands, output directory, `/api/*` → `/api/index`, function timeout |

The browser calls **`/api/convert`** (and `/api/health`, etc.) on the **same origin** as the page, so no CORS or public API URL is required for the default setup.

## Prerequisites

- A [Vercel](https://vercel.com/) account  
- [Node.js](https://nodejs.org/) 18+ (for local builds; Vercel uses its own build image)  
- [Git](https://git-scm.com/) if you deploy from a repository  

## Deploy on Vercel (recommended)

### 1. Repository layout

If this project lives inside a larger monorepo, set Vercel’s **Root Directory** to the folder that contains `vercel.json` (the **TimeZoneChecker** directory), not the monorepo root.

### 2. Import the project

1. In Vercel: **Add New…** → **Project** → import your Git repository.  
2. **Root Directory:** `TimeZoneChecker` (or your equivalent path).  
3. **Framework Preset:** Other / leave defaults; build settings are taken from `vercel.json`.  
4. **Environment variables:** none are required for the stock app.  
5. Deploy.

### 3. CLI (alternative)

From the **TimeZoneChecker** directory (where `vercel.json` lives):

```bash
npm i -g vercel   # optional; or use: npx vercel@latest
vercel login
vercel --prod
```

The first run may ask for a project name. Use a **lowercase** slug (e.g. `timezone-checker`); Vercel rejects invalid characters in project names.

After linking, Vercel creates a `.vercel/` directory (usually gitignored). Do **not** commit secrets or tokens.

### 4. Smoke test

- Open the production URL (and any production alias).  
- `GET /api/health` should return JSON like `{"status":"ok"}`.  
- Use the UI: pick cities and confirm the results table loads (exercises `POST /api/convert`).

## Configuration reference (`vercel.json`)

- **`buildCommand` / `installCommand`:** run inside `frontend/` with `npm ci`.  
- **`outputDirectory`:** `frontend/dist` (Vite build output).  
- **`rewrites`:** all `/api/*` traffic goes to the Python function at `api/index.py` (destination `/api/index`).  
- **`functions.api/index.py.maxDuration`:** serverless timeout (seconds); increase if cold starts or slow responses are an issue.

## Python runtime

Vercel installs dependencies from **`requirements.txt`** at the **TimeZoneChecker** root (not only `backend/requirements.txt`). Keep those files aligned when you bump FastAPI or add packages used by `backend/main.py`.

The serverless entry **`api/index.py`** must export the ASGI app as **`app`** (the FastAPI instance from `backend/main.py`).

## Custom domains

In the Vercel project: **Settings** → **Domains** → add your domain and follow DNS instructions. No app code changes are required for same-origin `/api` routes.

## Troubleshooting

| Symptom | What to check |
|---------|----------------|
| Build fails on `npm ci` | Run `npm ci` locally in `frontend/`; commit an up-to-date `package-lock.json`. |
| `/api/*` 404 | Root directory must include `api/index.py` and `vercel.json` rewrites. |
| `/api/*` 500 | Vercel **Functions** logs; confirm `requirements.txt` matches `backend` needs and `api/index.py` imports `app` correctly. |
| UI loads but “Cannot reach the API” | Usually a failed `fetch` to `/api/convert` — check function logs and that the deployment finished successfully. |

## Other hosting options

- **Static + separate API:** build `frontend` with `npm run build`, host `dist/` on any static host, and run FastAPI with `uvicorn` (or similar) behind a reverse proxy that maps `/api` to the API process. The client uses relative URLs (`/api`), so the static site and API must share the same origin **or** you must change the client to use an absolute API base URL.  
- **Docker:** not provided in-repo; you can containerize `backend` and serve `frontend/dist` with nginx (or a single image with both).

For local development and generic production notes, see the [README](../README.md).
