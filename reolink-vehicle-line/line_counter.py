"""Count vehicles crossing a horizontal virtual line using YOLO track IDs."""

from __future__ import annotations


class VehicleLineCounter:
    """
    Counts vehicles crossing a horizontal line (top → bottom by default).
    Uses YOLO track IDs when available; falls back to x-bucket heuristic without track.
    """

    def __init__(self, line_y: float):
        self.line_y = line_y
        self.count = 0
        self._tracked: dict[int, str] = {}  # track_id -> "above" | "below"
        self._position_tracked: dict[int, str] = {}  # x_bucket -> side (no track id)

    def set_line_y(self, line_y: float) -> None:
        """Update line position (e.g. after first frame dimensions known)."""
        self.line_y = line_y

    def update_from_yolo_results(self, results) -> int:
        """
        Process one frame of YOLO results (with optional track ids).
        Returns number of new crossings this frame.
        """
        if results is None or results.boxes is None or len(results.boxes) == 0:
            return 0

        new_count = 0
        for box in results.boxes:
            xy = box.xyxy[0]
            if hasattr(xy, "cpu"):
                xy = xy.cpu().numpy()
            x1, y1, x2, y2 = float(xy[0]), float(xy[1]), float(xy[2]), float(xy[3])
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            above = cy < self.line_y
            side = "above" if above else "below"

            track_id = None
            if box.id is not None:
                track_id = int(box.id[0])

            if track_id is not None:
                prev = self._tracked.get(track_id)
                if prev == "above" and side == "below":
                    new_count += 1
                    self.count += 1
                self._tracked[track_id] = side
            else:
                x_bucket = int(cx // 60)
                prev = self._position_tracked.get(x_bucket)
                if prev == "above" and side == "below":
                    new_count += 1
                    self.count += 1
                self._position_tracked[x_bucket] = side

        if len(self._tracked) > 200:
            self._tracked = dict(list(self._tracked.items())[-100:])
        if len(self._position_tracked) > 100:
            self._position_tracked = dict(list(self._position_tracked.items())[-50:])

        return new_count

    def reset(self) -> None:
        self.count = 0
        self._tracked.clear()
        self._position_tracked.clear()
