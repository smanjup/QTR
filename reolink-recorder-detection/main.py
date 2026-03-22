"""
Reolink Recorder with Object Detection

Reads from Reolink camera via RTSP, detects objects in real time, and saves video to the C drive.
Press 'r' to start/stop recording, 'd' to toggle detection, 'q' to quit.
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from config import get_config
from detector import ObjectDetector

OUTPUT_DIR = Path("C:/webcam_recordings")


def build_rtsp_url(ip: str, user: str, password: str, channel: int = 1, stream: str = "main") -> str:
    """Build Reolink RTSP URL."""
    return f"rtsp://{user}:{password}@{ip}:554/h264Preview_{channel:02d}_{stream}"


def draw_detections(frame: np.ndarray, results) -> None:
    """Draw bounding boxes and labels on frame from YOLO results."""
    if results.boxes is None:
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
        cv2.putText(
            frame, label, (x1, y1 - 2),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reolink camera recorder with object detection"
    )
    parser.add_argument(
        "--ip",
        type=str,
        default=None,
        help="Camera IP (overrides config.json)",
    )
    parser.add_argument(
        "--user",
        type=str,
        default=None,
        help="Camera username (overrides config.json)",
    )
    parser.add_argument(
        "--password",
        type=str,
        default=None,
        help="Camera password (overrides config.json and REOLINK_PASSWORD)",
    )
    parser.add_argument(
        "--channel",
        type=int,
        default=None,
        help="Camera channel (overrides config.json)",
    )
    parser.add_argument(
        "--stream",
        type=str,
        choices=["main", "sub"],
        default=None,
        help="Stream type: main or sub (overrides config.json)",
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
    )

    # Check if IP address is provided in configuration; if not, exit with error
    if not cfg["ip"]:
        print("Error: IP required. Set in config.json or use --ip.")
        sys.exit(1)
    # Check if password is provided; if not, exit with error
    if not cfg["password"]:
        print("Error: Password required. Set in config.json, use --password, or REOLINK_PASSWORD env var.")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rtsp_url = build_rtsp_url(
        cfg["ip"], cfg["user"], cfg["password"], cfg["channel"], cfg["stream"]
    )
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        print("Error: Could not connect to Reolink camera. Check IP, credentials, and network.")
        sys.exit(1)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 15.0

    detector = ObjectDetector(model_size="n", confidence=0.5)
    detection_enabled = True

    writer: cv2.VideoWriter | None = None
    recording = False
    output_path: Path | None = None

    print("Reolink Recorder with Object Detection")
    print("=" * 45)
    print(f"Camera: {cfg['ip']} (channel {cfg['channel']}, {cfg['stream']} stream)")
    print(f"Output folder: {OUTPUT_DIR}")
    print("Press 'r' to start/stop recording")
    print("Press 'd' to toggle object detection")
    print("Press 'q' to quit")
    print("=" * 45)

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        display_frame = frame.copy()
        results = None

        if detection_enabled:
            results = detector.detect(frame)
            draw_detections(display_frame, results)
            frame_count += 1
            if frame_count % 30 == 0 and results.boxes is not None:
                names = [results.names[int(box.cls[0])] for box in results.boxes]
                print(f"Detected: {', '.join(names)}")

        if recording and writer is not None:
            writer.write(display_frame)

        status = "RECORDING" if recording else "Idle"
        color = (0, 0, 255) if recording else (0, 255, 0)
        cv2.putText(
            display_frame, status, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2,
        )
        det_status = "Detection: ON" if detection_enabled else "Detection: OFF"
        cv2.putText(
            display_frame, det_status, (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1,
        )
        cv2.putText(
            display_frame, "r=record  d=detect  q=quit", (10, height - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1,
        )

        cv2.imshow("Reolink Recorder + Detection", display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("d"):
            detection_enabled = not detection_enabled
            print(f"Detection: {'ON' if detection_enabled else 'OFF'}")
        elif key == ord("r"):
            if recording:
                recording = False
                if writer is not None:
                    writer.release()
                    writer = None
                if output_path:
                    print(f"Saved: {output_path}")
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = OUTPUT_DIR / f"reolink_{timestamp}.mp4"
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                writer = cv2.VideoWriter(
                    str(output_path), fourcc, fps, (width, height),
                )
                recording = True
                print(f"Recording to: {output_path}")

    cap.release()
    if writer is not None:
        writer.release()
    cv2.destroyAllWindows()
    print("Done.")


if __name__ == "__main__":
    main()
