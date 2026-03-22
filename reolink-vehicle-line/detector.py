"""Vehicle detection and tracking using YOLOv8 (COCO vehicle classes only)."""

import numpy as np
from ultralytics import YOLO

# COCO: car, motorcycle, bus, truck
VEHICLE_CLASS_IDS = [2, 3, 5, 7]


class VehicleDetector:
    """YOLOv8 vehicle detector with optional ByteTrack-style tracking for line crossing."""

    def __init__(self, model_size: str = "n", confidence: float = 0.5):
        self.model = YOLO(f"yolov8{model_size}.pt")
        self.confidence = confidence

    def detect(self, frame: np.ndarray, track: bool = True):
        """Run detection; use track=True for persistent IDs (recommended for counting)."""
        if track:
            results = self.model.track(
                frame,
                conf=self.confidence,
                classes=VEHICLE_CLASS_IDS,
                verbose=False,
                persist=True,
            )[0]
        else:
            results = self.model.predict(
                frame,
                conf=self.confidence,
                classes=VEHICLE_CLASS_IDS,
                verbose=False,
            )[0]
        return results
