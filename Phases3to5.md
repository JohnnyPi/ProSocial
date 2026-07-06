# Prosocial Platform: Phase 3–5 Engineering Backlog

## Scope

This backlog defines three deliverable phases following the completed Phase 0–2 foundation:

* **Phase 3 — Knowledge Layer and Identity Hub:** thread types, tags, clipping, collections, knowledge home, follows.
* **Phase 4 — Social Graph and Communities:** follow-weighted feed, guilds, messaging, caught-up endpoint, expanded reactions.
* **Phase 5 — Quality Signals and Trust Architecture:** peer ratings, Helper Style onboarding, trust events, hybrid ETS/PTS scoring.

Each phase should end in a deployable and testable product increment.

---

# Shared Engineering Standards

## Application structure

```text
apps/
├── knowledge/
├── follows/
├── guilds/
├── messaging/
├── trust/
├── gamification/      # Phase 6 stub hooks only in Phase 5
├── ai_coach/          # Phase 7
├── moderation/        # Phase 8
├── engagement/        # Phase 9
├── discovery/         # Phase 10
└── advanced/          # Phase 11 (donations, skill-sharing, privacy export)
```

Each application uses: `models.py`, `forms.py`, `services.py`, `selectors.py`, `views.py`, `urls.py`, `admin.py`, `migrations/`, `templates/<app_name>/`, `tests/`.

## General definition of done

Same as Phases0to2.md: models, migrations, authz, accessible templates, POST for mutations, tests, admin where useful, activity events, no internal error leakage.

---

# Phase 3 — Knowledge Layer and Identity Hub

## Phase objective

Users can clip helpful content into a personal Vault, organize clips into Collections, browse by tag, follow users and threads, and view a Knowledge Hub home page.

---

## Phase 3 Models

### P3-001: Thread type on Post

**Application:** `posts`

Add `thread_type` field:

```text
ThreadType
├── DISCUSSION
├── HELP_REQUEST
├── KNOWLEDGE_SHARE
├── SUPPORT_CIRCLE (stub)
└── CHALLENGE
```

Optional `title` field (max 200 chars) for knowledge threads.

**Acceptance criteria**

* Existing posts default to DISCUSSION.
* Users can set thread type and title when creating posts.
* Thread type appears on post detail and feed cards.

---

### P3-002: Tag model

**Application:** `knowledge`

```text
Tag
├── slug (unique)
├── name
└── created_at
```

```text
PostTag
├── post → Post
├── tag → Tag
└── unique (post, tag)
```

**Acceptance criteria**

* Users can add up to 5 tags when creating/editing a post.
* Tag browse page lists recent tagged threads.

---

### P3-003: Clip model

**Application:** `knowledge`

```text
Clip
├── public_id: UUID
├── owner → User
├── post → Post (nullable)
├── reply → Reply (nullable)
├── clip_kind: WHOLE_POST | WHOLE_REPLY | SELECTION | WHOLE_THREAD
├── quoted_text
├── selection_start (nullable int)
├── selection_end (nullable int)
├── private_note
└── created_at
```

**Rules**

* Exactly one of post or reply must be set for content clips.
* WHOLE_THREAD clips reference the post only.
* Owner cannot clip deleted content.
* Clipping is idempotent per (owner, post/reply, clip_kind, selection range).

**Acceptance criteria**

* User can clip a whole post from post detail.
* User can clip a reply from reply thread.
* Clips appear in personal Vault with source attribution link.
* Activity event `CLIP_CREATED` is recorded.

---

### P3-004: Collection models

**Application:** `knowledge`

```text
Collection
├── public_id: UUID
├── owner → User
├── title
├── description
├── visibility: PRIVATE | GUILD | PUBLIC
└── created_at, updated_at

CollectionItem
├── collection → Collection
├── clip → Clip (nullable)
├── post → Post (nullable)
├── sort_order
└── unique constraints per item type
```

**Acceptance criteria**

* User can create private collections.
* User can add clips and whole posts to a collection.
* Collection detail shows ordered items with source links.
* Only owner can edit private collections.

---

### P3-005: Follow models

**Application:** `follows`

```text
UserFollow
├── follower → User
├── following → User
└── unique (follower, following)

PostFollow
├── user → User
├── post → Post
└── unique (user, post)
```

**Acceptance criteria**

* User can follow/unfollow another user (not self).
* User can follow/unfollow a post (thread).
* Following generates `USER_FOLLOWED` / `POST_FOLLOWED` notifications.
* Followed activity appears on Knowledge Hub.

---

### P3-006: Knowledge Hub dashboard

**Application:** `dashboard` (view extension)

Panels:

* Activity feed (recent from followed users/threads)
* My Collections (recent 5)
* Followed threads
* Placeholders: Active Challenges, Streak tracker

Route: `/dashboard/knowledge/`

**Acceptance criteria**

* Authenticated user sees personalized knowledge home.
* Links navigate to vault, collections, and tag browse.

