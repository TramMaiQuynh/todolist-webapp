# To-do List Web App

A task management web app built with Django REST Framework, React, and PostgreSQL.

## Features

- User accounts with registration, login, logout, and password change
- Tasks with status, priority, due date, estimated time, and an "important" flag
- Categories, tags, and subtasks
- Recurring tasks (daily, weekly, monthly, or yearly)
- Archive and restore, plus bulk actions on multiple tasks
- Statistics: overview, deadlines, breakdowns, trends, performance, and workload

## Tech stack

| Layer | Technology |
| --- | --- |
| Backend | Python, Django, Django REST Framework, Gunicorn |
| Frontend | React, Vite |
| Database | PostgreSQL (SQLite for quick local development) |
| Deployment | Docker Compose, nginx |

## Requirements

- Docker with Docker Compose
- For local development: Python 3.11+ and Node.js 22+. PostgreSQL is optional, because SQLite also works.

## Getting started

1. Create the environment file:

   ```sh
   cp .env.example .env
   ```

2. Set `DJANGO_SECRET_KEY` and `POSTGRES_PASSWORD` in `.env`. You can generate a secret key with:

   ```sh
   python -c "import secrets; print(secrets.token_urlsafe(64))"
   ```

3. Start the app:

   ```sh
   docker compose up --build
   ```

Open <http://localhost:8080>. The API is available at `/api/v1/` on the same origin, and the health check is at `/healthz/`.

Compose waits for PostgreSQL, runs migrations, and collects static files before it starts Gunicorn and nginx.

To stop the app, run `docker compose down`. Your data stays in the `postgres_data` volume. To delete the data as well, run `docker compose down -v`.

## Local development

Create `.env` from `.env.example` first.

**Backend:**

```sh
python -m venv backend/.venv
source backend/.venv/bin/activate      # Windows: backend\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd backend
python manage.py migrate
python manage.py runserver
```

If PostgreSQL runs on your machine, set `POSTGRES_HOST=localhost` in `.env`. To use SQLite instead, remove `POSTGRES_DB` from `.env`.

**Frontend** (in a second terminal):

```sh
cd frontend/todo_frontend
npm ci
npm start
```

The dev server runs at <http://localhost:5173> and forwards API requests to `http://127.0.0.1:8000`. To use an API on a different origin, set `VITE_API_URL` before you build.

## Configuration

Settings are read from environment variables or from a `.env` file in the project root or in `backend/`. See [.env.example](.env.example) for sample values.

| Variable | Purpose |
| --- | --- |
| `DJANGO_SECRET_KEY` | Django secret key. Required when `DJANGO_DEBUG=false`. |
| `DJANGO_DEBUG` | Debug mode. Off by default. |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list of allowed hostnames |
| `TIME_ZONE` | Time zone. Default: `Asia/Ho_Chi_Minh` |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Database credentials |
| `POSTGRES_HOST`, `POSTGRES_PORT` | Database address. Compose sets the host to `db`. |
| `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` | Comma-separated lists of allowed origins |
| `AUTH_TOKEN_TTL_DAYS` | Number of days a login token stays valid |
| `DJANGO_TEST_SQLITE` | Run tests on a separate SQLite database |

## Deployment

Compose serves plain HTTP, which is fine for local use. Before you put the app on the internet:

1. Place nginx behind a reverse proxy that handles TLS, and make the proxy set the `X-Forwarded-Proto` header.
2. Use a random secret key and set your real hostname in `DJANGO_ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`.
3. Once HTTPS works, set `DJANGO_SSL_REDIRECT=true`, `DJANGO_SECURE_COOKIES=true`, and a value for `DJANGO_HSTS_SECONDS`.
4. Set `DJANGO_HSTS_INCLUDE_SUBDOMAINS=true` and `DJANGO_HSTS_PRELOAD=true` only if every subdomain also uses HTTPS.

When you run locally over HTTP, `manage.py check --deploy` shows HTTPS and HSTS warnings. These warnings are expected.

## Testing

Backend tests (from `backend/`):

```sh
python manage.py test
```

By default, the tests use a separate SQLite database so they run quickly. To run them against PostgreSQL:

```sh
docker compose run --rm backend python manage.py test
```

Frontend tests and build:

```sh
cd frontend/todo_frontend
npm ci
npm test
npm run build
```

## Project structure

```text
backend/
  accounts/       Registration, login, and token authentication
  tasks/          Tasks, categories, tags, recurrence, and statistics
  todo_backend/   Django settings and URLs
frontend/
  todo_frontend/  React app
docker-compose.yml
```
