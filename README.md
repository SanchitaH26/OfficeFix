# OfficeFix: Office Maintenance Management System

OfficeFix is an internal web application for reporting and managing office maintenance issues. Employees submit requests. Administrators review requests, assign technicians, track status, and record how each issue was resolved.

## Features

- **Dashboard:** total, open, in-progress, and resolved request counts, high-priority unresolved requests, recently submitted requests, and per-technician workload. All figures come from PostgreSQL.
- **Submit request:** employee name and email, issue title, description, category, office location or floor, and priority, with field-level validation.
- **Maintenance requests:** searchable table with status, priority, and category filters. Admins can view and edit a request, assign or unassign a technician, change status, record resolution notes, and delete a request after confirmation.
- **Technicians:** add and edit technicians, mark them Available or Unavailable, and view each technician's active request count. Only Available technicians can be newly assigned.

Business rules enforced by the backend:
- New requests start as `Open` and may be unassigned.
- Marking a request `Resolved` records a resolution date. Reopening it clears that date.
- An Unavailable technician cannot be newly assigned. Existing assignments are kept.
- Category, priority, status, and availability accept only the allowed values.

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite 8, Axios, plain CSS |
| Backend | Python, FastAPI, Pydantic 2, SQLAlchemy 2.x |
| Database | PostgreSQL 17 (local), compatible with Azure Database for PostgreSQL |
| Migrations | Alembic |
| Driver | Psycopg 3 |
| Tests | pytest, FastAPI TestClient |

## Folder structure

```
officefix/
├── README.md
├── CLAUDE.md
├── .gitignore
├── backend/
│   ├── app/
│   │   ├── main.py              FastAPI app, CORS, error handlers, /health
│   │   ├── database.py          settings (from .env), engine, session factory
│   │   ├── dependencies.py      database session dependency
│   │   ├── models.py            SQLAlchemy models: Technician, MaintenanceRequest
│   │   ├── schemas.py           Pydantic request and response schemas
│   │   ├── routers/             requests.py, technicians.py, dashboard.py
│   │   └── services/            maintenance_service.py (business logic)
│   ├── alembic/
│   │   ├── env.py               reads DATABASE_URL, uses the app's metadata
│   │   ├── script.py.mako
│   │   └── versions/            migration revision files (commit these)
│   ├── tests/                   pytest suite (conftest.py, test_*.py)
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html
    ├── package.json
    ├── package-lock.json
    ├── vite.config.js
    ├── .env.example
    └── src/
        ├── main.jsx, App.jsx
        ├── components/          layout, modals, badges, state messages
        ├── pages/               Dashboard, Requests, SubmitRequest, Technicians
        ├── services/            api.js (all HTTP calls), format.js
        └── styles/global.css
```

## Prerequisites

- **Python 3.14** (the version this project was built and tested with). Other 3.x versions are not verified.
- **Node.js** with npm (the project was built and tested with the version installed on the development machine; see `node -v`).
- **PostgreSQL 17**, running locally. Tested with 17.12. Other versions are not verified. Install from https://www.postgresql.org/download/. Include the **Command Line Tools** option, which provides `psql`.
- A PostgreSQL superuser password, set during installation. Used only for the one-time database setup below.

## 1. PostgreSQL setup

Create one application role and two databases: `officefix` for the running application and `officefix_test` for the test suite. Run these as the `postgres` superuser. On Windows, `psql` is at `C:\Program Files\PostgreSQL\17\bin\psql.exe`.

```sql
CREATE ROLE officefix_app LOGIN PASSWORD '<choose-a-strong-password>';
CREATE DATABASE officefix OWNER officefix_app;
CREATE DATABASE officefix_test OWNER officefix_app;
```

Command line example:

```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost -p 5432 -c "CREATE ROLE officefix_app LOGIN PASSWORD '<choose-a-strong-password>';"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost -p 5432 -c "CREATE DATABASE officefix OWNER officefix_app;"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost -p 5432 -c "CREATE DATABASE officefix_test OWNER officefix_app;"
```

The role owns both databases, so it can create tables and run migrations without superuser rights. This matches how Azure Database for PostgreSQL is typically set up.

## 2. Backend setup

Run all commands from the `backend/` folder.

**Create and activate a virtual environment:**

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux, use `python3 -m venv .venv` and `source .venv/bin/activate`.

**Install dependencies:**

```powershell
pip install -r requirements.txt
```

**Create the environment file.** Copy `backend/.env.example` to `backend/.env` and replace the placeholders with the role password you chose above:

```
DATABASE_URL=postgresql+psycopg://officefix_app:<password>@localhost:5432/officefix
TEST_DATABASE_URL=postgresql+psycopg://officefix_app:<password>@localhost:5432/officefix_test
CORS_ORIGINS=http://localhost:5173
```

