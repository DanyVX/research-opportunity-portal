# University Research Opportunity Portal

CN Assignment 1 - Danial Hassan, 24P-0747, BCS-5B.

Create, list, view, edit, close/reopen and delete research opportunities. MySQL stores all records; the frontend communicates with Flask's REST API. All matching records are displayed without a ten-item limit. No frontend data is hard-coded.

**GitHub Repository:**https://github.com/DanyVX/research-opportunity-portal

**Before submission:** add your real GitHub link, run the Postman collection yourself and record a demonstration of at most one minute. Understand/adapt the code to your own work; the assignment prohibits copied/plagiarized submissions.

## Requirements

Python 3.10+, MySQL 8.0+, Postman and Git. This is a local faculty management app without authentication, intended for localhost use.

## Windows setup (PowerShell)

Open a terminal in the extracted project folder containing this README:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open MySQL Workbench, connect as administrator, open `database/schema.sql` and execute the whole script. Then run the following SQL using your own password (never commit it):

```sql
CREATE USER 'portal_user'@'localhost' IDENTIFIED BY 'choose_your_own_local_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON research_portal.* TO 'portal_user'@'localhost';
```

If the user already exists, skip CREATE USER or use ALTER USER. Edit `.env` and set DB_PASSWORD to that password. The other defaults are host 127.0.0.1, port 3306, database research_portal and user portal_user. Set your actual MySQL port if different.

```powershell
.\.venv\Scripts\python.exe -m backend.app
```

Open **http://127.0.0.1:5000**. Keep the terminal open. The initial empty list is expected. Flask serves the frontend too: no npm or separate frontend server is needed.

## macOS/Linux

Set up MySQL as above, then:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
# Edit .env with your local MySQL credentials.
.venv/bin/python -m backend.app
```

## Using the app

New opportunity opens the form. Every field is required. Details fetches a complete record. Edit changes any field. Close/Reopen updates status. Delete asks for confirmation. Search and status filters apply to the complete database result.

Available positions must be a positive integer. Deadlines are YYYY-MM-DD calendar dates; historical dates are allowed for maintaining existing records. Status is explicit and does not automatically change when a deadline passes. IDs are database-generated. PUT requires all nine editable fields, not ID.

## API

| Method | Endpoint | Success |
|---|---|---|
| POST | /api/opportunities | 201, created object and Location header |
| GET | /api/opportunities | 200, all objects |
| GET | /api/opportunities/:id | 200, one complete object |
| PUT | /api/opportunities/:id | 200, updated object |
| DELETE | /api/opportunities/:id | 200, deletion message |

Invalid/missing data or malformed JSON: 400. Absent record: 404. Unexpected database/server failure: 500. Oversized body: 413. Unsupported method: 405. Errors return an `error` message, with `fields` for validation errors.

Example POST or PUT body:

```json
{
  "title": "Computer Vision Research Assistant",
  "description": "Assist with image classification experiments.",
  "research_area": "Computer Vision",
  "faculty_name": "Dr. Example",
  "department": "Computer Science",
  "required_skills": "Python, linear algebra",
  "available_positions": 2,
  "application_deadline": "2027-01-31",
  "status": "Open"
}
```

## Postman testing

Import `postman/research-portal.postman_collection.json`. Start the app. Run requests in numbered order or use Collection Runner. `base_url` defaults to http://127.0.0.1:5000. Create requests capture IDs automatically. Assertions check status codes and relevant values.

The sequence creates three records, retrieves all, retrieves one, updates, closes, deletes, gets the deleted record for 404 and sends missing data for 400. It deletes only the first created record; the other two remain. Repeated runs add records. Python tests supplement, rather than replace, your required Postman demonstration.

## Automated tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Validation tests require no database. Integration tests skip unless TEST_DB_NAME is set. For real tests, create a **dedicated** database named research_portal_test and grant your test user SELECT, INSERT, UPDATE, DELETE and CREATE on it. These tests delete all rows of its opportunities table before and after testing. Never point them at a real inventory/data database.

```powershell
$env:TEST_DB_NAME="research_portal_test"
$env:DB_USER="your_test_user"
$env:DB_PASSWORD="your_test_password"
.\.venv\Scripts\python.exe -m pytest -q
```

On Linux use `TEST_DB_NAME=research_portal_test DB_USER=your_test_user DB_PASSWORD=your_test_password .venv/bin/python -m pytest -q`. See docs/VALIDATION.md for actual build checks.

## Files

- backend/app.py: Flask routes, validation and SQL transactions.
- frontend/: HTML, CSS and JavaScript.
- database/schema.sql: MySQL setup.
- postman/: importable collection.
- tests/: validation and real database checks.
- docs/: explanation, demo checklist and validation evidence.

## Troubleshooting

**Database 500:** verify MySQL is running, schema is imported, and .env credentials/port/user permissions match. Technical details appear only in server logs. **Access denied:** test the same account in Workbench and check host grants. **Port occupied:** change PORT in .env, restart and update Postman base_url. **Module missing:** install requirements with the same Python executable you use to run. **Empty initial list:** create records; there is no automatic seed.

## References

Instructor's Assignment_1.pdf; Flask official documentation https://flask.palletsprojects.com/en/stable/ ; PyMySQL documentation https://pymysql.readthedocs.io/en/latest/ .
