# Fractal Lab

**React (Vite) + TypeScript** frontend and a **FastAPI** backend that renders the **Mandelbrot set**, **Julia sets**, **fractal tree**, **Tree with love**, and the **Barnsley fern** IFS (NumPy + Pillow). Routes include **`/`**, **`/julia`**, **`/tree`**, **`/treewithlove`**, **`/barnsley`**.

## Prerequisites

- Python 3.10+
- Node.js 18+

## Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

- `GET http://127.0.0.1:8002/api/health` — liveness
- `GET http://127.0.0.1:8002/api/fractal.png?xmin=...&xmax=...&ymin=...&ymax=...&width=800&height=600&max_iter=256` — Mandelbrot PNG
- `GET http://127.0.0.1:8002/api/julia.png?...&cx=...&cy=...` — Julia set PNG (same bounds/width/height/max_iter as above, plus **`cx`** / **`cy`** for the constant \(c = cx + i\,cy\))
- `GET http://127.0.0.1:8002/api/tree.png?width=800&height=600&depth=10&branch_angle=28&length_scale=0.72&trunk_frac=0.22&origin_x=0.5&origin_y=0.92` — recursive binary tree PNG
- `GET http://127.0.0.1:8002/api/treewithlove.png?width=800&height=600&length=100&angle=30&backward=200&min_length=9` — turtle-style “tree with love” (green forward / brown backward)
- `GET http://127.0.0.1:8002/api/barnsley.png?width=800&height=600&points=350000&skip=50&xmin=-2.2&xmax=2.7&ymin=0&ymax=10.1` — Barnsley fern (optional `seed` for reproducibility)

## Frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the URL shown (default **5175**). Vite proxies **`/api`** to **`http://127.0.0.1:8002`**.

## Production build

```bash
cd frontend
npm run build
```

Serve `frontend/dist` behind a host that reverse-proxies **`/api`** to the same FastAPI process (or deploy both on a platform that supports static + Python).

## Deploy on Vercel

This folder includes **`vercel.json`**, **`api/index.py`** (FastAPI ASGI entry), and a root **`requirements.txt`** for the Python serverless function.

1. In [Vercel](https://vercel.com), **Add New Project** and import the **`smanjup/QTR`** GitHub repo (or push these files and connect the repo you use).
2. Set **Root Directory** to **`fractal-lab`** (required when the repo contains more than this app).
3. Deploy with defaults; Vercel will run `npm ci` / `npm run build` in `frontend/`, serve `frontend/dist`, route **`/api/*`** to the Python function, and fall back to **`index.html`** for client-side routes (`/julia`, `/barnsley`, etc.).
4. Heavy renders (large Mandelbrot / many Barnsley points) can approach the **60s** function limit; reduce resolution or iterations if a request times out.