`backend/.env` contains a password and is listed in `.gitignore`. Do not commit it.

**Run the database migrations:**

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Check the result:

```powershell
.\.venv\Scripts\python.exe -m alembic current
```

It should print `00cbed0b13c5 (head)`.

## Alembic migration commands

Run from `backend/`.

| Command | Purpose |
|---|---|
| `alembic upgrade head` | Apply all migrations (use after pulling new code) |
| `alembic current` | Show the revision the database is at |
| `alembic history` | List all revisions |
| `alembic downgrade -1` | Undo the most recent migration |
| `alembic check` | Confirm the models and the database schema match (no drift) |
| `alembic revision --autogenerate -m "description"` | Generate a new migration after changing `app/models.py` |

Schema changes are made only through migrations. The application does not call `create_all()`. Review every autogenerated migration before applying it.

## 3. Run the backend

From `backend/`, with the virtual environment active:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8001 --reload
```

The API runs at **http://localhost:8001**.

- Health check: `GET http://localhost:8001/health`. Returns `{"status":"ok","database":"ok"}` when PostgreSQL is reachable.
- API documentation (Swagger UI): **http://localhost:8001/docs**
- OpenAPI schema: http://localhost:8001/openapi.json

All API routes use the `/api/v1` prefix and have no trailing slash, for example `/api/v1/requests`. A trailing slash returns 404.

## 4. Frontend setup

Run from `frontend/`:

```powershell
cd frontend
npm install
```

**Create the environment file (optional).** The default API address is already `http://localhost:8001`. To set it explicitly, copy `frontend/.env.example` to `frontend/.env`:

```
VITE_API_BASE_URL=http://localhost:8001
```

Set the base URL only. Do not add a trailing slash or `/api/v1`, since the app adds those.

**Start the development server:**

```powershell
npm run dev
```

The application opens at **http://localhost:5173**. It must run on this port, because the backend's `CORS_ORIGINS` allows only that origin.

**Build for production:**

```powershell
npm run build
```

The output goes to `frontend/dist/`. Preview it with `npm run preview`.

## 5. Running the application

Start both servers in two terminals:

1. Backend: `backend\` folder, `.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8001 --reload`
2. Frontend: `frontend\` folder, `npm run dev`

Then open http://localhost:5173.

## 6. Running the backend tests

The test suite runs against `officefix_test`, using `TEST_DATABASE_URL`. It refuses to run against any database whose name does not end in `_test`. Before each test it empties the `technicians` and `maintenance_requests` tables in that database. Do not point `TEST_DATABASE_URL` at `officefix`.

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

The suite contains 36 tests in `test_requests.py`, `test_technicians.py`, and `test_dashboard.py`.

## Environment variables

| Variable | Where | Purpose | Example (placeholder) |
|---|---|---|---|
| `DATABASE_URL` | `backend/.env` | Application database URL (SQLAlchemy, psycopg driver) | `postgresql+psycopg://officefix_app:<password>@localhost:5432/officefix` |
| `TEST_DATABASE_URL` | `backend/.env` | Test database URL. Must end in `_test` | `postgresql+psycopg://officefix_app:<password>@localhost:5432/officefix_test` |
| `CORS_ORIGINS` | `backend/.env` | Comma-separated allowed frontend origins | `http://localhost:5173` |
| `VITE_API_BASE_URL` | `frontend/.env` | Backend base URL used by the frontend | `http://localhost:8001` |

Never commit `.env` files or passwords. `.gitignore` excludes `.env`, `backend/.env`, and `frontend/.env`. Only the `.env.example` files are committed.

## Deploying to Azure Database for PostgreSQL

Only `DATABASE_URL` changes. Use the server host and an SSL requirement:

```
DATABASE_URL=postgresql+psycopg://<user>:<password>@<server>.postgres.database.azure.com:5432/officefix?sslmode=require
```

Apply migrations with `alembic upgrade head` against that URL. Do this only with the approved process for the target environment.

## Troubleshooting

- **"Cannot reach the OfficeFix server" in the browser:** the backend is not running on port 8001, or `VITE_API_BASE_URL` points elsewhere. Restart the backend and check `http://localhost:8001/health`.
- **Health check returns 503:** PostgreSQL is not running, or `DATABASE_URL` is wrong. Check that the `postgresql-x64-17` service is running.
- **CORS errors in the browser console:** the frontend is not on port 5173. Start it with `npm run dev`, or add its origin to `CORS_ORIGINS` and restart the backend.
- **`alembic current` shows nothing:** migrations have not been applied. Run `alembic upgrade head`.
- **Frontend requests return 404:** check that the path has no trailing slash and that the base URL has no `/api/v1` suffix.
