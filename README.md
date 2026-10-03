# SAI Air Mouse 🖐️🖱️

> **From a webcam-controlled mouse to a programmable human-computer interface.**

SAI Air Mouse is a computer-vision project that turns natural hand movement into Windows input. A webcam observes the hand, MediaPipe extracts hand landmarks, and Python translates those landmarks into mouse, click, drag, scroll, application-switching, and customizable gesture actions.

This project is designed as a **first step toward a more natural, touch-free interaction layer**—the kind of direction often imagined in futuristic interfaces such as the technology shown in *Iron Man*. The project does not claim movie-level capabilities; it is a practical prototype built from accessible computer-vision software and a normal webcam.

---

## 🚀 Why This Project Exists

Traditional computers depend heavily on a physical mouse, keyboard, or touchscreen.

SAI Air Mouse explores a different idea:

**What if your hand could become the controller?**

Instead of touching a mouse:

- ☝️ Move your index finger → move the cursor
- ✌️ Bring index + middle finger together → click
- ✌️ Hold the gesture → drag
- 👍 + middle-finger gesture → right click
- ✌️ Use two fingers → scroll
- ✋ Open-palm movement → switch between recent applications
- 🖐️ Learn a custom gesture → trigger a custom action

The project therefore moves from a simple **air mouse** toward a **gesture-driven human-computer interface**.

---

## ✨ Current Capabilities

### 🖱️ Air Mouse Control

The index fingertip is used as the primary cursor controller.

The application maps the finger position inside a webcam control region to the Windows screen and applies adaptive smoothing so small hand motion can be handled more precisely while larger movement remains responsive.

### 🖱️ Click + Cursor Lock

**Index + Middle fingers close** activates the left-click gesture.

During the click gesture, the cursor is temporarily locked to the current screen position. This prevents small hand movement during the gesture from moving the cursor onto a nearby UI element before the click is completed.

### 🖱️ Drag & Drop

Holding the click gesture long enough starts a mouse-button hold.

Release the gesture to drop the selected item.

### 🖱️ Right Click

A **thumb + middle-finger** pinch is mapped to a Windows right click.

### 📜 Scrolling

The project supports:

- Two-finger vertical scrolling
- Two-finger horizontal scrolling where the operating system/application supports it
- Open-palm / four-finger vertical scrolling in versions that include the palm-scroll extension

### 🔄 Application Switching

Open-palm horizontal movement is used as a gesture layer for recent Windows application switching.

- Move the palm to the right → next application with `Alt + Tab`
- Move the palm to the left → previous application with `Alt + Shift + Tab`

The switching logic uses horizontal distance, motion speed, direction dominance, gesture timing, and a lock/cooldown to reduce accidental triggers.

---

# 🧠 SAI Gesture Learning

One of the project's important extensions is the **custom gesture system**.

The idea is simple:

> **You define the gesture. SAI learns its hand shape. You decide what it should do.**

A learned gesture is represented using normalized hand-landmark information rather than absolute camera pixels. This makes the gesture template less dependent on where the hand appears in the frame or how large it appears.

### Example workflow

1. Enter gesture-learning mode.
2. Hold a special hand pose.
3. SAI captures a series of landmark frames.
4. The frames are averaged into a normalized gesture template.
5. Choose an action.
6. The gesture is stored locally.
7. Performing the learned gesture again can trigger its assigned action.

The current implementation stores custom gestures in `sai_gestures.json`.

That means learned mappings can persist between application runs.

---

## ⚡ Example Custom Actions

The current gesture-learning implementation provides actions such as:

| Action | Example result |
|---|---|
| Screenshot | Capture the screen and save an image |
| Play/Pause | Control media playback |
| Next Track | Move to the next media track |
| Previous Track | Move to the previous media track |
| Show Desktop | Trigger Windows `Win + D` |
| Calculator | Open Windows Calculator |
| Open Browser | Open a browser page |

The important architectural idea is not the individual action list.

It is the **gesture → action mapping**.

That mapping can be expanded later to support more Windows shortcuts, application launching, workflows, automation commands, or project-specific actions.

---

# 🎯 From Air Mouse to Programmable Gesture Interface

SAI Air Mouse can be viewed as a progression:

```text
Webcam
   ↓
Hand Detection
   ↓
21 Hand Landmarks
   ↓
Gesture Interpretation
   ↓
Intent
   ↓
Windows Action
```

The current project demonstrates several levels of this pipeline:

```text
Hand movement
   ↓
Cursor control

Finger relationship
   ↓
Click / drag / right-click

Finger configuration
   ↓
Scroll / mode selection

Palm movement
   ↓
Application switching

Learned gesture
   ↓
Custom action
```

That is why this repository is more than a traditional webcam mouse. It is an early prototype for a **programmable gesture-control layer**.

---

# 🤖 Future-Tech Direction

The long-term vision of SAI Air Mouse is to explore interaction that feels more natural, spatial, and programmable.

Possible future directions include:

### 🧠 Better Gesture Recognition
Move from simple geometric rules toward a learned gesture classifier that can recognize more complex hand poses and motion sequences.

### ✋ Dynamic Gestures
Recognize not only **what the hand looks like**, but also **how it moves over time**.

```text
Pose → Motion → Direction → Speed → Intent
```

### 🎛️ Gesture Profiles
Different profiles could provide different gesture mappings:

