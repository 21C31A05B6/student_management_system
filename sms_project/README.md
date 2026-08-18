# Student Management System

A full Student Management System built with **Django (Python)**, **Bootstrap 5** (HTML/CSS/JS
frontend), and support for **PostgreSQL** in production (SQLite by default for instant local
testing). Built following the phased module plan:

- **Module 1** — Authentication (Admin / Teacher / Student roles)
- **Module 2** — Student Management (CRUD, profile, photo, status)
- **Module 3** — Teacher Management (CRUD, subjects taught)
- **Module 4** — Department Management
- **Module 5** — Course / Section (Class) Management + Attendance Management
- **Module 6** — Subject Management + Exam / Marks Management (auto grade & percentage)
- **Module 7** — Fees Management (payments, receipts, due tracking)
- **Module 8** — Timetable Management (weekly grid, per role)
- **Module 9** — Dashboards (different view for Admin / Teacher / Student)

## Project layout

```
sms_project/
├── accounts/       # Custom User model (roles), login/logout/profile
├── academics/      # Department, Course, Section, Subject
├── students/       # Student model + CRUD
├── teachers/       # Teacher model + CRUD
├── attendance/     # Attendance marking & viewing
├── exams/          # Exams + Marks entry, auto grade/percentage
├── fees/           # Fee records + payments
├── timetable/      # Weekly timetable per section
├── dashboard/       # Role-based home dashboards
│   └── management/commands/seed_demo_data.py   # demo data seeder
├── templates/       # All Bootstrap HTML templates (base.html + per-app folders)
├── static/css/sms.css
└── sms_project/settings.py, urls.py
```

## 1. Quick start (SQLite — zero setup)

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cd sms_project
python manage.py migrate
python manage.py seed_demo_data   # creates demo admin/teacher/student + sample data
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** and log in with:

| Role    | Username  | Password    |
|---------|-----------|-------------|
| Admin   | admin     | admin123    |
| Teacher | rprasad   | teacher123  |
| Student | rahul     | student123  |

(Also creates a second teacher `spatel` and students `prashanth`, `arun`, `suresh`, `priya`,
all with password `student123` / `teacher123`.)

To create your own superuser instead: `python manage.py createsuperuser`, then use Django admin
at `/admin/` to add departments, courses, subjects, teachers, and students — or use the app's own
admin pages (Departments, Courses, Subjects, Students, Teachers in the sidebar).

## 2. Switching to PostgreSQL

1. Create a database and user in PostgreSQL:
   ```sql
   CREATE DATABASE sms_db;
   CREATE USER sms_user WITH PASSWORD 'sms_password';
   GRANT ALL PRIVILEGES ON DATABASE sms_db TO sms_user;
   ```
2. Set environment variables before running Django (or put them in a `.env` file and load them,
   e.g. with `python-dotenv` or `django-environ`):
   ```bash
   export DJANGO_DB_ENGINE=postgres
   export DJANGO_DB_NAME=sms_db
   export DJANGO_DB_USER=sms_user
   export DJANGO_DB_PASSWORD=sms_password
   export DJANGO_DB_HOST=localhost
   export DJANGO_DB_PORT=5432
   ```
3. Run migrations against Postgres and seed data as usual:
   ```bash
   python manage.py migrate
   python manage.py seed_demo_data
   python manage.py runserver
   ```

`psycopg2-binary` is already in `requirements.txt`, so no extra driver install is needed.

## 3. Role-based access

- **Admin**: full access — manage students, teachers, departments, courses, subjects, exams,
  fees, timetable; views all dashboards and reports.
- **Teacher**: mark attendance and enter marks for their assigned subjects/sections; view
  students and timetable.
- **Student**: view own profile, attendance %, marks/grades, fee status, and timetable — no
  edit access anywhere (mirrors FR-01–FR-08 and the non-functional requirement that students
  cannot modify their own marks).
- **Parent**: view-only portal showing their linked children's profile, attendance, marks, and
  fee status (via the `parents` app).

## 4. Advanced features (all built in)

