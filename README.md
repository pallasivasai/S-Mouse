# SAI Air Mouse

A computer-vision based air mouse that lets you control the Windows mouse using hand gestures captured through a webcam.

## What I built

This project started as a basic hand-tracking air mouse and was extended into a smoother, low-latency gesture controller.

### Core controls
- Index finger movement controls the mouse cursor.
- Index finger + thumb pinch performs a left click.
- A quick second pinch performs a double click.
- Holding the index-thumb pinch starts drag-and-drop.
- Thumb + middle-finger pinch performs a right click.
- Two-finger movement supports vertical scrolling.
- Two-finger horizontal movement supports horizontal scrolling where supported.
- Hand tracking loss safely releases an active drag.

### Performance improvements
- 640x480 camera mode for lower processing latency.
- Requests 60 FPS from cameras that support it.
- Low camera buffering for reduced latency.
- MediaPipe Hands with `model_complexity=0`.
- Adaptive cursor smoothing for precise small movements and faster large movements.
- Pinch detection normalized against hand size.
- Click cooldown and press/release hysteresis reduce accidental repeated clicks.
- Live FPS, hand-detection, pinch and gesture status are shown in the camera window.

> A 60 FPS request does not guarantee 60 FPS. The actual FPS depends on the webcam, driver, CPU, lighting, and other workload.

## Requirements

- Windows 10/11
- Python 3.12
- Working webcam
- MediaPipe
- OpenCV
- PyAutoGUI

## Installation

Create a virtual environment:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run

```powershell
python air_mouse.py
```

Move your index finger inside the on-screen control rectangle.

Press `Q` to stop the application.

## Files

- `air_mouse.py` - main runnable Air Mouse application.
- `HandTracking.py` - reusable hand tracking / landmark helper.
- `requirements.txt` - Python dependencies.

## Troubleshooting

### Hand is not detected
Use a well-lit environment. Avoid putting a bright window directly behind your hand. The camera should see the hand clearly.

### Cursor feels slow
Use a camera mode that provides higher FPS and close unnecessary applications. The application is tuned for 640x480 for lower latency.

### PyAutoGUI safety
PyAutoGUI failsafe remains enabled. Moving the cursor to the top-left corner can trigger PyAutoGUI's emergency stop behavior.

## Project status

The repository is intended to be ready to clone, install, and run with the files above.
