"""Object detection using YOLOv8."""

import numpy as np
from ultralytics import YOLO


class ObjectDetector:
    """YOLOv8-based object detector for general objects (COCO classes)."""

    def __init__(self, model_size: str = "n", confidence: float = 0.5):
        self.model = YOLO(f"yolov8{model_size}.pt")
        self.confidence = confidence

    def detect(self, frame: np.ndarray):
        """Detect objects in frame. Returns YOLO results object."""
        results = self.model.predict(
            frame,
            conf=self.confidence,
            verbose=False,
        )[0]
        return results
