"""
Reolink Web Backend

Streams camera feed via MJPEG and provides control API.
Reads config from reolink-recorder-detection/config.json.
"""

import os
import threading
from datetime import datetime
from pathlib import Path

import cv2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from config_loader import get_config

# Import detector from parent reolink-recorder-detection
sys_path = Path(__file__).parent.parent.parent / "reolink-recorder-detection"
import sys
sys.path.insert(0, str(sys_path))
from detector import ObjectDetector

OUTPUT_DIR = Path("C:/webcam_recordings")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Reolink Web API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared state
_state = {
    "recording": False,
    "detection_enabled": True,
    "writer": None,
    "output_path": None,
    "frame": None,
    "frame_lock": threading.Lock(),
    "width": 1920,
    "height": 1080,
}


def build_rtsp_url(ip: str, user: str, password: str, channel: int = 1, stream: str = "main") -> str:
    return f"rtsp://{user}:{password}@{ip}:554/h264Preview_{channel:02d}_{stream}"


def draw_detections(frame, results):
    """Draw YOLO boxes on frame."""
    if results is None or results.boxes is None:
        return
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = f"{results.names[cls_id]} {conf:.1f}"
        color = (0, 255, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x1, y1 - th - 4), (x1 + tw, y1), color, -1)
        cv2.putText(frame, label, (x1, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)


def capture_loop():
    """Background thread: capture from RTSP, run detection, optionally record."""
    cfg = get_config()
    if not cfg.get("ip") or not cfg.get("password"):
        return
    rtsp_url = build_rtsp_url(
        cfg["ip"], cfg["user"], cfg["password"], cfg["channel"], cfg["stream"]
    )
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        return
    detector = ObjectDetector(model_size="n", confidence=0.5)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 15.0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        _state["width"] = frame.shape[1]
        _state["height"] = frame.shape[0]
        display = frame.copy()
        results = None
        if _state["detection_enabled"]:
            results = detector.detect(frame)
            draw_detections(display, results)
        if _state["recording"] and _state["writer"] is not None:
            _state["writer"].write(display)
        status = "RECORDING" if _state["recording"] else "Idle"
        color = (0, 0, 255) if _state["recording"] else (0, 255, 0)
        cv2.putText(display, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        det_status = "Detection: ON" if _state["detection_enabled"] else "Detection: OFF"
        cv2.putText(display, det_status, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        with _state["frame_lock"]:
            _, jpeg = cv2.imencode(".jpg", display)
            _state["frame"] = jpeg.tobytes()
    cap.release()
    if _state["writer"] is not None:
        _state["writer"].release()
        _state["writer"] = None


def generate_frames():
    """MJPEG generator for streaming."""
    import time
    while True:
        with _state["frame_lock"]:
            frame = _state.get("frame")
        if frame:
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
        time.sleep(0.033)  # ~30 fps


@app.on_event("startup")
async def startup():
    """Start capture thread."""
    try:
        cfg = get_config()
        if cfg.get("ip") and cfg.get("password"):
            t = threading.Thread(target=capture_loop, daemon=True)
            t.start()
    except FileNotFoundError:
        pass


@app.get("/stream")
async def stream():
    """MJPEG stream endpoint."""
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.get("/status")
async def status():
    """Get current recording and detection status."""
    return {
        "recording": _state["recording"],
        "detection_enabled": _state["detection_enabled"],
    }


@app.post("/record")
async def toggle_record():
    """Start or stop recording."""
    if _state["recording"]:
        _state["recording"] = False
        if _state["writer"] is not None:
            _state["writer"].release()
            _state["writer"] = None
        path = _state.get("output_path")
        _state["output_path"] = None
        return {"recording": False, "saved": str(path) if path else None}
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = OUTPUT_DIR / f"reolink_{timestamp}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        w, h = _state.get("width", 1920), _state.get("height", 1080)
        _state["writer"] = cv2.VideoWriter(str(path), fourcc, 15.0, (w, h))
        _state["recording"] = True
        _state["output_path"] = path
        return {"recording": True, "path": str(path)}


@app.post("/detection")
async def toggle_detection():
    """Toggle object detection on/off."""
    _state["detection_enabled"] = not _state["detection_enabled"]
    return {"detection_enabled": _state["detection_enabled"]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
