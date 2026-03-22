# Reolink Vehicle Line Counter

Copy of the Reolink recorder focused on **vehicles only** (car, motorcycle, bus, truck) with a **virtual horizontal line**. Vehicles crossing **from above the line to below** increment the counter (YOLO tracking avoids double counts).

## Setup

```bash
pip install -r requirements.txt
copy config.example.json config.json
```

Edit `config.json` with camera IP, password, and optional:

| Field | Meaning |
|-------|---------|
| `line_y_ratio` | Line height as fraction of frame (0–1). `0.6` = 60% from top |
| `confidence` | YOLO confidence threshold |
| `model_size` | `n`, `s`, `m`, `l`, `x` |

## Run

```bash
python main.py
```

Override line: `python main.py --line-y 0.55`

## Keys

| Key | Action |
|-----|--------|
| `r` | Start/stop recording → `C:\webcam_recordings\reolink_vehicle_line_*.mp4` |
| `d` | Toggle detection |
| `c` | Reset crossing count |
| `q` | Quit |

## Web UI

See **`reolink-vehicle-line-web`** (same logic in browser; backend port **8001**).
