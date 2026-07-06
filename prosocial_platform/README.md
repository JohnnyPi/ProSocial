# Prosocial Platform

A secure, prosocial sharing site built as a Django modular monolith.

Phase 0 delivers the **Secure Social Core**: accounts, profiles, text and image posts, a paginated dashboard feed, activity events, and a production-ready project skeleton.

Phases 1 and 2 add **interactions** (replies, gratitude, boundaries, reports) and **prosocial actions** (commitments, verification, invitations).

Phases 3–11 add the roadmap features: **knowledge** (clips, collections, vault), **follows**, **guilds**, **messaging**, **trust** (Helper Style, peer ratings, hybrid ETS/PTS), **gamification** (XP, streaks, badges), **AI coach** (sentiment, journal), **moderation** (roles, crisis protocol), **engagement** (challenges, rest mode), **discovery** (most clipped, ripple effect), and **advanced** (donations, skill-sharing, data export).

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

## Test profile management

Load and remove a fixed set of test users, profiles, and posts for local UI and integration testing. Fixture definitions live in `apps/common/test_data/fixtures.py`.

### Commands

**Seed** (idempotent — safe to re-run; skips posts that already exist):

```bash
python manage.py seed_test_data
python manage.py seed_test_data --verbose   # list each profile and post
```

**Purge** (removes all test users and their related data):

```bash
python manage.py purge_test_data --dry-run  # preview counts, no deletes
python manage.py purge_test_data            # delete test data
python manage.py purge_test_data --force    # required when DEBUG=False
```

With Docker:

```bash
docker compose exec web python manage.py seed_test_data
docker compose exec web python manage.py purge_test_data
```

### Logging in as a test user

All seeded accounts share the password **`TestPass123!`**. Log in at `/accounts/login/` with any handle below as the username.

| Handle | Display name | Role |
| --- | --- | --- |
| `test_river` | Test River Chen | Mentor / community helper |
| `test_morgan` | Test Morgan Lee | New member |
| `test_sam` | Test Sam Ortiz | Local action organizer |
| `test_jordan` | Test Jordan Kim | Knowledge sharer |
| `test_casey` | Test Casey Wells | Support / encouragement |

Public profiles are at `/profiles/<handle>/` (for example, `/profiles/test_river/`).

### What gets seeded

Each run creates or updates **5 profiles** and **9 posts**:

- **4 plain posts** — varied `PostKind` and `ThreadType` values (discussion, knowledge share, encouragement).
- **5 action posts** — linked `ActionOpportunity` records (help request/offer, local action, volunteer shift).

Every post body includes the marker `[PROSOCIAL_TEST]` and a unique seed id, for example `[PROSOCIAL_TEST:post=river-welcome]`. Titles, when present, are also tagged.

### Identification and purge safety

Test records are identified by convention, not a database flag:

| Entity | Rule |
| --- | --- |
| Users | Username starts with `test_`; email ends with `@test.prosocial` |
| Profiles | Handle matches username (e.g. `test_river`) |
| Posts | Body or title contains `[PROSOCIAL_TEST]` |

Purge rules:

- Only deletes users matching **both** the username prefix and email domain.
- Never deletes staff or superuser accounts, even if they match the pattern.
- Also removes orphan posts that still contain the test marker.
- Blocked when `DEBUG=False` unless `--force` is passed.

Deleting a test user cascades to their profile, posts, replies, action opportunities, and other related rows.

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
│   ├── dashboard/     # Feed, composer, knowledge hub
│   ├── interactions/  # Replies, thank-yous, boundaries
│   ├── prosocial_actions/
│   ├── knowledge/     # Clips, collections, tags
│   ├── follows/
│   ├── guilds/
│   ├── messaging/
│   ├── trust/
│   ├── gamification/
│   ├── ai_coach/
│   ├── moderation/
│   ├── engagement/
│   ├── discovery/
│   ├── advanced/      # Donations, skills, data export
│   └── common/        # Shared models, health, events, test data seeding
├── config/settings/   # base, development, testing, production
├── templates/
├── static/
└── deploy/
```

## What is intentionally limited

Trust contribution scores are computed internally; public profiles show ranges only when opted in. Donations use a stub flow without live payment processor integration. Semantic search and live collaboration rooms are scaffolded for future work.

## Documentation

See the repository root docs:

- `SetupAndIntialImplementation.md`
- `Phases0to2.md`
- `Phases3to5.md`
- `ProsocialNetworkDesign.md`
