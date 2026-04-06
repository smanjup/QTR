# QTR

## Fractal Lab on Vercel

The repo includes **`vercel.json` at the root** so you can deploy **without** setting a subfolder as Root Directory:

1. [Vercel](https://vercel.com) → **Add New Project** → import **`smanjup/QTR`**.
2. Leave **Root Directory** as **`.`** (repository root).
3. **Deploy** — build runs in `fractal-lab/frontend`, `/api/*` uses `api/index.py` → `fractal-lab/backend`.

Alternatively, set **Root Directory** to **`fractal-lab`** and use the copy of the config inside that folder (same behavior).