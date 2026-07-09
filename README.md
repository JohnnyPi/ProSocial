# Common Good (Prosocial Platform)

**Common Good** is a prosocial social network — a Django web application built to reward helpfulness, cooperation, and genuine community contribution rather than raw popularity or time-on-site. Where conventional social media optimizes for engagement (often at the cost of division and shallow interaction), Common Good deliberately cultivates empathy, mutual support, and altruism.

**North star:** Growth in prosocial skill — not daily active time — is the metric of success.

**Last updated:** July 2026 · **Implementation:** Phases 0–12 (Functional Trust)

---

## Core Principles

| Principle | What it means in practice |
|-----------|---------------------------|
| **Prosocial over popularity** | Deeply helpful replies outweigh hundreds of shallow likes. Discovery ranks by clipping and constructive signals, not raw engagement. |
| **Visibility as responsibility** | Prominence is earned through sustained prosocial behavior and quality trust scores — not tenure or follower count alone. |
| **Gentle friction before harm** | A soft reflection prompt may appear before hostile posts or replies. Users can edit, post anyway, or cancel — never a silent block. |
| **Earn your privacy upgrades** | Higher-trust capabilities (context notes, moderation tools, official role claims) unlock through demonstrated constructive participation. |
| **Knowledge outlasts conversation** | Clipping, collections, and vault turn ephemeral threads into reusable knowledge artifacts. |
| **Growth is the metric** | XP, trust, and badges reward skill development and verified help — not addiction loops or infinite scroll. |
| **AI as coach, not cop** | Automated suggestions encourage and explain; humans make every binding moderation decision. |

---

## What It Does

Common Good is a modular Django monolith with server-rendered templates and HTMX. Each module reinforces prosocial behavior:

| Area | Role |
|------|------|
| **Accounts & Profiles** | Identity with scoped role badges, mute/block boundaries |
| **Home Feed & Posting** | Paginated feed with "you're caught up" — no infinite scroll trap |
| **Interactions** | Prosocial reactions (Helpful, Kind, Clarified, etc.), context notes, reporting |
| **Knowledge** | Clip posts to a personal Vault; organize Collections and Tags |
| **Prosocial Actions** | Help requests, offers, local actions — commit, complete, verify |
| **Guilds & Messaging** | Community groups and private 1:1 coordination |
| **Discovery** | Surfaces most-clipped and sentiment-boosted content |
| **Trust & Helper Style** | Multi-dimensional ETS/PTS scores, domain reputation, earned privileges |
| **Gamification** | XP, streaks, badges — motivation without addiction |
| **AI Coach** | Pre-send content review, civility prompts, reflection journal |
| **Moderation & Safety** | Human-reviewed queue, transparent actions, 14-day appeals, crisis protocol |
| **Advanced** | Donations, skill sharing, full JSON data export |

### Trust Architecture

Influence is governed by **multi-dimensional trust** — deliberately separated so popularity alone cannot buy power:

- **Engagement Trust Score (ETS)** — quality of participation
- **Popularity Trust Score (PTS)** — social validation filtered for authenticity
- **Contribution Score** — composite (65% ETS + 35% PTS) for role eligibility; **ETS gates first**
- **Domain reputation** — separate channels (support, clarity, knowledge, civility, concern) from typed prosocial reactions

**Functional Trust** adds layered account assurance, earned privileges, community context notes, transparent moderation with appeals, and anti-gaming safeguards — all **without** exposing a single public social-credit number.

---

## Stack

- Python 3.12+, Django 5.1+
- PostgreSQL 16
- Django templates + HTMX
- Pillow (image processing)
- Docker Compose (local development)

---

## Quick Start

### Docker (recommended)

```bash
cd prosocial_platform
cp .env.example .env
docker compose up --build
```

