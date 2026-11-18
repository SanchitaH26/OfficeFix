# CLAUDE.md — OfficeFix

## 1. Project objective

Build **OfficeFix — Office Maintenance Request and Management System**, a small internal company application.

Employees can submit office maintenance issues. An administrator can review requests, categorize them, assign maintenance technicians, update their status, and record resolution notes.

Build a working full-stack application, not a static UI prototype.

## 2. Mandatory technology stack

### Frontend
- React
- Vite
- JavaScript (do not introduce TypeScript unless explicitly requested)
- Axios or the native Fetch API for backend communication
- Plain CSS or a lightweight styling approach; avoid adding unnecessary UI frameworks

### Backend
- Python
- FastAPI
- SQLAlchemy 2.x
- Pydantic
- Alembic for database migrations
- Psycopg PostgreSQL driver

### Database
- PostgreSQL for local development
- Keep configuration compatible with Azure Database for PostgreSQL
- Read the database connection string from an environment variable
- Do not hardcode credentials or connection strings

## 3. Repository structure

Keep the repository focused and use this structure unless a genuine implementation need requires a small change:

```text
officefix/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── dependencies.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── requests.py
│   │   │   ├── technicians.py
│   │   │   └── dashboard.py
│   │   └── services/
│   │       ├── __init__.py
│   │       └── maintenance_service.py
│   ├── alembic/
│   │   ├── versions/
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_requests.py
│   │   ├── test_technicians.py
│   │   └── test_dashboard.py
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── styles/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .gitignore
├── CLAUDE.md
└── README.md
```

Do not add Dockerfiles, docker-compose files, Kubernetes, Terraform, CI/CD workflows, cloud infrastructure folders, or other deployment scaffolding unless the user explicitly requests them. Do not create empty folders or placeholder modules that are not used.

## 4. Functional scope

Keep the first version small enough to complete and test in approximately 3–4 hours.

### Employee request submission
Provide a form with:
- Employee name and email
- Issue title
- Description
- Category: Electrical, HVAC/AC, Plumbing, Internet/Network, Furniture, Other
- Office location or floor
- Priority: Low, Medium, High

For this time-boxed version, employee details may be entered in the form. Do not build full authentication or a complex employee-management module unless explicitly requested.

### Admin request management
The admin interface must:
- Display all maintenance requests.
- View the details of an individual request.
- Filter by status, category, and priority.
- Assign or change the assigned technician.
- Change status between Open, In Progress, and Resolved.
- Add or update resolution notes.
- Record the resolved date when a request becomes Resolved.
- Allow an appropriate edit or delete operation, with confirmation before deletion.

### Technician management
The admin must be able to:
- Create a technician.
- View technicians.
- Edit technician details.
- Mark a technician Available or Unavailable.
- View each technician's active request count.
- Assign only available technicians to new requests.

### Dashboard
Display database-derived values for:
- Total requests
- Open requests
- In-progress requests
- Resolved requests
- High-priority unresolved requests
- Recent requests
- Active workload per technician

Do not hardcode dashboard counts. Calculate them from stored records.

### Business rules
- A newly submitted request starts with status `Open`.
- A request may be unassigned.
- A technician marked unavailable must not be offered for a new assignment.
- A resolved request must have a resolution date.
- If a resolved request is reopened, clear its resolved date unless the application explicitly stores a separate resolution history.
- Validate required fields and reject invalid input with useful error messages.
- Do not allow invalid status, priority, or category values.
- Prevent accidental deletion through a frontend confirmation.

Avoid adding email, SMS, AI, file uploads, maps, complex role-based access, or external integrations in the first version.

## 5. Database design

Use SQLAlchemy models and PostgreSQL tables.

At minimum, create:

### MaintenanceRequest
- id (primary key)
- employee_name
- employee_email
- title
- description
- category
- location
- priority
- status
- technician_id (nullable foreign key)
- resolution_notes (nullable)
- created_at
- updated_at
- resolved_at (nullable)

