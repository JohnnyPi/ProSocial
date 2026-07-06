# Prosocial Platform

A secure, prosocial sharing site built as a Django modular monolith.

Phase 0 delivers the **Secure Social Core**: accounts, profiles, text and image posts, a paginated dashboard feed, activity events, and a production-ready project skeleton.

## Stack

- Python 3.12+, Django 5.1+
- PostgreSQL
- Django templates + HTMX
- Pillow for image processing
- Docker Compose for local development

## Quick start (Docker)

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. Copy environment variables:

   ```bash
   cd prosocial_platform
   cp .env.example .env
   ```

3. Start the stack:

   ```bash
   docker compose up --build
   ```

4. Open [http://localhost:8000](http://localhost:8000).

5. Create a superuser (in another terminal):

   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

## Local development (without Docker)

Requirements: Python 3.12+, PostgreSQL 16.

```bash
cd prosocial_platform
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e ".[dev]"
cp .env.example .env          # set POSTGRES_HOST=localhost
python manage.py migrate
python manage.py runserver
```

## Useful commands

```bash
python manage.py migrate
python manage.py createsuperuser
pytest
ruff check .
python manage.py check --deploy --settings=config.settings.production
```

## Phase 0 routes

| Route | Purpose |
| --- | --- |
| `/health/` | Health check |
| `/accounts/register/` | Registration |
| `/accounts/login/` | Login |
| `/accounts/logout/` | Logout |
| `/accounts/password-change/` | Change password |
| `/accounts/password-reset/` | Reset password |
| `/profiles/<handle>/` | Public profile |
| `/profiles/edit/` | Edit own profile |
| `/posts/create/` | Create post |
| `/posts/<uuid>/` | Post detail |
| `/dashboard/` | Feed and composer |

## Project layout

```text
prosocial_platform/
├── apps/
│   ├── accounts/      # Custom user model and auth
│   ├── profiles/      # Public profile data
│   ├── posts/         # Posts and image uploads
│   ├── dashboard/     # Feed and composer
│   └── common/        # Shared models, health, events
├── config/settings/   # base, development, testing, production
├── templates/
├── static/
└── deploy/
```

## What is intentionally not built yet

Per the phased plan, Phase 1+ will add replies, gratitude, boundaries, and prosocial actions. There is no trust score, recommendation engine, or public reputation system.

## Documentation

See the repository root docs:

- `SetupAndIntialImplementation.md`
- `Phases0to2.md`
- `ProsocialNetworkDesign.md`
