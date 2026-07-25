# 🎓 Digital Campus Management System

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com/)
[![SQLite/PostgreSQL](https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Google Gemini AI](https://img.shields.io/badge/AI-Gemini%20Pro-8E44AD?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)

An all-in-one, modern, web-based **Digital Campus Management System** designed to streamline academic, administrative, and transportation operations for educational institutions. Featuring a sleek UI, role-based dashboards, automated Excel/CSV attendance parsing, online quizzes, fee tracking, bus tracking, and an integrated **Google Gemini AI Assistant**.

---

## 🏗️ Clean Project Architecture

The repository is modularly organized into distinct **Frontend** and **Backend** directories for clear separation of concerns, readability, and ease of maintainability.

```
college-minor-project/
├── 🎨 frontend/                  # User Interface & Visual Assets
│   ├── static/                   # Static Assets
│   │   ├── css/                  # Custom CSS (style.css with responsive design)
│   │   └── js/                   # Interactive JavaScript Modules
│   │       ├── script.js         # Global interactive logic
│   │       └── core/             # View-specific JS modules
│   └── templates/                # Jinja2 / Django HTML Templates
│       ├── base.html             # Core Layout Template
│       ├── core/                 # App Views (Dashboards, Forms, Quizzes, Attendance)
│       └── includes/             # Reusable UI Partials & Components
│
├── ⚙️ backend/                   # Server-side Logic, Database & APIs
│   ├── core/                     # Django Application Core
│   │   ├── admin.py              # Django Admin Panel Configuration
│   │   ├── forms.py              # Form Definitions & Input Validation
│   │   ├── models.py             # ORM Models (User, Attendance, Quiz, Fee, Bus, etc.)
│   │   ├── urls.py               # Route Definitions
│   │   ├── utils.py              # Gemini AI Integration, PDF & Helper Utilities
│   │   └── views.py              # Controller & Business Logic
│   ├── digital_campus/           # Global Django Settings & WSGI
│   │   ├── settings.py           # Environment & App Settings
│   │   ├── urls.py               # Main Routing Table
│   │   └── wsgi.py               # WSGI Entrypoint (Serverless & Vercel compatible)
│   ├── scripts/                  # Seed Generators & Verification Scripts
│   │   └── populate_data.py      # Automated Test Data Generator
│   ├── manage.py                 # Backend Django CLI Utility
│   └── requirements.txt          # Python Dependencies Manifest
│
├── 📂 media/                     # User Uploaded Documents & Media Attachments
├── 🚀 manage.py                  # Root Helper CLI (Run commands directly from root)
├── ⚡ vercel.json                 # Vercel Serverless Deployment Configuration
├── 🔒 .env.local                 # Local Environment Variables
└── 📄 README.md                  # Project Documentation
```

---

## ✨ Key Features by Role

### 👨‍💼 1. Admin Portal
- **User Management & Verification**: Review, verify, and approve new Student, Teacher, and Driver registrations.
- **Bus Fleet Management**: Add bus routes, assign drivers, and monitor fleet status.
- **Fee Configuration**: Set up fee structures, view payment status, and approve student payments.
- **Grievance Redressal**: View and address complaints submitted by students or staff.
- **System Audit & Analytics**: Comprehensive dashboard overview of campus statistics.

### 👩‍🏫 2. Teacher Portal
- **Attendance Management**: Bulk upload attendance via Excel (`.xlsx`) or CSV, or mark attendance manually using an interactive grid interface.
- **Marks & Grading**: Batch entry grid for subject marks and internal evaluations.
- **Assignment Hub**: Create assignments with file attachments, set due dates, and grade student submissions.
- **Online Quiz Builder**: Create dynamic quizzes, manage question banks, and review auto-graded results.
- **Resource Center**: Upload lecture notes, syllabus guides, and reference material for students.

### 👨‍🎓 3. Student Portal
- **Personalized Dashboard**: Real-time summary of attendance percentages, upcoming assignments, and pending fees.
- **Attendance Analytics**: View subject-wise breakdown of present/absent days and attendance alerts.
- **Quiz Execution Engine**: Take online quizzes with immediate scoring and feedback.
- **Fee Payment Portal**: View fee breakdowns and submit payment transactions.
- **Live Bus Tracker**: Track assigned college bus routes and estimated timings.
- **Lost & Found Portal**: Report lost items or claim found items on campus.
- **🤖 Gemini AI Campus Assistant**: Ask academic questions, get help with campus rules, or seek study assistance.

### 🚚 4. Bus Driver Portal
- **Route Dashboard**: View assigned bus numbers, route details, and timing schedules.
- **Status Updates**: Update operational status for student tracking.

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Backend Framework** | Python 3.12, Django 6.0 |
| **Frontend UI** | HTML5, Modern Vanilla CSS3, Vanilla JavaScript (ES6+) |
| **Database** | SQLite (Local Development) / PostgreSQL (Production) |
| **AI Integration** | Google Gemini 1.5 / Pro API (`google-generativeai`) |
| **Static File Handling** | WhiteNoise (`CompressedStaticFilesStorage`) |
| **Deployment Platform** | Vercel Serverless Functions |

---

## 🚀 Quick Start & Local Setup Guide

Follow these steps to set up and run the project locally on your machine:

### Prerequisites
- **Python 3.10+** installed on your system.
- **Git** installed.

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/digital-campus-management.git
cd digital-campus-management
```

### 2. Create & Activate Virtual Environment
- **On Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **On macOS/Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment Variables
Create a `.env.local` file in the root directory:
```env
SECRET_KEY=your-django-secret-key-here
DJANGO_DEBUG=True
GEMINI_API_KEY=your-gemini-api-key-optional
```

### 5. Apply Migrations & Seed Sample Data
```bash
python manage.py makemigrations
python manage.py migrate
python backend/populate_data.py
```

### 6. Run the Development Server
You can run the server directly from the root folder:
```bash
python manage.py runserver 8000
```
Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## ☁️ Deployment on Vercel

This project is pre-configured for seamless serverless deployment on **Vercel**.

1. **Push your code to GitHub**.
2. **Import the repository into Vercel**.
3. Set the required **Environment Variables** in Vercel settings:
   - `SECRET_KEY`: A random strong string.
   - `DJANGO_DEBUG`: `False`
   - `GEMINI_API_KEY`: Your Gemini AI API Key.
   - `DATABASE_URL`: (Optional) PostgreSQL Connection String (e.g. Supabase, Neon, or Vercel Marketplace Postgres).
4. Click **Deploy**. Vercel will automatically build and deploy the app using `backend/digital_campus/wsgi.py` and `vercel.json`.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 🤝 Contact & Acknowledgments

- **Developer**: Niraj Kumar
- **Project**: College Minor Project - Digital Campus Management System
