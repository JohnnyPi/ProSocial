# Stage 2 — Application Inventory

**Repository:** `e:\CursorApps\ProSocial`
**Application root:** [prosocial_platform](../prosocial_platform)
**Audit date:** 2026-07-05

---

## 2.1 Repository Topology

```
ProSocial/
├── ProsocialNetworkDesign.md      # Product specification
├── CompleteAudit.md               # Audit procedure
├── audit/                         # Audit deliverables (this folder)
├── .github/workflows/ci.yml       # CI pipeline
└── prosocial_platform/            # Django modular monolith
    ├── apps/                      # 18 domain apps
    ├── config/                    # settings, urls, wsgi/asgi
    ├── deploy/Dockerfile
    ├── static/                    # css, htmx
    ├── templates/                 # shared layouts, auth, errors
    ├── tests/                     # integration + unit (pytest)
    ├── compose.yaml
    ├── manage.py
    ├── pyproject.toml
    ├── .env.example
    └── README.md
```

### Django Apps (18)

| App | Path | Purpose |
|-----|------|---------|
| accounts | `apps/accounts/` | Custom `User` model, registration, login, password flows |
| profiles | `apps/profiles/` | Public profile (handle, bio, avatar); edit own profile |
| posts | `apps/posts/` | Posts (text/image), soft delete, moderation status, thread types |
| dashboard | `apps/dashboard/` | Feed composer, paginated feed, knowledge hub |
| interactions | `apps/interactions/` | Replies, thank-yous, notifications, hide/mute/block, reports, reactions |
| prosocial_actions | `apps/prosocial_actions/` | Action opportunities, commitments, verification, invitations |
| knowledge | `apps/knowledge/` | Clips, vault, collections, tags |
| follows | `apps/follows/` | User and post follows |
| guilds | `apps/guilds/` | Community groups, membership, guild feed |
| messaging | `apps/messaging/` | 1:1 conversations and messages |
| trust | `apps/trust/` | Helper Style, ETS/PTS/contribution scores, peer ratings |
| gamification | `apps/gamification/` | XP, levels, streaks, badges, achievements |
| ai_coach | `apps/ai_coach/` | Keyword sentiment, journal, interventions, thread summaries |
| moderation | `apps/moderation/` | Role assignments, review queue, crisis flags, transparency log |
| engagement | `apps/engagement/` | Challenges, guild missions, rest mode, re-engagement messages |
| discovery | `apps/discovery/` | Most clipped, sentiment-boosted feed, ripple, spotlights |
| advanced | `apps/advanced/` | Donation campaigns (stub), skill offerings, data export |
| common | `apps/common/` | `TimeStampedModel`, `ActivityEvent` audit log, health check, error handlers |

**Note:** README describes implementation phases 0–11; design document roadmap has phases 1–4 only. Implementation exceeds design roadmap scope in many areas.

---

## 2.2 Technology Stack (Actual vs Design)

| Layer | Design (§15) | Actual | Deviation class |
|-------|--------------|--------|-----------------|
| Client | Next.js / React / TypeScript | Django templates + HTMX | Manageable |
| API | Next.js API Routes | Django views (server-rendered) | Manageable |
| Database | Supabase PostgreSQL | PostgreSQL 16 (Docker/CI) | Beneficial (same engine) |
| Auth | Supabase Auth | Django session auth, custom `accounts.User` | Manageable |
| Realtime | Supabase Realtime / WebSocket | None | Blocker for live features only |
| Storage | Supabase Storage | Django `MEDIA_ROOT` + Pillow | Manageable |
| Security | Row-Level Security | Django ORM + view-level authz | Manageable — requires authz audit |
| AI | Anthropic API + NLTK/BERT | In-process keyword heuristic (`keyword-v1`) | Blocker for design Phase 3 intelligence |
| Background jobs | Edge Functions + pg_cron | Management commands only | Technical debt for scale |
| Forms | React Hook Form + Zod | Django forms | Manageable |
| CSS | Tailwind + shadcn/ui | Custom `static/css/site.css` | Manageable |
| Python | — | ≥3.12 | — |
| Framework | — | Django ≥5.1, <7 | — |
| Test | — | pytest + pytest-django | — |
| Lint | — | ruff, pre-commit | — |
| Container | — | Docker Compose (Postgres + web) | — |