- Work
- Presentation
- Media
- Coding
- Gaming
- Accessibility

### 🪟 Advanced Window Control
Future gestures could control window snapping, minimize/maximize, desktop navigation, task view, and application groups.

### 🎵 Media Control
Gesture-driven play/pause, next/previous, volume, and mute.

### 🖥️ Presentation Mode
Use hand gestures for next slide, previous slide, presentation control, and pointer movement.

### 🔗 Workflow Automation
A future gesture could trigger a complete workflow rather than one key press:

```text
Custom Gesture
      ↓
Recognize
      ↓
Run workflow
      ↓
Open applications
      ↓
Arrange windows
      ↓
Execute commands
```

### 🔐 Privacy-First Local Processing
A major future direction is keeping gesture interpretation locally on the machine so the webcam stream does not need to leave the device.

---

# 🏗️ Architecture

```text
┌─────────────────────────────┐
│          Webcam             │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│     OpenCV Frame Capture    │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│      MediaPipe Hands        │
│   21 hand landmarks/frame   │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│   Gesture Interpretation    │
│                             │
│ • Index movement            │
│ • Click / drag              │
│ • Right click               │
│ • Scroll                    │
│ • Palm swipe                │
│ • Custom gesture matching   │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│       Intent / Action       │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│       Windows Input         │
│   PyAutoGUI / OS actions    │
└─────────────────────────────┘
```

---

# 📂 Repository Structure

```text
S-Mouse/
│
├── air_mouse.py
├── HandTracking.py
├── requirements.txt
├── req.txt
└── README.md
```

### `air_mouse.py`

Main runnable application.

It contains the camera loop, MediaPipe hand processing, cursor control, gestures, application switching, and custom gesture learning/matching.

### `HandTracking.py`

Reusable hand-tracking helper containing:

- MediaPipe Hands setup
- Landmark extraction
- Finger-state detection
- Landmark distance utilities
- Bounding-box support

### `requirements.txt`

Current Python dependencies:

```text
opencv-python>=4.8,<5
mediapipe==0.10.21
pyautogui>=0.9.54
```

---

# ⚙️ Requirements

- Windows 10/11
- Python 3.12
- Working webcam
- OpenCV
- MediaPipe
- PyAutoGUI

The current repository pins MediaPipe to `0.10.21` and targets Python 3.12.

---

# 🛠️ Installation

Create a Python 3.12 virtual environment:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run:

```powershell
python air_mouse.py
```

Press:

```text
Q
```

to stop the application.

---

# 🖐️ Basic Gesture Map

```text
☝️  INDEX FINGER
    ↓
Mouse cursor

✌️  INDEX + MIDDLE CLOSE
    ↓
Left click

✌️  HOLD
    ↓
Drag

👍 + MIDDLE
    ↓
Right click

✌️  TWO FINGERS
    ↓
Scroll

✋  OPEN PALM + HORIZONTAL MOTION
    ↓
Previous / Next App

CUSTOM LEARNED GESTURE
    ↓
Assigned custom action
```

---

# 🎯 Performance Design

The application is tuned around a **640×480** camera mode and requests up to 60 FPS where supported.

The actual frame rate depends on:

- Webcam hardware
- Camera driver
- CPU load
- Lighting
- Other running applications

The project uses low camera buffering and MediaPipe's lightweight hand model configuration to reduce latency.

Cursor smoothing is adaptive so the system can prioritize precision for small movements without making large movements unnecessarily sluggish.

---

# 💡 Lighting Matters

Computer vision quality depends heavily on the camera image.

For reliable hand recognition:

- Use even lighting on the hand.
- Avoid a very bright window directly behind the hand.
- Keep the hand within the visible control region.
- Avoid extreme motion blur.

A backlit hand can appear as a dark silhouette and reduce landmark detection quality.

---

# 🛡️ Safety

PyAutoGUI's failsafe remains enabled.

If the cursor reaches the configured PyAutoGUI failsafe region, the library can stop automation according to PyAutoGUI's safety behavior.

The application also releases an active drag when hand tracking is lost.

---

# 🔬 Project Evolution

SAI Air Mouse is intentionally being developed in stages:

```text
Stage 1
Basic hand tracking
        ↓
Stage 2
Air mouse
        ↓
Stage 3
Click / drag / scroll
        ↓
Stage 4
Application switching
        ↓
Stage 5
Custom gesture learning
        ↓
Stage 6
Programmable gesture workflows
        ↓
Stage 7
Advanced spatial interaction
```

This makes the repository a foundation for experimenting with **touch-free human-computer interaction**, rather than treating the air mouse as the final product.

---

# 🚀 Vision

The long-term concept behind SAI Air Mouse is:

> **The computer should understand the user's interaction, not just the user's clicks.**

A future version could combine:

**Vision + Gesture + Motion + Intent + Automation**

to create an interface where a user's hand becomes a programmable input device.

That is the direction this project is exploring: a practical first step from a webcam-based air mouse toward a more natural, customizable, and futuristic human-computer interface.

---

## 👨‍💻 Author

**Palla Siva Sai**

GitHub: [@pallasivasai](https://github.com/pallasivasai)

---

## 📜 License

No explicit open-source license is currently declared in this repository. Add a `LICENSE` file before presenting the project as licensed for reuse.
