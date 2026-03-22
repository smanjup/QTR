# Reolink Web

Web interface for the Reolink camera with object detection and recording.

Uses the same `config.json` as the desktop app (`reolink-recorder-detection/config.json`).

## Setup

1. **Create config** (if not done already):
   ```bash
   cd reolink-recorder-detection
   copy config.example.json config.json
   # Edit config.json with your camera IP and password
   ```

2. **Backend**:
   ```bash
   cd reolink-web/backend
   pip install -r requirements.txt
   python server.py
   ```
   Backend runs on http://localhost:8000

3. **Frontend**:
   ```bash
   cd reolink-web/frontend
   npm install
   npm run dev
   ```
   Frontend runs on http://localhost:5173

## Usage

- Open http://localhost:5173 in your browser
- View the live stream
- **Start Recording** / **Stop Recording** – saves to `C:\webcam_recordings\`
- **Detection: ON/OFF** – toggle object detection overlay

## Production

- Build frontend: `cd frontend && npm run build`
- Serve the `dist` folder with a static server
- Run backend: `python server.py` (or use uvicorn/gunicorn)
- For same-origin access, use a reverse proxy (e.g. nginx) to serve both from one domain