**Evidence:** [pyproject.toml](../prosocial_platform/pyproject.toml), [config/settings/base.py](../prosocial_platform/config/settings/base.py), [apps/ai_coach/services.py](../prosocial_platform/apps/ai_coach/services.py)

---

## 2.3 Environment and Configuration

| File | Purpose |
|------|---------|
| [.env.example](../prosocial_platform/.env.example) | Placeholder `DJANGO_SECRET_KEY`, Postgres connection — safe placeholders |
| [config/settings/base.py](../prosocial_platform/config/settings/base.py) | App registry, auth model, content limits, rate limits, cache |
| [config/settings/development.py](../prosocial_platform/config/settings/development.py) | `.env` load, console email backend |
| [config/settings/testing.py](../prosocial_platform/config/settings/testing.py) | SQLite in-memory or CI Postgres, MD5 hasher |
| [config/settings/production.py](../prosocial_platform/config/settings/production.py) | Deploy checks via CI `check --deploy` |
| [compose.yaml](../prosocial_platform/compose.yaml) | Postgres 16 + web service |

**Rate limits (base.py):** Registration 5/hr, login 10/15min.
**Content limits:** Post body 5000 chars, image 5MB max 4096px JPEG/PNG/WEBP.

---

## 2.4 Schema Inventory

### Core entities vs design §15

| Design table | Implementation | App | Notes |
|--------------|----------------|-----|-------|
| users | `User` | accounts | `public_id` UUID, unique email |
| profiles | `Profile` | profiles | OneToOne; no visibility enum |
| threads | `Post` with `thread_type`, `title` | posts | Thread = post, not separate table |
| posts | `Reply` | interactions | Nested via `parent` FK (1-level enforced in service) |
| clips | `Clip` | knowledge | `clip_kind`, selection fields, `private_note` |
| collections | `Collection`, `CollectionItem` | knowledge | Visibility enum; no public read path |
| collection_items | `CollectionItem` | knowledge | Clip OR post per item |
| follows | `UserFollow`, `PostFollow` | follows | Unidirectional only |
| reactions | `ProsocialReaction`, `ThankYou` | interactions | Multiple reaction kinds |
| notifications | `Notification` | interactions | Recipient-scoped |
| media_assets | `Post.image` | posts | Inline on post, not separate table |
| trust_events | `TrustEvent` | trust | Weighted events |
| reflection_journal | `ReflectionJournalEntry` | ai_coach | Not encrypted at field level |
| sentiment_snapshots | `SentimentSnapshot` | ai_coach | `model_version=keyword-v1` |
| moderation_actions | `ModerationReview`, `TransparencyLogEntry` | moderation | Linked to reports |
| ripple_chains | `RippleLink` | discovery | Helper/helped/citation |

### Soft delete

| Model | Mechanism | Queryset filter |
|-------|-----------|-----------------|
| `Post` | `deleted_at` | `Post.objects.visible()` |
| `Reply` | `deleted_at` | `Reply.objects.visible()` — **not used in `get_post_replies`** |

### Visibility models

| Model | Field | Values | Enforced in views |
|-------|-------|--------|-------------------|
| `Collection` | `visibility` | PRIVATE, GUILD, PUBLIC | Owner-only routes only |
| `UserTrustProfile` | `score_visibility` | HIDDEN, RANGE, EXACT | Own settings only |
| `Commitment` | `is_public` | boolean | `commitment_detail` 403 check |
| `Post` | `moderation_status` | ACTIVE, etc. | `visible()` queryset |

---

## 2.5 Route Map

Root: [config/urls.py](../prosocial_platform/config/urls.py)

| Prefix | App | Key routes |
|--------|-----|------------|
| `/` | common | Home redirect |
| `/health/` | common | Health JSON |
| `/admin/` | Django | Admin |
| `/accounts/` | accounts | register, login, logout, password change/reset (8 routes) |
| `/profiles/` | profiles | edit, `<handle>/` |
| `/posts/` | posts | create, detail, edit, delete |
| `/dashboard/` | dashboard | feed, `knowledge/` hub |
| `/knowledge/` | knowledge | vault, collections CRUD, tags, clip post |
| `/follows/` | follows | follow user/post toggles |
| `/guilds/` | guilds | list, create, detail, join/leave |
| `/messages/` | messaging | list, detail, start by handle |
| `/trust/` | trust | onboarding, settings, rate post/reply |
| `/gamification/` | gamification | progress dashboard |
| `/ai/` | ai_coach | journal list/create |
| `/moderation/` | moderation | queue, review detail |
| `/engagement/` | engagement | challenges, rest mode |
| `/discovery/` | discovery | home, ripple |
| `/advanced/` | advanced | donations, skills, export |
| `/` (root) | interactions | replies, thanks, notifications, hide, mute/block, reports |
| `/` (root) | prosocial_actions | actions, commitments, invitations, verification |

