"""
Reolink Vehicle Line — Web backend (MJPEG + API).

Uses reolink-vehicle-line/config.json. Port 8001 to avoid clash with reolink-web (8000).
"""

import os
import sys
import threading
from datetime import datetime
from pathlib import Path

import cv2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from config_loader import get_config

_APP_DIR = Path(__file__).resolve().parent
_PROJECT_LINE = _APP_DIR.parent.parent / "reolink-vehicle-line"
sys.path.insert(0, str(_PROJECT_LINE))

from detector import VehicleDetector  # noqa: E402
from line_counter import VehicleLineCounter  # noqa: E402

OUTPUT_DIR = Path("C:/webcam_recordings")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Reolink Vehicle Line API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_state = {
    "recording": False,
    "detection_enabled": True,
    "writer": None,
    "output_path": None,
    "frame": None,
    "frame_lock": threading.Lock(),
    "width": 1920,
    "height": 1080,
    "vehicle_count": 0,
    "line_y_ratio": 0.6,
    "pending_counter_reset": False,
}


def build_rtsp_url(ip: str, user: str, password: str, channel: int = 1, stream: str = "main") -> str:
    return f"rtsp://{user}:{password}@{ip}:554/h264Preview_{channel:02d}_{stream}"


def draw_detections(frame, results):
    if results is None or results.boxes is None:
        return
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        tid = f" id{int(box.id[0])}" if box.id is not None else ""
        label = f"{results.names[cls_id]}{tid} {conf:.1f}"
        color = (0, 255, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x1, y1 - th - 4), (x1 + tw, y1), color, -1)
        cv2.putText(frame, label, (x1, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)


def draw_virtual_line(frame, line_y: int, width: int) -> None:
    cv2.line(frame, (0, line_y), (width, line_y), (0, 255, 255), 2)
    cv2.putText(
        frame, "VEHICLE COUNT LINE",
        (10, line_y - 8),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1,
    )


def capture_loop():
    try:
        cfg = get_config()
    except FileNotFoundError:
        return

    if not cfg.get("ip") or not cfg.get("password"):
        return

    ratio = cfg["line_y_ratio"]
    _state["line_y_ratio"] = ratio

    rtsp_url = build_rtsp_url(
        cfg["ip"], cfg["user"], cfg["password"], cfg["channel"], cfg["stream"]
    )
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        return

    detector = VehicleDetector(
        model_size=cfg["model_size"],
        confidence=cfg["confidence"],
    )
    counter = VehicleLineCounter(line_y=100.0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]
        _state["width"] = w
        _state["height"] = h
        line_y = int(h * ratio)
        counter.set_line_y(float(line_y))

        if _state.get("pending_counter_reset"):
            counter.reset()
            _state["pending_counter_reset"] = False
            _state["vehicle_count"] = 0

        display = frame.copy()
        if _state["detection_enabled"]:
            results = detector.detect(frame, track=True)
            counter.update_from_yolo_results(results)
            _state["vehicle_count"] = counter.count
            draw_detections(display, results)
        else:
            _state["vehicle_count"] = counter.count

        draw_virtual_line(display, line_y, w)

        if _state["recording"] and _state["writer"] is not None:
            _state["writer"].write(display)

        rec_col = (0, 0, 255) if _state["recording"] else (0, 255, 0)
        cv2.putText(
            display, "RECORDING" if _state["recording"] else "Idle",
            (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 1, rec_col, 2,
        )
        cv2.putText(
            display,
            f"Detection: {'ON' if _state['detection_enabled'] else 'OFF'}",
            (10, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1,
        )
        cv2.putText(
            display, f"Crossed line: {_state['vehicle_count']}",
            (10, 88), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2,
        )

        with _state["frame_lock"]:
            _, jpeg = cv2.imencode(".jpg", display)
            _state["frame"] = jpeg.tobytes()

    cap.release()
    if _state["writer"] is not None:
        _state["writer"].release()
        _state["writer"] = None


@app.on_event("startup")
async def startup():
    try:
        cfg = get_config()
        if cfg.get("ip") and cfg.get("password"):
            threading.Thread(target=capture_loop, daemon=True).start()
    except FileNotFoundError:
        pass


def generate_frames():
    import time
    while True:
        with _state["frame_lock"]:
            frame = _state.get("frame")
        if frame:
            yield (
                b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )
        time.sleep(0.033)


@app.get("/stream")
async def stream():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.get("/status")
async def status():
    return {
        "recording": _state["recording"],
        "detection_enabled": _state["detection_enabled"],
        "vehicle_count": _state["vehicle_count"],
        "line_y_ratio": _state["line_y_ratio"],
    }


@app.post("/record")
async def toggle_record():
    if _state["recording"]:
        _state["recording"] = False
        if _state["writer"] is not None:
            _state["writer"].release()
            _state["writer"] = None
        path = _state.get("output_path")
        _state["output_path"] = None
        return {"recording": False, "saved": str(path) if path else None}
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"reolink_vehicle_line_{ts}.mp4"
    w, h = _state.get("width", 1920), _state.get("height", 1080)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    _state["writer"] = cv2.VideoWriter(str(path), fourcc, 15.0, (w, h))
    _state["recording"] = True
    _state["output_path"] = path
    return {"recording": True, "path": str(path)}


@app.post("/detection")
async def toggle_detection():
    _state["detection_enabled"] = not _state["detection_enabled"]
    return {"detection_enabled": _state["detection_enabled"]}


@app.post("/reset-count")
async def reset_count():
    _state["pending_counter_reset"] = True
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
