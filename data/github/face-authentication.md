Repository: face-authentication

Description:
No description

Language:
Jupyter Notebook

Topics:


Stars:
0

Repository URL:
https://github.com/Manas-Dikshit/face-authentication

README:

﻿# MRD Face Authentication System

## Overview

MRD Face Authentication System is a real-time face verification project that identifies and authenticates **Manas Dikshit (MRD)** using facial recognition technology.

The project uses:

* Python
* InsightFace
* OpenCV
* NumPy

The system can:

* Detect faces from images
* Generate facial embeddings
* Create a personal identity profile
* Verify whether a face belongs to MRD
* Authenticate users through a webcam in real time

---

## Features

* Face Detection
* Face Cropping Pipeline
* Face Embedding Generation
* Image-Based Verification
* Real-Time Webcam Authentication
* Fast and Lightweight
* Easy to Extend

---

## Project Structure

```text
face-authentication/
│
├── crop_faces.py
├── create_embeddings.py
├── verify_mrd.py
├── webcam_auth.py
├── main.ipynb
├── README.md
├── LICENSE
└── .gitignore
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Manas-Dikshit/face-authentication.git
cd face-authentication
```

Install dependencies:

```bash
pip install insightface onnxruntime opencv-python numpy
```

---

## Dataset Preparation

Create a folder containing images of yourself:

```text
my_photos/
```

Guidelines:

* Use images with different angles.
* Include different lighting conditions.
* Include different facial expressions.
* Use both indoor and outdoor photos.

---

## Face Cropping

Run:

```bash
python crop_faces.py
```

This will automatically detect and crop faces into:

```text
cropped_faces/
```

---

## Generate Face Embeddings

Run:

```bash
python create_embeddings.py
```

Output:

```text
mrd_embedding.npy
```

This file contains the reference identity embedding used for authentication.

---

## Verify a Single Image

Place a test image in the project directory and update the image path if necessary.

Run:

```bash
python verify_mrd.py
```

Example output:

```text
Similarity: 0.73
ACCESS GRANTED
```

or

```text
Similarity: 0.18
ACCESS DENIED
```

---

## Webcam Authentication

Run:

```bash
python webcam_auth.py
```

The system will:

1. Open the webcam.
2. Detect faces in real time.
3. Compare detected faces with the stored MRD embedding.
4. Grant or deny access based on similarity.

Press `Q` to exit.

---

## Technology Stack

| Component           | Technology  |
| ------------------- | ----------- |
| Language            | Python      |
| Face Recognition    | InsightFace |
| Computer Vision     | OpenCV      |
| Numerical Computing | NumPy       |

---

## Future Improvements

* Face Liveness Detection
* Anti-Spoofing Protection
* Multi-User Authentication
* Attendance Management Integration
* Smart Lock Integration
* Mobile Application Support

---

## Author

**Manas Dikshit**

GitHub: https://github.com/Manas-Dikshit

Owner and Maintainer of this Project.

---

## License

Copyright (c) 2026 Manas Dikshit

All Rights Reserved.

This project and its source code are the intellectual property of Manas Dikshit.

Permission is granted to use, study, and modify this software for personal, educational, and research purposes.

Commercial use, redistribution, sublicensing, resale, or claiming ownership of this project without explicit written permission from the author is prohibited.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.