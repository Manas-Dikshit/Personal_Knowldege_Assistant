<div align="center">

# AI Hand Muscle Evaluator

### Real-Time Computer Vision Arm Flex Analyzer

*Pose detection meets pixel-perfect muscle science (sort of).*

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-CV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF?style=for-the-badge)](https://github.com/ultralytics/ultralytics)
[![PyTorch](https://img.shields.io/badge/PyTorch-DeepLearning-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](#license)

</div>

---

## Overview

**AI Hand Muscle Evaluator** is a webcam-based computer vision application that analyzes your arm flex in real time. It combines **pose estimation**, **segmentation**, **angle geometry**, and **temporal smoothing** to score your flex — then reacts with a suitably dramatic verdict.

> It's not a medical device. It's a hype machine with math behind it.

---

## Features

| Category | Capability |
|---|---|
| Detection | Real-time webcam pose & segmentation detection |
| Automation | Automatic left/right arm selection |
| Calibration | Relax-stage baseline capture |
| Flex Engine | Flex detection with 3-second hold mechanism |
| Scoring | Stable score locking after hold completes |
| Geometry | Angle-based joint analysis |
| Vision Metrics | Arm area expansion analysis via segmentation |
| Fun Factor | Emoji reactions based on final score |
| Control | Instant reset support |

---

## System Architecture

```mermaid
flowchart TD
    A["Webcam Feed"] --> B["YOLOv8 Pose Model"]
    A --> C["YOLOv8 Segmentation Model"]

    B --> D["Feature Extractor<br/>Joint Angles + Landmarks"]
    C --> E["Feature Extractor<br/>Arm Area + Expansion"]

    D --> F["Temporal Smoothing Layer"]
    E --> F

    F --> G{"Stage Controller"}

    G -->|"Stage 1"| H["RELAX<br/>Baseline Calibration"]
    H --> I["FLEX<br/>Detect Flex Trigger"]
    I --> J["HOLD<br/>3-Second Stability Check"]
    J --> K["Score Engine<br/>Angle + Area Fusion"]

    K --> L["Final Score Locked"]
    L --> M["Reaction Engine"]

    M --> N1["Baby Biceps"]
    M --> N2["Gym Bro"]
    M --> N3["Beast Mode"]
    M --> N4["Greek God"]

    G -->|"R Key Pressed"| H

    style A fill:#1a1a2e,stroke:#00d4ff,color:#ffffff
    style B fill:#16213e,stroke:#00d4ff,color:#ffffff
    style C fill:#16213e,stroke:#00d4ff,color:#ffffff
    style F fill:#0f3460,stroke:#e94560,color:#ffffff
    style G fill:#533483,stroke:#e94560,color:#ffffff
    style K fill:#e94560,stroke:#ffffff,color:#ffffff
    style L fill:#ffd700,stroke:#000000,color:#000000
    style M fill:#533483,stroke:#e94560,color:#ffffff
```

---

## Project Structure

```text
Hand_Muscle_Evaluator/
│
├── download_models.py      # Fetches YOLOv8 Pose, Segmentation & MobileNetV2
├── flex_evaluator.py        # Main application entry point
├── feature_extractor.py     # Angle & area feature computation
├── reaction_engine.py       # Score → emoji reaction mapping
├── requirements.txt          # Python dependencies
│
├── models/                   # Downloaded model weights
├── history/                  # Session history logs
├── assets/                   # Static assets (images, icons)
│
└── README.md
```

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/Manas-Dikshit/Hand_Muscle_Evaluator
cd Hand_Muscle_Evaluator
```

**2. Create a virtual environment**
```bash
python -m venv venv
```

**3. Activate it**

| OS | Command |
|---|---|
| Windows | `venv\Scripts\activate` |
| Linux / Mac | `source venv/bin/activate` |

**4. Install dependencies**
```bash
pip install -r requirements.txt
```

---

## Download Models

```bash
python download_models.py
```

This fetches:
- **YOLOv8 Pose** — skeletal keypoint detection
- **YOLOv8 Segmentation** — precise arm masking
- **MobileNetV2** — lightweight auxiliary feature extraction

---

## Run the App

```bash
python flex_evaluator.py
```

---

## Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant S as System

    U->>S: Stand in front of webcam
    S->>U: RELAX — capture baseline
    U->>S: Flex arm
    S->>U: FLEX detected
    U->>S: Hold pose
    S->>U: HOLD — 3 second timer
    S->>S: Compute Angle + Area Score
    S->>U: FINAL SCORE locked
    S->>U: Reaction revealed
```

**Stages:**

1. **RELAX** — Keep your arm relaxed while the system captures baseline measurements.
2. **FLEX** — Flex your arm and hold the position.
3. **HOLD** — Maintain the pose for **3 seconds** straight.
4. **FINAL SCORE** — The score locks in.
5. **REACTION** — Baby Biceps · Gym Bro · Beast Mode · Greek God

---

## Controls

| Key | Action |
|---|---|
| `ESC` | Exit the application |
| `R` | Reset the current evaluation |

---

## Tech Stack

<div align="center">

| Technology | Purpose |
|---|---|
| **Python** | Core language |
| **OpenCV** | Real-time video processing |
| **Ultralytics YOLOv8** | Pose + Segmentation inference |
| **NumPy** | Numerical & geometric computation |
| **Transformers** | Auxiliary feature modeling |
| **PyTorch** | Deep learning backend |

</div>

---

## Example Output

```text
Stage: FLEX
Selected Arm: RIGHT
Angle: 73°
Score: 84
Beast Mode
```

---

## Future Improvements

- Voice reactions
- History tracking
- Progress dashboard
- Leaderboard
- Streamlit interface
- Mobile app support
- Multi-person evaluation
- Muscle growth tracking over time

---

## Disclaimer

This project evaluates **flex posture and visual appearance** from a webcam feed only.
It is **not** a medical, physiological, or strength assessment tool. Results are for entertainment purposes.

---

## License

Released under the **MIT License**.

---

<div align="center">

### Made by **MRD** with ❤️

</div>
