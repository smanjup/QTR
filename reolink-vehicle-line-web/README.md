# Reolink Vehicle Line — Web UI

Browser interface for **[reolink-vehicle-line](../reolink-vehicle-line/)**: vehicles only, virtual count line, MJPEG stream.

## Prerequisite

1. Create **`reolink-vehicle-line/config.json`** from `config.example.json` (camera IP, password).
2. This folder’s backend uses that same config.

## Run

**Terminal 1 — backend (port 8001):**

```bash
cd reolink-vehicle-line-web\backend
pip install -r requirements.txt
python server.py
```

**Terminal 2 — frontend:**

```bash
cd reolink-vehicle-line-web\frontend
npm install
npm run dev
```

Open **http://localhost:5173** (Vite may pick another port; check the terminal).

## API

| Method | Path | Action |
|--------|------|--------|
| GET | `/stream` | MJPEG |
| GET | `/status` | recording, detection, vehicle_count, line_y_ratio |
| POST | `/record` | Toggle recording |
| POST | `/detection` | Toggle detection |
| POST | `/reset-count` | Reset line crossing count |

Original all-objects app is unchanged: `reolink-recorder-detection` + `reolink-web` (port 8000).
