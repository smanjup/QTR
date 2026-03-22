# TimeZoneChecker — “What time is the time there”

Three-step web app: choose a **reference city**, enter **local date & time**, add **other cities**, then see those moments as **local wall times** in each place (DST-aware), similar in spirit to [World Time Buddy](https://www.worldtimebuddy.com/).

- **Frontend:** React (Vite) — `frontend/`
- **Backend:** Python (FastAPI) — `backend/`
- **City search & IANA zones:** [Open-Meteo Geocoding API](https://open-meteo.com/en/docs/geocoding-api) (no API key for basic use)

## Prerequisites

- Python 3.10+
- Node.js 18+

## Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

API: `http://127.0.0.1:8001` — `GET /api/health`, `GET /api/cities/search?q=`, `POST /api/convert`.

## Frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the URL shown (default dev server uses port **5174**). Vite proxies `/api` to the backend on **8001**.

## Production build

```bash
cd frontend
npm run build
```

Serve `frontend/dist` with any static host; configure that host to reverse-proxy `/api` to your FastAPI service, or set a full API base URL in the client if you split origins.

## Repository

This project lives under the [QTR](https://github.com/smanjup/QTR) monorepo in `TimeZoneChecker/`.
