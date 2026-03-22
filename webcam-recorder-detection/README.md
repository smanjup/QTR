# Webcam Recorder with Object Detection

Records from your webcam, detects objects in real time using YOLOv8, and saves video to `C:\webcam_recordings\`.

## Setup

```bash
pip install -r requirements.txt
```

On first run, YOLOv8 will download the model (~6 MB for nano).

## Usage

```bash
python main.py
```

### Controls

| Key | Action |
|-----|--------|
| **r** | Start or stop recording |
| **d** | Toggle object detection on/off |
| **q** | Quit |

### Output

- Videos saved to `C:\webcam_recordings\recording_YYYYMMDD_HHMMSS.mp4`
- Recorded video includes bounding boxes and labels when detection is enabled
- Detects 80 COCO classes (person, car, dog, bottle, etc.)

## Requirements

- Python 3.9+
- Webcam
