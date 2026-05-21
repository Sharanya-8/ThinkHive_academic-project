# ThinkHive — Complete Project Documentation

---

## 1. Project Overview

**ThinkHive** is a college-level academic project management portal built with Python (Flask) and SQLite. It allows students to submit their projects with detailed technical information and receive structured feedback, ratings, and phase-based progress tracking from faculty members. The platform also provides an analytics dashboard for data-driven insights across all submissions.

**Target Users:** Engineering college students and faculty across multiple departments.

---

## 2. Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Backend     | Python 3.x, Flask                   |
| Database    | SQLite3 (via Python's built-in lib) |
| Frontend    | HTML5, CSS3 (custom), Vanilla JS    |
| Charts      | Chart.js v4 (CDN)                   |
| File Upload | Werkzeug (secure_filename)          |
| Templating  | Jinja2 (Flask built-in)             |

---

## 3. Project Structure

```
thinkhive/
├── app.py                  # Main Flask application (all routes + DB logic)
├── database.db             # SQLite database (auto-created on first run)
├── uploads/                # Uploaded project files (auto-created)
├── static/
│   └── style.css           # All CSS styles
└── templates/
    ├── index.html          # Landing / home page
    ├── login.html          # Login page
    ├── signup.html         # Registration page
    ├── student.html        # Student dashboard
    ├── faculty.html        # Faculty dashboard
    ├── settings.html       # Profile & settings page
    └── analytics.html      # Analytics dashboard
```

---

## 4. Installation & Setup

### Prerequisites
- Python 3.8 or above
- pip

### Steps

```bash
# 1. Navigate to the project folder
cd thinkhive

# 2. Install dependencies
pip install flask werkzeug

# 3. Run the application
python app.py

# 4. Open in browser
http://127.0.0.1:5000
```

The database (`database.db`) and `uploads/` folder are created automatically on first run. No manual setup needed.

---

## 5. Database Schema

### Table: `users`

| Column      | Type    | Description                              |
|-------------|---------|------------------------------------------|
| id          | INTEGER | Primary key, auto-increment              |
| name        | TEXT    | Full name                                |
| username    | TEXT    | Unique login username                    |
| password    | TEXT    | Plain-text password (demo only)          |
| role        | TEXT    | `student` or `faculty`                   |
| roll        | TEXT    | Roll number (students only)              |
| department  | TEXT    | Department name                          |
| year        | TEXT    | Academic year (1st–4th)                  |
| teacher_id  | TEXT    | Teacher ID (faculty only)                |
| coordinator | TEXT    | Section / coordinator (faculty only)     |
| email       | TEXT    | Email address                            |
| phone       | TEXT    | Phone number                             |
| created_at  | TEXT    | Account creation timestamp               |

---

### Table: `projects`

| Column            | Type    | Description                                      |
|-------------------|---------|--------------------------------------------------|
| id                | INTEGER | Primary key, auto-increment                      |
| title             | TEXT    | Project title                                    |
| description       | TEXT    | Project description                              |
| department        | TEXT    | Department                                       |
| domain            | TEXT    | Technical domain (AI, Web, IoT, etc.)            |
| project_type      | TEXT    | Research Project / Regular Project               |
| project_nature    | TEXT    | Software / Hardware                              |
| year              | TEXT    | Academic year of student                         |
| guide_name        | TEXT    | Name of the assigned guide/mentor                |
| phase             | TEXT    | Current project phase (Phase 1–7)                |
| filename          | TEXT    | Uploaded file name (stored in /uploads)          |
| student_id        | INTEGER | Foreign key → users.id                           |
| feedback          | TEXT    | Faculty feedback text                            |
| rating            | INTEGER | Rating 1–5 given by faculty                      |
| status            | TEXT    | Pending / Reviewed / Approved                    |
| visited           | INTEGER | 0 = Not visited, 1 = Visited (faculty toggle)    |
| next_review       | TEXT    | Scheduled next review date (YYYY-MM-DD)          |
| review_notes      | TEXT    | Internal faculty notes (not shown to student)    |
| uploaded_at       | TEXT    | Submission timestamp                             |
| sw_languages      | TEXT    | Programming languages (comma-separated)          |
| sw_frameworks     | TEXT    | Frameworks used (comma-separated)                |
| sw_databases      | TEXT    | Database used                                    |
| sw_deployment     | TEXT    | Deployment platform                              |
| sw_github         | TEXT    | GitHub repository URL                            |
| sw_demo_url       | TEXT    | Live demo URL                                    |
| sw_frontend       | TEXT    | Frontend technologies (comma-separated)          |
| sw_backend        | TEXT    | Backend technologies (comma-separated)           |
| sw_arch           | TEXT    | Architecture type (Full Stack, Mobile, etc.)     |
| hw_components     | TEXT    | Hardware components (comma-separated)            |
| hw_category       | TEXT    | Hardware category                                |
| hw_microcontroller| TEXT    | Microcontroller / board used                     |
| hw_power_source   | TEXT    | Power source                                     |
| hw_prototype      | TEXT    | Prototype status                                 |

> **Auto-migration:** `init_db()` uses `PRAGMA table_info` to detect and `ALTER TABLE` for any missing columns. This means the app safely upgrades old databases without data loss.

---

## 6. Application Routes

### Public Routes

| Route     | Method   | Description                        |
|-----------|----------|------------------------------------|
| `/`       | GET      | Landing page                       |
| `/login`  | GET/POST | Login form + authentication        |
| `/signup` | GET/POST | Registration form                  |
| `/logout` | GET      | Clears session, redirects to home  |

### Student Routes (role: student required)

| Route                      | Method   | Description                              |
|----------------------------|----------|------------------------------------------|
| `/student`                 | GET      | Student dashboard (3 tabs)               |
| `/upload`                  | POST     | Submit a new project with file           |
| `/delete_project/<id>`     | POST     | Delete own project                       |
| `/download/<filename>`     | GET      | Download a project file                  |

### Faculty Routes (role: faculty required)

| Route                  | Method   | Description                                  |
|------------------------|----------|----------------------------------------------|
| `/faculty`             | GET      | Faculty dashboard with filters               |
| `/feedback/<id>`       | POST     | Submit/update review, phase, visit, schedule |
| `/mark_visited/<id>`   | POST     | Quick visited/not-visited toggle             |

### Shared Routes (any logged-in user)

| Route               | Method   | Description                          |
|---------------------|----------|--------------------------------------|
| `/settings`         | GET      | View profile and account details     |
| `/settings/update`  | POST     | Update editable profile fields       |
| `/analytics`        | GET      | Analytics dashboard with 6 charts    |

---

## 7. Features — Detailed Breakdown

### 7.1 Authentication

- Role-based login: students and faculty see different dashboards
- Session stores `user_id`, `role`, `name`
- Duplicate username check on signup
- Flash messages for errors and success

### 7.2 Signup Form

**Common fields:** Full Name, Username, Password, Email, Phone, Role selector

**Student-specific fields:**
- Roll Number
- Department (dropdown — 7 options)
- Year (1st–4th Year)

**Faculty-specific fields:**
- Teacher ID
- Section / Coordinator
- Department

JavaScript toggles student/faculty fields based on role selection.

### 7.3 Student Dashboard

Three tabs:

**Tab 1 — Upload Project**

Basic Info:
- Title, Description, Department, Year, Domain, Project Type

Guide & Phase:
- Guide/Mentor Name
- Current Phase (Phase 1–7 dropdown)

Project Nature toggle (Software / Hardware):

*Software fields:*
- Architecture type (radio: Full Stack, Frontend Only, Backend/API, Mobile, Desktop, AI/ML, CLI)
- Frontend Technologies (checkboxes: React, Angular, Vue, Next.js, Bootstrap, Tailwind, Flutter, etc.)
- Backend Technologies (checkboxes: Django, Flask, Node.js, Spring Boot, FastAPI, etc.)
- Database (dropdown)
- Deployment platform (dropdown)
- GitHub URL
- Live Demo URL

*Hardware fields:*
- Hardware Category (dropdown)
- Microcontroller/Board (dropdown: Arduino, ESP32, Raspberry Pi, etc.)
- Components (checkboxes)
- Power Source (dropdown)
- Prototype Status (dropdown)

File Upload: PDF, DOC, DOCX, PPT, PPTX, ZIP (max 16MB)

**Tab 2 — My Projects**

Each project card shows:
- Title, description, badges (dept, domain, type, nature, year)
- Guide name + visited/not-visited badge
- Next review date (if scheduled)
- Phase progress tracker (7-step visual stepper)
- Tech stack details (frontend, backend, database, GitHub, demo)
- Faculty feedback with star rating
- Upload date, download button, delete button

**Tab 3 — All Projects**

- Filterable by department and project type
- Shows all projects from all students
- Read-only view (no delete)

### 7.4 Faculty Dashboard

**Stats row:** Total projects, Reviewed, Pending, Groups Visited

**Filters:** Department, Type, Nature (SW/HW), Phase, Visit Status, Overall Status

**Each project card shows:**
- Title, description, all badges
- Student name, roll number, year, email
- Guide name
- Phase mini-bar (compact 7-dot progress indicator)
- Visit status badge + next review date pill
- Tech stack chips (color-coded: frontend=blue, backend=green, db=yellow, arch=purple)
- GitHub / Demo links
- Existing feedback with star rating

**Review Panel** (expands on click):

Section 1 — Review Details:
- Feedback textarea
- Rating (1=Poor to 5=Excellent)
- Overall Status (Pending / Reviewed / Approved)

Section 2 — Phase & Visit:
- Update Phase dropdown (all 7 phases)
- Group Visit Status (Visited / Not Visited)

Section 3 — Schedule Next Review:
- Next Review Date (date picker)
- Internal Notes (private, not shown to student)

### 7.5 Project Phases

| Phase | Name                                  |
|-------|---------------------------------------|
| 1     | Project Selection                     |
| 2     | Abstract Submission                   |
| 3     | Implementation Part 1                 |
| 4     | Implementation Part 2                 |
| 5     | Final Project                         |
| 6     | Document & Report Submission          |
| 7     | Paper Submission (IEEE Format)        |

Phases are tracked per project. Faculty can update the phase during review. Students see a visual stepper showing completed (green), current (amber), and upcoming (grey) phases.

### 7.6 Settings Page

- Profile header with avatar (first letter of name), username, role badge, member since date
- Read-only section: Roll/Teacher ID, Year/Section, Department, Username
- Editable section: Full Name, Email, Phone, Department, Year, Section
- Account actions: Create New Account link, Logout button

### 7.7 Analytics Dashboard

Six Chart.js charts:

| Chart                    | Type     | Data                                      |
|--------------------------|----------|-------------------------------------------|
| Projects per Domain      | Bar      | Count of projects grouped by domain       |
| Submission Trend         | Line     | Monthly submission count over time        |
| Average Rating by Domain | Bar      | Mean rating per domain                    |
| Projects per Department  | Bar      | Count grouped by department               |
| Phase Distribution       | Doughnut | How many projects are in each phase       |
| Software vs Hardware     | Pie      | Nature split                              |

KPI cards: Total Projects, Reviewed, Pending, Average Rating, Most Active Domain

---

## 8. Departments Supported

1. Computer Science Engineering
2. Computer Science Engineering (AI & ML)
3. Computer Science Engineering (Data Science)
4. Information Technology
5. Electronics & Communication Engineering
6. Electrical & Electronics Engineering
7. Electronics & Telematics Engineering

---

## 9. Domains Supported

Artificial Intelligence, Machine Learning, Deep Learning, Web Development, Mobile Development, Cloud Computing, Cybersecurity, Internet of Things, Data Science, Blockchain, Embedded Systems, Networking, Robotics, Other

---

## 10. File Upload Details

- Allowed types: `.pdf`, `.doc`, `.docx`, `.ppt`, `.pptx`, `.zip`, `.png`, `.jpg`, `.jpeg`
- Files are saved to the `uploads/` folder
- Filename is sanitized using `werkzeug.utils.secure_filename`
- A unique suffix (`_<user_id>_<timestamp>`) is appended to prevent overwrites
- Files are served via `/download/<filename>` route using `send_from_directory`

---

## 11. Settings Gear Menu (Navbar)

Available on all authenticated pages (student, faculty, settings, analytics):

- ⚙️ Settings & Profile → `/settings`
- ➕ Create New Account → `/signup`
- 🚪 Logout → `/logout`

Clicking outside the dropdown closes it (handled via JS `document.addEventListener('click', ...)`).

---

## 12. Security Notes (for production upgrade)

| Current (Demo)              | Recommended for Production              |
|-----------------------------|-----------------------------------------|
| Plain-text passwords        | Use `werkzeug.security` hash functions  |
| SQLite                      | Migrate to PostgreSQL or MySQL          |
| No file size enforcement    | Add `MAX_CONTENT_LENGTH` in Flask config|
| No CSRF protection          | Use Flask-WTF for CSRF tokens           |
| `debug=True`                | Set `debug=False`, use gunicorn/nginx   |
| No email verification       | Add Flask-Mail for verification         |

---

## 13. Key Constants (app.py)

| Constant       | Purpose                                      |
|----------------|----------------------------------------------|
| `DEPARTMENTS`  | List of 7 department names                   |
| `YEARS`        | 1st Year – 4th Year                          |
| `DOMAINS`      | 14 technical domains                         |
| `PROJECT_TYPES`| Research Project, Regular Project            |
| `PHASES`       | 7 project phases (Phase 1–7)                 |
| `SW_FRONTEND`  | 14 frontend technology options               |
| `SW_BACKEND`   | 16 backend technology options                |
| `SW_DATABASES` | 10 database options                          |
| `HW_COMPONENTS`| 12 hardware component options                |
| `HW_CATEGORIES`| 8 hardware category options                  |

---

## 14. How Auto-Migration Works

On every app start, `init_db()`:
1. Creates tables with `CREATE TABLE IF NOT EXISTS` (safe if already exists)
2. Runs `PRAGMA table_info(users)` and `PRAGMA table_info(projects)` to get existing columns
3. For each expected column not found, runs `ALTER TABLE ... ADD COLUMN ...`

This means you can add new columns to the schema and they'll be added to existing databases automatically without losing any data.

---

## 15. Running in Production (basic)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

Set environment variable for secret key:
```python
app.secret_key = os.environ.get('SECRET_KEY', 'fallback')
```

---

*ThinkHive — Built for real-time college project management.*