Open [http://localhost:8000](http://localhost:8000).

Create a superuser in another terminal:

```bash
docker compose exec web python manage.py createsuperuser
```

### Local development (without Docker)

Requirements: Python 3.12+, PostgreSQL 16.

```bash
cd prosocial_platform
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -e ".[dev]"
cp .env.example .env          # set POSTGRES_HOST=localhost
python manage.py migrate
python manage.py runserver
```

### Useful commands

```bash
python manage.py migrate
python manage.py createsuperuser
pytest
ruff check .
python manage.py check --deploy --settings=config.settings.production
```

With Docker:

```bash
docker compose exec web python manage.py <command>
```

---

## Test Data

Seed five test users, posts, replies, guilds, and sample trust data:

```bash
python manage.py seed_test_data
python manage.py seed_test_data --verbose
```

All seeded accounts share the password **`TestPass123!`**. Log in at `/accounts/login/`.

| Handle | Display name | Role |
|--------|--------------|------|
| `test_river` | Test River Chen | Mentor / community helper |
| `test_morgan` | Test Morgan Lee | New member |
| `test_sam` | Test Sam Ortiz | Local action organizer |
| `test_jordan` | Test Jordan Kim | Knowledge sharer |
| `test_casey` | Test Casey Wells | Support / encouragement |

Remove test data:

```bash
python manage.py purge_test_data --dry-run   # preview
python manage.py purge_test_data             # delete
```

Trust maintenance commands:

```bash
python manage.py seed_privileges
python manage.py sync_trust_clusters
python manage.py recalculate_trust_scores
```

---

## Navigation (signed in)

The app uses a three-column shell: **left sidebar** (primary nav), **main content**, and **right rail** (context).

| Link | Route | Purpose |
|------|-------|---------|
| Home | `/dashboard/` | Feed and post composer |
| Knowledge | `/dashboard/knowledge/` | Collections, followed threads, vault links |
| Guilds | `/guilds/` | Community groups |
| Messages | `/messages/` | Private 1:1 conversations |
| Discover | `/discovery/` | Most clipped and sentiment-boosted content |
| Actions | `/actions/` | Help requests, offers, commitments |
| Notifications | `/notifications/` | Replies, thank-yous, invitations |
| Profile | `/profiles/<handle>/` | Public profile |

---

## Project Layout

```text
ProSocial/
├── README.md                    # This file
├── ApplicationSummary.md        # Purpose, architecture, prosocial role of each module
├── UserGuide.md                 # Complete feature guide with status and routes
├── ProsocialNetworkDesign.md    # Full product vision
├── FunctionalTrust.md           # Trust-network design themes
└── prosocial_platform/          # Django application
    ├── apps/
    │   ├── accounts/            # Custom user model and auth
    │   ├── profiles/            # Public profile data
    │   ├── posts/               # Posts and image uploads
    │   ├── dashboard/           # Feed, composer, knowledge hub
    │   ├── interactions/        # Replies, reactions, boundaries
    │   ├── prosocial_actions/   # Commitments, verification, invitations
    │   ├── knowledge/           # Clips, collections, tags
    │   ├── follows/
    │   ├── guilds/
    │   ├── messaging/
    │   ├── trust/               # Helper Style, ETS/PTS, privileges
    │   ├── gamification/        # XP, streaks, badges
    │   ├── ai_coach/            # Content review, journal
    │   ├── moderation/          # Queue, appeals, crisis protocol
    │   ├── engagement/          # Challenges, rest mode
    │   ├── discovery/
    │   ├── advanced/            # Donations, skills, data export
    │   └── common/              # Shared models, health, events, test data
    ├── config/settings/         # base, development, testing, production
    ├── templates/
    ├── static/
    └── deploy/
```

---

## Implementation Status

Phases 0–12 deliver a production-shaped social core with Functional Trust features end-to-end: prosocial reactions, civility prompts, context notes, appeals, scoped badges, and anti-gaming hooks.

**Fully working:** Registration and auth, dashboard feed, posts and replies, prosocial reactions, clipping and vault, prosocial actions lifecycle, guilds, 1:1 messaging, AI content review, moderation history and appeals, data export, and more.

**Partially implemented:** Some features work but lack UI links (vault in right rail, follow buttons on profiles, collection edit/add UI), MFA enrollment, donation payment processing, full XP wiring, and rest mode effects.

**Scaffolded for future work:** Group messaging, semantic search, trending feed, live collaboration rooms, achievements, and several AI coach enhancements.

See [UserGuide.md](UserGuide.md) §21–22 for the complete feature status summary and known gaps.

---

## Documentation

| Document | Contents |
|----------|----------|
| [ApplicationSummary.md](ApplicationSummary.md) | What the platform is, why it exists, how modules reinforce prosocial behavior |
| [UserGuide.md](UserGuide.md) | Complete user guide — every feature, route, and implementation status |
| [prosocial_platform/README.md](prosocial_platform/README.md) | Developer setup, test data details, security hooks |
| [ProsocialNetworkDesign.md](ProsocialNetworkDesign.md) | Full product vision and phased roadmap |
| [FunctionalTrust.md](FunctionalTrust.md) | Trust-network design themes |

---

## Security Hooks

Install git hooks from the repository root to block accidental secret leaks:

```powershell
# Windows
.\scripts\install-git-hooks.ps1
```

```bash
# macOS / Linux / Git Bash
./scripts/install-git-hooks.sh
```

Requires `pre-commit` (`pip install pre-commit` or `pip install -e ".[dev]"` from `prosocial_platform/`).

---

## How the Pieces Fit Together

```text
                    ┌─────────────────────────────────────┐
                    │     North star: prosocial growth    │
                    └─────────────────────────────────────┘
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        ▼                               ▼                               ▼
  Participate                    Signal quality                   Preserve & discover
  (posts, replies,               (prosocial reactions,            (clips, collections,
   actions, guilds)               context notes, gratitude)        discovery ranking)
        │                               │                               │
        └───────────────────────────────┼───────────────────────────────┘
                                        ▼
                         Trust & privileges (ETS-first, domain-specific)
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
            Earn capabilities    Reflect & improve     Safe community
            (tags, notes,        (pre-send prompts,    (moderation,
             moderation)          journal, challenges)   appeals, crisis)
```

No single module carries the mission alone. **Actions** turn intent into verified help. **Knowledge** makes help durable. **Interactions** replace shallow likes with meaningful signals. **Trust** ensures influence follows demonstrated care. **AI Coach** and **Moderation** protect agency while reducing harm. **Gamification** and **Engagement** sustain habit without addiction.
