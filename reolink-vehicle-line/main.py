"""
Reolink Recorder — Vehicles + virtual count line

Reads RTSP from Reolink, detects vehicles only, draws a horizontal virtual line,
and counts vehicles crossing top → bottom across the line.
Press 'r' record, 'd' detection, 'c' reset count, 'q' quit.
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from config import get_config
from detector import VehicleDetector
from line_counter import VehicleLineCounter

OUTPUT_DIR = Path("C:/webcam_recordings")


def build_rtsp_url(ip: str, user: str, password: str, channel: int = 1, stream: str = "main") -> str:
    return f"rtsp://{user}:{password}@{ip}:554/h264Preview_{channel:02d}_{stream}"


def draw_detections(frame: np.ndarray, results) -> None:
    if results is None or results.boxes is None:
        return
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        tid = ""
        if box.id is not None:
            tid = f" id{int(box.id[0])}"
        label = f"{results.names[cls_id]}{tid} {conf:.1f}"
        color = (0, 255, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x1, y1 - th - 4), (x1 + tw, y1), color, -1)
        cv2.putText(
            frame, label, (x1, y1 - 2),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1,
        )


def draw_virtual_line(frame: np.ndarray, line_y: int, width: int) -> None:
    """Draw horizontal virtual count line."""
    cv2.line(frame, (0, line_y), (width, line_y), (0, 255, 255), 2)
    cv2.putText(
        frame, "VEHICLE COUNT LINE (crossing down counts)", (10, line_y - 8),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reolink vehicle detection with virtual count line"
    )
    parser.add_argument("--ip", type=str, default=None)
    parser.add_argument("--user", type=str, default=None)
    parser.add_argument("--password", type=str, default=None)
    parser.add_argument("--channel", type=int, default=None)
    parser.add_argument("--stream", type=str, choices=["main", "sub"], default=None)
    parser.add_argument(
        "--line-y",
        type=float,
        default=None,
        help="Virtual line position 0.0–1.0 (overrides config line_y_ratio)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = get_config(
        ip=args.ip,
        user=args.user,
        password=args.password,
        channel=args.channel,
        stream=args.stream,
        line_y_ratio=args.line_y,
    )

    if not cfg["ip"]:
        print("Error: IP required. Set in config.json or use --ip.")
        sys.exit(1)
    if not cfg["password"]:
        print("Error: Password required in config.json, --password, or REOLINK_PASSWORD.")
        sys.exit(1)

    ratio = cfg["line_y_ratio"]
    if not 0.0 <= ratio <= 1.0:
        print("Error: line_y_ratio must be between 0 and 1.")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rtsp_url = build_rtsp_url(
        cfg["ip"], cfg["user"], cfg["password"], cfg["channel"], cfg["stream"]
    )
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        print("Error: Could not connect to Reolink camera.")
        sys.exit(1)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 15.0
    line_y = int(height * ratio)
    counter = VehicleLineCounter(line_y=float(line_y))

    detector = VehicleDetector(
        model_size=cfg["model_size"],
        confidence=cfg["confidence"],
    )
    detection_enabled = True
    writer: cv2.VideoWriter | None = None
    recording = False
    output_path: Path | None = None

    print("Reolink Vehicle Line Counter")
    print("=" * 45)
    print(f"Camera: {cfg['ip']} ({cfg['stream']} stream, ch {cfg['channel']})")
    print(f"Virtual line: {ratio * 100:.0f}% from top (y={line_y}px)")
    print(f"Output: {OUTPUT_DIR}")
    print("'r' record | 'd' detection | 'c' reset count | 'q' quit")
    print("=" * 45)

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        display = frame.copy()
        # Recalculate line if resolution changes
        h, w = display.shape[:2]
        line_y = int(h * ratio)
        counter.set_line_y(float(line_y))

        results = None
        if detection_enabled:
            results = detector.detect(frame, track=True)
            cross = counter.update_from_yolo_results(results)
            if cross:
                print(f"+{cross} vehicle(s) crossed line — total: {counter.count}")
            draw_detections(display, results)
            frame_count += 1
            if frame_count % 60 == 0 and results.boxes is not None:
                n = len(results.boxes)
                if n:
                    print(f"Vehicles in frame: {n} | line crossings: {counter.count}")

        draw_virtual_line(display, line_y, w)

        if recording and writer is not None:
            writer.write(display)

        y_off = 30
        rec_col = (0, 0, 255) if recording else (0, 255, 0)
        cv2.putText(display, "RECORDING" if recording else "Idle", (10, y_off), cv2.FONT_HERSHEY_SIMPLEX, 1, rec_col, 2)
        cv2.putText(
            display, f"Detection: {'ON' if detection_enabled else 'OFF'}", (10, y_off + 35),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1,
        )
        cv2.putText(
            display, f"Vehicles crossed line: {counter.count}", (10, y_off + 65),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2,
        )
        cv2.putText(
            display, "r record  d detect  c reset  q quit", (10, h - 12),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1,
        )

        cv2.imshow("Reolink Vehicle Line Counter", display)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("d"):
            detection_enabled = not detection_enabled
            print(f"Detection: {'ON' if detection_enabled else 'OFF'}")
        if key == ord("c"):
            counter.reset()
            print("Line crossing count reset.")
        if key == ord("r"):
            if recording:
                recording = False
                if writer:
                    writer.release()
                    writer = None
                if output_path:
                    print(f"Saved: {output_path}")
            else:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = OUTPUT_DIR / f"reolink_vehicle_line_{ts}.mp4"
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                writer = cv2.VideoWriter(str(output_path), fourcc, fps, (w, h))
                recording = True
                print(f"Recording: {output_path}")

    cap.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()
    print(f"Done. Total line crossings: {counter.count}")


if __name__ == "__main__":
    main()
