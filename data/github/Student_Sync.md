# Student_Sync

> **A Centralized Digital Platform for Comprehensive Student Activity Records in Higher Education Institutions (HEIs)**

---

## 📖 Overview

In modern education, student achievements are often scattered across departments or lost in paper-based records. From academic performance to co-curricular participation, there is no centralized system to document and validate a student's complete profile.  

**Smart Student Hub** solves this by offering a **web and mobile-based platform** that consolidates academic and non-academic achievements in a verified, dynamic, and easily shareable digital portfolio.  

This platform not only empowers students but also simplifies administrative tasks, particularly during audits and accreditations like **NAAC, AICTE, and NIRF**.  

---

## ✨ Key Features

✔ Dynamic Student Dashboard – Real-time updates on academics, attendance, and activities
✔ Activity Tracker – Upload and validate conferences, workshops, MOOCs, internships, etc.
✔ Faculty Approval Panel – Ensures authenticity of achievements
✔ Auto-Generated Digital Portfolio – Shareable in PDF or link format
✔ Analytics & Reporting – Institutional reports for NAAC/AICTE/NIRF evaluations
✔ Integration Support – Connect with LMS, ERP, or other digital platforms

pgsql
Copy code

---

## 🛠️ Technology Stack

**Frontend**  
- HTML, CSS, JavaScript (Vanilla)  
- Tailwind CSS – responsive and modern UI  
- Chart.js – visual analytics  
- Three.js – interactive 3D elements  

**Backend**  
- Django (Python) – robust server-side framework  
- Firebase – authentication, real-time database, and storage  

---
## 🏗️ System Architecture
+------------------------------+ +------------------------------+ +-------------------------------+
| Client | ---> | Backend | ---> | Firebase |
| Web & Mobile | | Django REST APIs | | Auth · Firestore · Storage |
| HTML · Tailwind · Chart.js | | Faculty/Admin Panel | | |
+------------------------------+ +------------------------------+ +-------------------------------+


**Flow:** Client (UI) → Backend (APIs, validation, faculty approvals) → Firebase (Auth, DB, storage)

**Components**
- **Client:** HTML / Vanilla JS, Tailwind, Chart.js, Three.js  
- **Backend:** Django (REST APIs), Admin/Faculty panels  
- **Data & Auth:** Firebase Authentication, Firestore, Cloud Storage

Extra: Compact Markdown table (optional) — copy-paste friendly
| Layer    | Main Technologies                            | Responsibility |
|---------:|----------------------------------------------|----------------|
| Client   | HTML, Vanilla JS, Tailwind, Chart.js, Three.js | UI, dashboards, uploads |
| Backend  | Django (REST APIs)                            | Validation, approvals, business logic |
| Data/Auth| Firebase Auth, Firestore, Cloud Storage       | Auth, persistent data, file storage |

🎯 Benefits
Builds a holistic digital profile for students

Simplifies career planning, placements, and higher education applications

Reduces administrative workload during audits & accreditations

Encourages active participation in extracurriculars

Enables data-driven decision-making at the institutional level

🚀 Getting Started
Clone the repository:
git clone (https://github.com/deba608/Student_Sync.git)

Set up the Django backend:
cd backend
python manage.py runserver

Open the frontend:
index.html
Configure Firebase:
Update the Firebase config in your frontend JavaScript file with your project credentials.

👨‍💻 Contributors
Lead Developers: @Manas-Dikshit, @deba608, @ADITYA-PADHIHARY

🔮 Future Enhancements
AI-based course & activity recommendations

Dedicated mobile app for Android & iOS

Integration with government/corporate skill-recognition platforms

📄 License
This project is licensed under the MIT License.
