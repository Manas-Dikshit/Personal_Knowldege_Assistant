# AirCanvas AI

Draw in the air with a single tracked finger and see it appear on screen in
real time — like writing on a touchscreen, except the "screen" is your
webcam feed and the "pen" is your hand.

AirCanvas AI uses **MediaPipe Hand Landmarker** for real, sub-pixel finger
tracking (no YOLO, no mocked detections) and an optional Hugging Face
segmentation model (`facebook/sam2-hiera-small`) for background
segmentation. Every drawing tool, gesture, undo/redo action, and toolbar
interaction is fully implemented and runs live at 30+ FPS.

---

## 1. Installation

```bash
# 1. Clone / unzip the project, then create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) set your Hugging Face token if you plan to enable
#    background segmentation — not required for core drawing.
export HF_TOKEN="hf_xxx...."          # Windows: set HF_TOKEN=hf_xxx....

# 4. Download the required models (safe to re-run — already-downloaded
#    files are skipped)
python download_models.py

# 5. Run the app
python main.py
```

To enable the optional segmentation model, also install its extra
dependencies and set the flag before downloading/running:

```bash
pip install torch torchvision sam2
export ENABLE_SEGMENTATION=1
python download_models.py
python main.py
```

Segmentation is entirely optional. Finger tracking and every drawing
feature work fully with it disabled (the default).

---

## 2. Folder Structure

```
aircanvas_ai/
├── main.py                 # Application entry point / real-time loop
├── download_models.py       # One dedicated script to fetch & cache models
├── config.py                 # All tunable configuration in one place
├── requirements.txt
├── README.md
│
├── utils/
│   ├── logger.py             # Shared logging setup (console + rotating file)
│   └── helpers.py             # Geometry, FPS meter, point smoothing
│
├── models/
│   ├── model_loader.py         # Loads MediaPipe + optional SAM2, GPU/CPU auto-detect
│   └── weights/                 # Downloaded model files land here
│
├── tracker/
│   ├── camera.py                 # Webcam wrapper (open/read/release)
│   └── hand_tracker.py             # MediaPipe landmark inference + finger lock-on
│
├── gestures/
│   └── gesture_detector.py         # Finger-count / pinch -> gesture classification
│
├── canvas/
│   ├── drawing.py                    # Stroke data model + pure rasterization
│   └── canvas.py                       # Stateful surface, undo/redo, save, composite
│
├── ui/
│   ├── toolbar.py                       # Toolbar layout, rendering, hit-testing
│   └── overlay.py                        # FPS/status HUD, selection prompt, cursor
│
├── tests/
│   ├── test_gesture_detector.py           # Pure-logic gesture tests
│   └── test_canvas.py                       # Stroke/undo/redo/composite tests
│
├── outputs/                                  # Saved drawings & screenshots (PNG)
└── assets/                                     # Icons / static assets (optional)
```

---

## 3. Model Information

| Purpose                     | Model                                   | Source                                  |
|------------------------------|------------------------------------------|--------------------------------------------|
| Hand / finger landmark tracking | MediaPipe Hand Landmarker (21 keypoints) | Google MediaPipe Tasks (official model bucket) |
| Optional background segmentation | `facebook/sam2-hiera-small`             | Hugging Face Hub                            |

Finger tracking **always** uses MediaPipe — it is the most accurate,
lowest-latency solution available for hand landmarks and is what makes
real-time 30+ FPS tracking possible on a laptop GPU or even CPU. YOLO is
intentionally not used for landmarks per the project's design.

The Hugging Face SAM2 model is wired in as an optional component for
future background segmentation / matting features and is loaded only when
`ENABLE_SEGMENTATION=1`. It never participates in finger tracking.

`download_models.py` is idempotent: it checks whether a model is already
present and valid before downloading anything, so running it repeatedly
(e.g., in CI or on every `main.py` boot) is cheap and safe.

---

## 4. How Tracking Works

1. Each webcam frame is converted to an `mp.Image` and passed to
   `HandLandmarker.detect_for_video`, which returns 21 normalized (x, y, z)
   landmarks per detected hand plus a handedness label.
2. `HandTracker._compute_fingers_up` determines which of the five fingers
   are extended using real joint geometry:
   - **Four fingers** (index/middle/ring/pinky): a finger counts as "up"
     when its tip sits meaningfully above its PIP joint in image space.
   - **Thumb**: compared along the x-axis instead of y (thumbs extend
     sideways), with the comparison direction flipped depending on
     handedness, since the camera feed is mirrored for a natural
     drawing experience.
3. **Finger lock-on**: at startup, `FingerSelector` waits until exactly
   one finger has been continuously raised for
   `FINGER_SELECTION_STABLE_FRAMES` frames (default 20, roughly two-thirds
   of a second at 30 FPS), then locks that finger in as the permanent
   drawing pointer. The prompt never reappears until the app restarts.