**Total approximate user-facing routes:** 70+

---

## 2.6 Integration Map

| Integration | Status | Evidence |
|-------------|--------|----------|
| AI provider (Anthropic/OpenAI) | **Not integrated** | `ai_coach/services.py` — keyword lists only |
| Email | Console (dev), locmem (test) | `development.py`, password reset templates |
| Payment processor | **Stub** | `advanced/services.py` — fee calc without gateway |
| Object storage | Local `media/` | `MEDIA_ROOT` in settings |
| WebSocket / realtime | **Absent** | No Channels/ASGI consumers |
| Background jobs | Management command only | `trust/management/commands/recalculate_trust_scores.py` |
| Full-text / semantic search | **Absent** | `discovery/selectors.py` — ranking only |
| External OAuth | **Absent** | Django auth only |

---

## 2.7 Test Inventory

**Config:** `testpaths = ["tests"]` — app-level `apps/*/tests/` may not run in CI.

| File | Coverage area | Test count (approx) |
|------|---------------|---------------------|
| `tests/integration/test_phase0_flow.py` | Health, auth, dashboard, post create, edit authz | 5 |
| `tests/integration/test_phase1_flow.py` | Replies, nesting limit, thanks, block, mute feed | 5 |
| `tests/integration/test_phase2_flow.py` | Prosocial actions lifecycle | 5 |
| `tests/integration/test_phase3_flow.py` | Clips, collections, follows, knowledge hub | 4 |
| `tests/integration/test_phase4_flow.py` | Guilds, messaging, following feed, reactions | 5 |
| `tests/integration/test_phase5_flow.py` | Trust onboarding, peer ratings | 4 |
| `tests/integration/test_phase6_flow.py` | XP award, level up | 3 |
| `tests/integration/test_phase7_flow.py` | Sentiment, pre-send prompt, journal | 4 |
| `tests/integration/test_phase8_flow.py` | Crisis flags, role sync | 3 |
| `tests/integration/test_phase9_flow.py` | Challenges, rest mode | 2 |
| `tests/integration/test_phase10_flow.py` | Discovery, ripple | 3 |
| `tests/integration/test_phase11_flow.py` | Donations, skills, export | 3 |
| `tests/integration/test_security.py` | CSRF, XSS escaping, safe delete | 3 |
| `tests/unit/test_account_models.py` | User/Profile validation | 2 |
| `tests/unit/test_post_models.py` | Post validation | 2 |

**Run result (2026-07-05):** 62 passed in 2.63s

**Gaps:** No password-reset email integration test, no moderator E2E HTTP tests, no collection visibility tests, no clip passage selection tests, no account deletion tests, duplicate unit tests in `apps/accounts/tests/` and `apps/posts/tests/`.

---

## 2.8 CI/CD and Exclusions

**CI** ([.github/workflows/ci.yml](../.github/workflows/ci.yml)): ruff → migrate → pytest → `check --deploy` on Postgres 16.

**.gitignore** ([prosocial_platform/.gitignore](../prosocial_platform/.gitignore)):
- Excludes: `.env`, venvs, `media/`, `staticfiles/`, `db.sqlite3`, caches, coverage, logs
- **Present on disk but gitignored:** `.env` (local secrets — not audited for content in this stage)

---

## 2.9 Stack Deviation Summary

| Count | Classification |
|-------|----------------|
| 8 | Manageable |
| 1 | Beneficial |
| 2 | Blocker (realtime, true AI/semantic search for Phase 3+) |
| 1 | Technical debt (background jobs) |
| 3 | Intentionally deferred (payments, semantic search per README) |

---

## 2.10 Stage 2 Exit Criteria

- [x] Directory tree and app purposes documented
- [x] Actual stack derived from code with deviation classification
- [x] Schema inventory with soft-delete and visibility notes
- [x] Complete route index
- [x] Integrations mapped (including stubs)
- [x] Test coverage map with gaps identified