---

## Phase 3 Release Acceptance Criteria

* User can clip, collect, tag, and follow.
* Knowledge Hub renders without JavaScript.
* Integration tests in `tests/integration/test_phase3_flow.py` pass.
* No XP or trust scores displayed yet (stubs only).

---

# Phase 4 — Social Graph and Communities

## Phase objective

Move from global feed to contextual communities with guilds, DMs, follow-weighted feed, and explicit feed boundary.

---

## Phase 4 Models

### P4-001: Guild

**Application:** `guilds`

```text
Guild
├── public_id: UUID
├── name
├── slug (unique)
├── description
├── guild_type: CAUSE | HOBBY | HELPER_STYLE | FORUM_THEME
├── banner_url (optional)
├── created_by → User

GuildMembership
├── guild → Guild
├── user → User
├── role: LEADER | MEMBER
└── unique (guild, user)
```

Forum theme presets: Local Initiatives, Mental Wellness, Skill-Sharing, Environmental Action.

**Acceptance criteria**

* User can create a guild (becomes LEADER).
* User can join/leave guilds.
* Guild detail shows member list and guild-scoped post feed.

---

### P4-002: Guild posts

Add optional `guild` FK on `Post`.

**Acceptance criteria**

* Posts can be scoped to a guild.
* Guild feed filters by guild membership visibility.

---

### P4-003: Messaging

**Application:** `messaging`

```text
Conversation
├── public_id: UUID
├── participant_a → User
├── participant_b → User
├── unique ordered pair

Message
├── conversation → Conversation
├── sender → User
├── body (max 2000)
├── read_at
└── created_at
```

**Acceptance criteria**

* Blocked users cannot message each other.
* User sees conversation list and can send/receive text messages.
* Unread count shown in nav.

---

### P4-004: Follow-weighted feed

**Application:** `posts.selectors`

Feed modes:

* `all` — chronological global (existing)
* `following` — posts from followed users and guild memberships
* `caught_up` — returns empty next page with explicit end marker

**Acceptance criteria**

* Dashboard supports `?feed=following`.
* Feed shows "You're caught up" when no more pages.

---

### P4-005: Expanded reactions

**Application:** `interactions`

```text
ProsocialReaction
├── sender → User
├── post/reply target
├── kind: CONSTRUCTIVE | SUPPORTIVE | INSIGHTFUL
└── one per kind per target per sender
```

**Acceptance criteria**

* No public dislike counts.
* Reactions are additive, not ranked by count in feed.

---

## Phase 4 Release Acceptance Criteria

* Guilds, messaging, follow feed, and caught-up endpoint work.
* `tests/integration/test_phase4_flow.py` passes.

---

# Phase 5 — Quality Signals and Trust Architecture

## Phase objective

Measure prosocial quality with peer ratings and hybrid trust scoring (internal Contribution Score; public range or hidden).

---

## Phase 5 Models

### P5-001: Helper Style

**Application:** `trust`

```text
HelperStyle (enum)
├── EMPATHIZER
├── SAGE
├── BUILDER
├── GUIDE
└── CONNECTOR

UserTrustProfile
├── user (OneToOne)
├── helper_style
├── helper_style_completed_at
├── engagement_trust_score (ETS)
├── popularity_trust_score (PTS)
├── contribution_score
├── score_visibility: HIDDEN | RANGE | EXACT (default HIDDEN)
└── updated_at
```

Onboarding questionnaire at `/trust/onboarding/`.

---

### P5-002: Peer ratings

```text
PeerRating
├── rater → User
├── reply → Reply (nullable)
├── post → Post (nullable)
├── dimension: HELPED_ME | HELPFUL | SUPPORTIVE | INSIGHTFUL
├── is_positive
└── unique per (rater, target, dimension)
```

Negative dimensions (for moderation only, anonymous to rated user):

```text
ESCALATORY | DISMISSIVE | SPAMMY
```

---

### P5-003: Trust events

```text
TrustEvent
├── user → User
├── event_type
├── weight (float)
├── source_id (generic reference)
├── metadata (JSON)
└── created_at
```

Background management command: `recalculate_trust_scores`

Formula: `contribution_score = (ETS × 0.65) + (PTS × 0.35)`

ETS gates: role eligibility requires ETS threshold before PTS matters.

---

### P5-004: Profile trust display

Public profile shows:

* Helper Style badge (if set)
* Contribution range (if visibility = RANGE) e.g. "Trusted Contributor"
* Pinned contributions (clips/collections user opts to pin)

Private settings show full score trend.

**Acceptance criteria**

* Scores hidden by default.
* User can opt into range display.
* ETS must exceed threshold for any role unlock (Phase 8).

---

## Phase 5 Release Acceptance Criteria

* Helper Style onboarding, peer ratings, and trust recalculation work.
* `tests/integration/test_phase5_flow.py` passes.
* No gamification XP awarded yet (Phase 6).
