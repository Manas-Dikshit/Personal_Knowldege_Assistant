# Face Shape AI Agent

An AI-powered desktop application built in Java that detects a user's face through a webcam, identifies facial landmarks using a pre-trained ONNX model, estimates the face shape, and recommends suitable hairstyles in real time.

## Author

**Manas Ranjan Dikshit**

---

## Features

* Real-time webcam capture
* Face detection using OpenCV Haar Cascade
* 106-point facial landmark detection using a pre-trained ONNX model
* Face shape classification
* Live hairstyle recommendations
* Fully implemented in Java
* ONNX Runtime inference
* OpenCV image processing

---

## Project Workflow

```text
Webcam
   ↓
Face Detection
   ↓
Face Cropping
   ↓
106 Landmark Detection
   ↓
Face Shape Classification
   ↓
Hairstyle Recommendation
   ↓
Live Display
```

---

## Tech Stack

| Technology                 | Purpose                          |
| -------------------------- | -------------------------------- |
| Java 17                    | Core Application                 |
| Maven                      | Dependency Management            |
| OpenCV                     | Face Detection & Computer Vision |
| ONNX Runtime               | AI Model Inference               |
| InsightFace Landmark Model | 106 Facial Landmark Detection    |

---

## Project Structure

```text
face-shape-agent/
│
├── models/
│   ├── 2d106det.onnx
│   └── haarcascade_frontalface_default.xml
│
├── src/
│   └── main/
│       └── java/
│           └── com/
│               └── manas/
│                   ├── CameraTest.java
│                   ├── FaceDetector.java
│                   ├── LandmarkDetector.java
│                   ├── FaceLandmark.java
│                   ├── FaceShape.java
│                   ├── FaceShapeClassifier.java
│                   ├── HairstyleRecommender.java
│                   ├── ModelInspector.java
│                   └── OnnxTest.java
│
├── pom.xml
└── README.md
```

---

## Dependencies

```xml
<dependency>
    <groupId>org.openpnp</groupId>
    <artifactId>opencv</artifactId>
    <version>4.9.0-0</version>
</dependency>

<dependency>
    <groupId>com.microsoft.onnxruntime</groupId>
    <artifactId>onnxruntime</artifactId>
    <version>1.17.3</version>
</dependency>

<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <version>2.18.2</version>
</dependency>
```

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/Manas-Dikshit/model-using-java.git
cd model-using-java
```

### 2. Place Models

Create a models folder:

```bash
mkdir models
```

Place:

```text
2d106det.onnx
haarcascade_frontalface_default.xml
```

inside the models directory.

---

### 3. Build Project

```bash
mvn clean compile
```

---

### 4. Run Application

```bash
mvn exec:java "-Dexec.mainClass=com.manas.CameraTest"
```

---

## How It Works

### Face Detection

The application first detects a face using OpenCV's Haar Cascade classifier.

### Landmark Detection

The detected face is cropped and resized to:

```text
192 × 192
```

The crop is passed to the pre-trained ONNX landmark model which returns:

```text
106 facial landmarks
```

These landmarks represent:

* Jawline
* Chin
* Eyebrows
* Eyes
* Nose
* Lips
* Facial contours

### Face Shape Classification

Facial proportions are calculated using landmark geometry.

Examples:

* Oval
* Round
* Square
* Oblong
* Diamond
* Heart

### Hairstyle Recommendation

Based on the detected face shape, the application recommends suitable hairstyles.

Examples:

```text
Oval Face:
- Textured Quiff
- Pompadour
- Side Part
- French Crop

Round Face:
- High Fade
- Faux Hawk
- Undercut
- Pompadour
```

---

## Future Improvements

* Deep-learning based face shape classifier
* Hairstyle image preview generation
* Gender-specific recommendations
* Beard style recommendations
* Hairstyle ranking system
* Modern GUI using JavaFX
* Hugging Face model integration
* Multi-face detection support
* Hairstyle similarity search

---

## Requirements

* Java 17+
* Maven 3.8+
* Windows / Linux / macOS
* Webcam
* Visual C++ Redistributable (Windows)

---

## License

MIT License

Copyright (c) 2026 Manas Ranjan Dikshit

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Acknowledgements

* OpenCV
* ONNX Runtime
* InsightFace
* Maven
* Java Community

Built with ❤️ by **Manas Ranjan Dikshit**
