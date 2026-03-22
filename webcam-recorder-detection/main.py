"""
Webcam Recorder with Object Detection

Reads from webcam, detects objects in real time, and saves video to the C drive.
Press 'r' to start/stop recording, 'd' to toggle detection, 'q' to quit.
"""

import sys
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from detector import ObjectDetector

OUTPUT_DIR = Path("C:/webcam_recordings")


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


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        sys.exit(1)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    detector = ObjectDetector(model_size="n", confidence=0.5)
    detection_enabled = True

    writer: cv2.VideoWriter | None = None
    recording = False
    output_path: Path | None = None

    print("Webcam Recorder with Object Detection")
    print("=" * 45)
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
            # Print detected objects to console (every ~1 second)
            frame_count += 1
            if frame_count % 30 == 0 and results.boxes is not None:
                names = [results.names[int(box.cls[0])] for box in results.boxes]
                print(f"Detected: {', '.join(names)}")

        if recording and writer is not None:
            writer.write(display_frame)

        # Status overlay
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

        cv2.imshow("Webcam Recorder + Detection", display_frame)

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
                output_path = OUTPUT_DIR / f"recording_{timestamp}.mp4"
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