| Feature | Where |
|---|---|
| Email notifications | `notifications` app — console backend by default; set SMTP env vars to go live |
| SMS notifications | `notifications` app — logged/console by default; set `SMS_BACKEND=twilio` + Twilio env vars to go live |
| PDF report cards | `reports` app — `/reports/report-card/<student_id>/<exam_id>/` |
| Student ID cards (PDF) | `reports` app — `/reports/id-card/<student_id>/` |
| Performance charts | Chart.js graphs on the Admin dashboard (dept. distribution, attendance trend) and Student dashboard (marks by subject) |
| Announcements | `announcements` app — pinned, audience-targeted (all/teachers/students) |
| Academic calendar | `calendarapp` app — holidays, exams, events, deadlines |
| Assignment management | `assignments` app — teachers post, students submit files, teachers grade |
| Library management | `library` app — book catalog (title/author/isbn/quantity), issue/return tracking. Admin: full catalog CRUD. Teacher: view catalog + issue/return books (recorded as "issued by"). Student: read-only "My Books" view of their own borrowing history, due dates, and overdue status. Fully linked to the real `students.Student` and `teachers.Teacher` models — no separate library-only student records. |
| Transport management | `transport` app — routes, driver info, student assignment |
| Hostel management | `hostel` app — rooms, allocations, vacate flow |
| Parent portal | `parents` app — new `PARENT` role, linked to one or more students, read-only view |
| QR-code attendance | `students.qr_token` (UUID) + `/attendance/qr-scan/` — teacher scans/types a token to mark present instantly; QR image at `/reports/qr/<student_id>/` |
| Student ID card generation | Same as "ID cards" above |
| Audit logs | `auditlog` app — middleware logs every POST/PUT/PATCH/DELETE by an authenticated user; view at `/audit-logs/` |
| Backup / restore | `python manage.py backup_db` and `python manage.py restore_db <file>` |
| API integration | Full Django REST Framework API at `/api/` (students, teachers, attendance, exams, marks, fees, academics), token auth at `/api/token/` |

Notes:
- Email/SMS have no real external provider wired up by default (that requires a paid account).
  Every message is still logged to the `Notification` model and visible at `/notifications/`, so
  the feature is fully testable without credentials. See `settings.py` for the env vars to go live.
- The design uses a glassmorphism theme (frosted-glass cards, animated gradient blobs, hover/­fade
  animations) defined in `static/css/sms.css`.

## 5. Production notes

Before deploying for real use:
- Set `DJANGO_SECRET_KEY` to a new random value and `DJANGO_DEBUG=False`.
- Set `DJANGO_ALLOWED_HOSTS` to your real domain(s).
- Run `python manage.py collectstatic` and serve `staticfiles/` via your web server / CDN.
- Put uploaded photos (`media/`) behind proper storage (e.g. S3) rather than local disk.
- Put the app behind Gunicorn/uWSGI + Nginx (not `runserver`).

## 6. Fixes from the code review (this build)

Every issue from the latest security/quality review has been addressed:

**Correctness & security**
- Marks are validated at the model level: `0 ≤ marks_obtained ≤ max_marks`, enforced in `Mark.clean()` and re-checked in the API serializer (can't be bypassed by going around the HTML form or hitting the API directly).
- API permissions now properly separate read from write per role: Admin gets full CRUD; Teacher gets GET/POST/PATCH (no PUT, no DELETE) on attendance and marks; Student and Parent are **read-only everywhere**, including on their own records — filtering the queryset to "your own rows" was not sufficient on its own, since a `ModelViewSet` still exposes PATCH/DELETE by default.
- **Every delete view project-wide** (16 of them) now shows a confirmation page on GET and only deletes on POST — nothing is destroyed by a bare link click or a crawler following a GET link anymore.
- Deleting or editing a fee `Payment` now correctly recalculates `FeeRecord.paid_amount` from the remaining payments (previously this could go stale).
- Hostel room capacity is enforced server-side (`HostelAllocation.clean()`), and a student can no longer be double-booked into two rooms at once. Allocation is now a normal `ForeignKey` (not `OneToOne`) so a student's room history survives across moves.
- Timetable entries validate for section/teacher/room conflicts on save, and gained a `room_number` field.
- The Exam/Marks relationship was restructured: `Exam → ExamSubject → Marks`, so different subjects can have different maximum marks within the same exam.

**New features**
- GPA (per exam) and CGPA (overall) calculation, shown on the student's "My Marks" page, their profile, and on generated report cards.
- Library fines: ₹5/day past the due date, shown to admins, teachers, and the student who owes it, with a "mark paid" action.
- Student search/filter by name, ID, and department (already present, verified working).

**Testing & hygiene**
- Test suite grew from 8 to **62 tests**, covering authentication, role restrictions, student CRUD, marks validation, GPA/CGPA, hostel capacity, timetable conflicts, library fines, and — critically — API write-permission boundaries (a student cannot PATCH or DELETE their own marks/attendance/fees via the API; a teacher cannot DELETE marks at all).
- Removed the stray `{notifications,announcements,...}` directory left over from an unexpanded shell brace-expansion, and all `__pycache__`/`.pyc` files.

**Not yet done** (flagged as Priority 2/3 in the review, lower urgency than the above):
academic history tracking, attendance sessions, curriculum management layer, Excel export, and a dedicated performance-analytics dashboard. The codebase is structured (one Django app per concern) so any of these can be added without touching what's already here.

