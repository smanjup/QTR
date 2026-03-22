# Reolink Recorder with Object Detection

Reads from a Reolink camera via RTSP, detects objects in real time, and saves video to `C:\webcam_recordings\`.

## Setup

```bash
pip install -r requirements.txt
```

1. **Create config file**:
   ```bash
   copy config.example.json config.json
   ```
   Edit `config.json` with your camera IP, user, and password.

## Prerequisites

- Reolink camera on the same network
- RTSP enabled on the camera (Settings → Network → Advanced → Port Setup)

## Usage

```bash
python main.py
```

Settings are loaded from `config.json`. Command-line arguments override config values.

### Config file (config.json)

| Field | Description |
|-------|-------------|
| `ip` | Camera IP address |
| `user` | Camera username (default: admin) |
| `password` | Camera password |
| `channel` | NVR channel (1–8) |
| `stream` | `main` (HD) or `sub` (lower bandwidth) |

### Options (override config)

| Argument | Description |
|----------|-------------|
| `--ip` | Override camera IP |
| `--user` | Override username |
| `--password` | Override password |
| `--channel` | Override NVR channel |
| `--stream` | Override stream type |

### Example

```bash
# Using config.json (recommended)
python main.py

# Override IP from command line
python main.py --ip 192.168.1.101

# Password via environment variable (overrides config)
set REOLINK_PASSWORD=mypass
python main.py
```

### Controls

| Key | Action |
|-----|--------|
| **r** | Start or stop recording |
| **d** | Toggle object detection |
| **q** | Quit |

### Output

- Videos saved to `C:\webcam_recordings\reolink_YYYYMMDD_HHMMSS.mp4`
1. Start the backend
The backend must be running before you use the web app:

cd "c:\QTR AI Application\reolink-web\backend"
pip install -r requirements.txt
python server.py
You should see something like:

INFO:     Uvicorn running on http://0.0.0.0:8000
2. If it still fails, check for startup errors
If the backend crashes on startup, the React app will show that error. Common causes:

Cause	What to do
Missing config.json	Copy config.example.json to config.json in reolink-recorder-detection and fill in IP/password
Missing packages	Run pip install -r requirements.txt in reolink-web\backend
Port 8000 in use	Stop other apps using 8000, or change the port in server.py
Python/import errors	Check the terminal output when you run python server.py
3. Run both processes
You need two terminals:

Terminal 1 – backend:

cd "c:\QTR AI Application\reolink-web\backend"
python server.py
Terminal 2 – frontend:

cd "c:\QTR AI Application\reolink-web\frontend"
npm run dev
Then open http://localhost:5173 in your browser.