4. Every subsequent frame, the tip position of the locked finger is
   converted to pixel coordinates and smoothed with an exponential moving
   average (`SmoothedPoint`) to remove per-frame jitter without adding
   noticeable lag.

---

## 5. How Drawing Works

* The canvas is a persistent, full-resolution white image separate from
  the camera feed. Only non-white pixels are composited on top of the
  live frame each frame (`Canvas.composite_over`), so the camera always
  shows through everywhere nothing has been drawn.
* Drawing is **stroke-based**, not pixel-based: every pen/brush/
  highlighter/eraser stroke, shape, or fill action is stored as a
  `Stroke` object (tool, color, size, points/endpoints). This is what
  makes true undo/redo possible — undo pops the last stroke and replays
  every remaining stroke from scratch onto a blank canvas
  (`canvas.drawing.render_all`), and redo pushes it back.
* **Freehand tools** (Pen, Brush, Highlighter, Eraser, Freehand) draw a
  line segment between consecutive fingertip positions every frame while
  the DRAW gesture is active. The Highlighter blends at 35% opacity; the
  Eraser paints in canvas-white (visually "erasing").
* **Shape tools** (Rectangle, Circle, Line, Arrow) record a start point
  when drawing begins and continuously update an end point while the
  gesture holds; the shape is only committed to the canvas once the
  gesture ends, with a live preview shown in the meantime.
* **Fill** performs a single OpenCV flood-fill at the fingertip position,
  armed once per gesture cycle so holding the gesture doesn't repeatedly
  flood-fill.
* Touching the on-screen toolbar always cancels any in-progress stroke
  first, so selecting a tool or color never leaves an accidental mark.

---

## 6. Controls

### Toolbar (touch with your locked finger)
| Section | Items |
|---|---|
| Tools | Pen, Brush, Highlighter, Eraser, Rectangle, Circle, Line, Arrow, Freehand, Fill |
| Actions | Undo, Redo, Save, Snap (screenshot), Clear |
| Colors | Black, White, Red, Green, Blue, Yellow, Orange, Purple, Pink, Brown, Gray, Cyan |
| Brush size | Drag the slider knob |

### Gestures (configurable in `config.py`)
| Gesture | Action |
|---|---|
| Only the locked finger raised | Draw |
| Closed fist (0 fingers) | Stop drawing |
| Two fingers raised | Eraser |
| Three fingers raised | Undo |
| Four fingers raised | Redo |
| Five fingers raised | Clear canvas |
| Thumb + index pinch | Adjust brush size (pinch in/out) |

### Keyboard Shortcuts
| Key | Action |
|---|---|
| `Q` | Quit — releases the webcam and destroys all windows |
| `S` | Save the current drawing as a PNG to `outputs/` |
| `Z` | Undo |
| `Y` | Redo |
| `C` | Clear canvas |
| `P` | Save a full screenshot (drawing + camera feed + UI) to `outputs/` |

---

## 7. Performance Tips

* The app is tuned for an **RTX 3050 laptop GPU** but runs fine on CPU —
  `models/model_loader.py` auto-detects CUDA via PyTorch (only relevant
  for the optional segmentation model; MediaPipe's own runtime manages
  its own CPU/GPU delegate internally).
* Keep `ENABLE_SEGMENTATION` off unless you specifically need background
  segmentation — it adds a heavyweight model load with no benefit to the
  core drawing experience.
* If FPS drops below 30, lower `CAMERA_WIDTH`/`CAMERA_HEIGHT` in
  `config.py` (e.g., 960x540) — hand tracking accuracy is barely affected
  since MediaPipe operates on a normalized crop internally.
* Good, even lighting on your hand improves landmark confidence far more
  than any threshold tweak.

---

## 8. Troubleshooting

| Symptom | Fix |
|---|---|
| `CameraError: Could not open webcam` | Check the webcam isn't in use by another app; try a different `CAMERA_INDEX` in `config.py`. |
| `FileNotFoundError: Hand landmarker model not found` | Run `python download_models.py` before `main.py`. |
| Finger selection never locks in | Ensure only one finger is raised and clearly visible; improve lighting; the other four fingers must be curled into the palm. |
| Drawing feels laggy | Lower camera resolution; ensure no other GPU-heavy app is running; confirm you're not accidentally running with `ENABLE_SEGMENTATION=1` without a GPU. |
| Undo/Redo/Clear fires repeatedls while gesture is held | This is edge-triggered by design — release the gesture (fist) between actions to trigger it again. |
| Segmentation model fails to load | It is optional; the app logs a warning and continues without it. Verify `torch`, `sam2` are installed and `download_models.py` was run with `ENABLE_SEGMENTATION=1`. |

---

## 9. Running Tests

Core logic (gesture classification, stroke/undo/redo/compositing) is
covered by dependency-light unit tests that do not require a webcam or
the MediaPipe model file:

```bash
pytest tests/
```