### Technician
- id (primary key)
- name
- email
- specialization
- availability
- created_at

Use appropriate SQL types, constraints, indexes where useful, and a real foreign-key relationship. Use UTC-aware timestamps where practical.

Keep the schema simple. Do not introduce extra tables unless they are needed for a required feature.

## 6. Database configuration and migrations — critical

Alembic migrations are mandatory. Do not use `Base.metadata.create_all()` as the application schema setup mechanism.

Requirements:
1. Configure Alembic to use the same SQLAlchemy metadata as the application models.
2. Load the database URL securely from the backend environment.
3. Ensure Alembic can detect all model metadata.
4. Generate an initial migration containing all required tables, columns, constraints, indexes, and foreign keys.
5. Inspect the generated migration manually for correctness. Do not blindly trust autogenerated output.
6. Test the migration against a clean local PostgreSQL database.
7. Verify `alembic upgrade head` succeeds.
8. Verify `alembic current` reports the expected revision.
9. Verify `alembic downgrade -1` and re-upgrade work when practical and safe.
10. Commit and push all required migration files under `backend/alembic/versions/`.
11. Never commit database passwords, `.env` files, or secrets.
12. Do not delete or rewrite an already-applied migration merely to hide a schema problem. Create a new corrective migration instead.

The repository must contain the actual migration revision file(s), not just Alembic configuration.

## 7. API design and slash correctness — critical

Use one consistent API prefix: `/api/v1`.

Use route paths without trailing slashes, for example:
- `GET /api/v1/requests`
- `POST /api/v1/requests`
- `GET /api/v1/requests/{request_id}`
- `PATCH /api/v1/requests/{request_id}`
- `DELETE /api/v1/requests/{request_id}`
- `GET /api/v1/technicians`
- `POST /api/v1/technicians`
- `PATCH /api/v1/technicians/{technician_id}`
- `GET /api/v1/dashboard/stats`

Rules:
- Do not create paths containing `//`.
- Do not accidentally combine a prefix ending in `/` with a route beginning with an extra `/`.
- Keep the frontend API base URL and endpoint paths consistent.
- Normalize the API base URL in one central frontend API module by removing trailing slashes before appending endpoint paths.
- Use endpoint paths with exactly one leading slash.
- Do not scatter hardcoded API URLs throughout React components.
- Do not rely on redirects to conceal incorrect route construction.
- Test actual frontend network requests and backend route registration.
- Confirm that OpenAPI/Swagger lists the intended paths without duplicate slashes.

Use a configurable frontend environment variable such as `VITE_API_BASE_URL`, and a configurable backend CORS origin. Keep local defaults documented in `.env.example` or the README.

## 8. Backend quality requirements

- Keep route handlers small; place reusable business logic in the service layer when useful.
- Use Pydantic request and response schemas.
- Use SQLAlchemy sessions with correct cleanup.
- Return appropriate HTTP status codes.
- Handle missing records with 404 responses.
- Handle validation and database errors safely.
- Do not expose stack traces, secrets, or database credentials in API responses.
- Add a health endpoint such as `GET /health`.
- Ensure the app starts using the documented command.
- Do not add unnecessary abstraction or over-engineer this small project.

## 9. Frontend quality requirements

Build a clean, professional internal company dashboard:
- Sidebar navigation
- Dashboard summary cards
- Requests table with readable status and priority badges
- Request submission form
- Request detail/edit view or modal
- Technician management page
- Loading, empty, success, and error states
- Form validation and user-friendly messages
- Confirmation before destructive actions
- Responsive layout for normal laptop and smaller screens

All displayed records and counts must come from the backend. Do not leave fake hardcoded rows in the final integrated application. Seed data may be added through a deliberate, documented development-only method if useful.

## 10. Local development and testing

The application must be tested locally before Harbour testing.

