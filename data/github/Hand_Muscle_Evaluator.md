Repository: Hand_Muscle_Evaluator

Description:
No description

Language:
Python

Topics:


Stars:
0

Repository URL:
https://github.com/Manas-Dikshit/Hand_Muscle_Evaluator

README:

#  AI Hand Muscle Evaluator

An AI-powered webcam application that evaluates arm flex quality using computer vision.

The project uses:

* YOLOv8 Pose
* YOLOv8 Segmentation
* OpenCV
* NumPy
* Temporal smoothing
* Automatic arm selection
* Real-time scoring
* Funny emoji reactions

---

# Features

 Real-time webcam detection

 Automatic left/right arm selection

 Relax calibration stage

 Flex detection

 3-second hold mechanism

 Stable score locking

 Angle-based analysis

 Arm area expansion analysis

 Emoji reactions

 Reset support

---

# Project Structure

```text
Hand_Muscle_Evaluator/
│
├── download_models.py
├── flex_evaluator.py
├── feature_extractor.py
├── reaction_engine.py
├── requirements.txt
│
├── models/
├── history/
├── assets/
│
└── README.md
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/Manas-Dikshit/Hand_Muscle_Evaluator
cd Hand_Muscle_Evaluator
```

Create virtual environment:

```bash
python -m venv venv
```

Activate:

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Download Models

```bash
python download_models.py
```

This downloads:

* YOLOv8 Pose
* YOLOv8 Segmentation
* MobileNetV2

---

# Run

```bash
python flex_evaluator.py
```

---

# Workflow

## RELAX Stage

Keep your arm relaxed.

The system captures baseline measurements.

↓

## FLEX Stage

Flex your arm and hold.

↓

## HOLD Stage

Maintain the pose for 3 seconds.

↓

## FINAL SCORE

The score is locked.

↓

## Reaction

 Baby Biceps

 Gym Bro

 Beast Mode

 Greek God

---

# Controls

| Key | Action           |
| --- | ---------------- |
| ESC | Exit             |
| R   | Reset evaluation |

---

# Tech Stack

* Python
* OpenCV
* Ultralytics YOLOv8
* NumPy
* Transformers
* PyTorch

---

# Future Improvements

* Voice reactions
* History tracking
* Progress dashboard
* Leaderboard
* Streamlit interface
* Mobile app support
* Multi-person evaluation
* Muscle growth tracking

---

# Disclaimer

This project evaluates flex posture and visual appearance from a webcam.

It is **not** a medical, physiological, or strength assessment tool.

---

# License

MIT License

---

## Example Output

```text
Stage: FLEX

Selected Arm: RIGHT

Angle: 73°

Score: 84

 Beast Mode
```