Backend:
1. Create and activate a Python virtual environment.
2. Install `backend/requirements.txt`.
3. Create a local PostgreSQL database.
4. Configure `backend/.env` using `backend/.env.example` as a guide.
5. Run Alembic migrations against the local database.
6. Start FastAPI.
7. Test health, request, technician, and dashboard endpoints.
8. Run the automated tests.

Frontend:
1. Install dependencies using the package manager and lockfile selected for the project.
2. Configure the local API base URL.
3. Start Vite.
4. Verify the pages load.
5. Submit a request through the UI.
6. Confirm it is persisted in PostgreSQL and appears in the admin request list.
7. Assign a technician and update the status.
8. Confirm dashboard counts change based on the database.
9. Check browser console and network requests for errors.

Do not claim the project works unless these checks have actually been run. Report any checks that could not be completed.

## 11. Git requirements

- Keep `.gitignore` appropriate for Python, Node, virtual environments, build output, local environment files, caches, and IDE files.
- Commit source code, dependency manifests, README, Alembic configuration, and migration revision files.
- Do not commit `.env`, secrets, virtual environments, `node_modules`, build output, or local database files.
- Before finishing, inspect `git status`.
- Verify migration files are tracked using `git ls-files backend/alembic`.
- Do not claim changes have been pushed unless a successful push has actually occurred.
- If Git credentials, remote configuration, or permissions prevent a push, explain the exact issue and provide the command the user needs to run.

## 12. Harbour validation

After local testing passes, prepare the application for the user's Harbour environment.

- Inspect the actual Harbour project instructions, configuration, logs, and expected start commands available in the repository or provided by the user.
- Do not invent Harbour-specific commands, environment variable names, deployment conventions, or infrastructure.
- Keep local and Harbour configuration separate through environment variables.
- Ensure the Harbour environment points to its intended PostgreSQL database.
- Apply committed Alembic migrations in Harbour using the approved process for that environment.
- Verify backend startup, frontend access, database connectivity, and the main request-submission-to-resolution workflow.
- Check Harbour logs and browser network requests for errors.
- Confirm all API URLs have exactly one slash between the host/base path and endpoint.
- Report the actual Harbour test results and any blockers.

Do not run destructive migrations, reset a shared database, or overwrite shared data without explicit authorization.

## 13. Scope note: “2 applications each”

The project brief mentions the phrase “2 applications each,” but its exact meaning is not yet defined. Do not assume this means two separate products, two deployments, or two user interfaces. Build the single OfficeFix application described here and ask the user to clarify this requirement before implementing any additional application or instance.

## 14. Working method for Claude Code

Work in small, verifiable stages:

1. Inspect the current repository and existing files before changing anything.
2. Confirm the project root and avoid overwriting unrelated work.
3. Create the folder structure and minimal configuration.
4. Implement database models and Alembic configuration.
5. Generate and inspect the initial migration.
6. Implement and test backend APIs.
7. Implement the React interface.
8. Connect the frontend to the real backend.
9. Run local migrations, tests, and end-to-end manual checks.
10. Review API paths for double slashes.
11. Review Git tracking, especially migration files.
12. Prepare for Harbour validation only after local checks pass.

Do not generate the entire application in one unverified step. Do not silently skip failed tests. Do not replace a broken implementation with mock data just to make the UI appear functional.

At the end, provide:
- Final folder structure
- Commands to run backend and frontend locally
- Required environment variables (never their secret values)
- Migration commands
- Tests executed and their results
- Git files that must be committed
- Harbour-specific steps that remain, based on actual available instructions
- Any unresolved requirements or blockers

## 15. Definition of done

The first version is complete only when:
- Employee can submit a maintenance request.
- Admin can list, view, filter, update, assign, and resolve requests.
- Admin can manage technicians.
- Dashboard values reflect PostgreSQL data.
- Alembic migration files exist and work on a clean local database.
- Migration files are included in Git.
- Frontend and backend communicate successfully.
- No malformed API URLs or accidental double slashes are present.
- The documented local test workflow passes, with any exceptions clearly reported.
- Harbour validation is performed and reported when Harbour access and instructions are available.
