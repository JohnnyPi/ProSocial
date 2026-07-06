# Stage 1 — Audit Baseline

**Source specification:** [ProsocialNetworkDesign.md](../ProsocialNetworkDesign.md)  
**Audit date:** 2026-07-05  
**Method:** Full read of design document; requirements extracted and classified per [CompleteAudit.md](../CompleteAudit.md) §1.

---

## 1.1 Requirement ID Scheme

| Prefix | Area |
|--------|------|
| `PHIL` | Purpose and guiding philosophy |
| `P1`–`P7` | Core design principles |
| `SOC` | Baseline social features |
| `ACT` | Dedicated prosocial-action features |
| `TRUST` | Trust and identity architecture |
| `GAME` | Gamification |
| `KNOW` | Knowledge and forum systems |
| `COLLAB` | Collaboration and community |
| `AI` | AI and LLM layer |
| `MOD` | Roles, moderation, and safety |
| `ENG` | Engagement and well-being |
| `UX` | Emotionally aware UX |
| `PRIV` | Privacy, security, and ethics |
| `MORAL` | Moral-values foundation |
| `STACK` | Technology stack and data model |
| `ROAD` | Phased implementation roadmap |

**Scope columns:**
- `DesignPhase`: 1, 2, 3, 4, or `Vision` (not in roadmap table §16)
- `AuditPriority`: `Roadmap`, `Foundation`, or `Deferred`

---

## 1.2 Open Design Decisions Log

| ID | Conflict | Affected requirements | Resolution status |
|----|----------|----------------------|-------------------|
| ODD-01 | P3 requires soft reflection and never blocking silently; §10.3 workflow hides flagged content pending human review | P3, MOD-WORKFLOW-01 | Unresolved — implementation must choose pre-publish vs post-publish friction |
| ODD-02 | P4 gates privacy behind trust thresholds; §13 allows anonymous posting opt-in per thread without trust gate | P4, PRIV-ANON-01, MOD-SUPPORT-01 | Unresolved — Support Circles partially align via Supporter+ visibility |
| ODD-03 | Gamification levels (Helper Initiate → Community Leader) vs trust roles (Member → Legendary Steward) share names (Community Supporter, Mentor) | GAME-LEVEL-01, TRUST-ROLE-01 | Unresolved — risk of user confusion and duplicate privilege systems |
| ODD-04 | ETS role thresholds (>40, >60, … >90) stated without ETS scale definition (0–100 assumed) | TRUST-ETS-01, TRUST-ROLE-01 | Unresolved — implementation uses 0–100 in code but design is silent |
| ODD-05 | Legendary Steward "Top 1%, sustained" — no duration or measurement window | TRUST-ROLE-09 | Unresolved |
| ODD-06 | Contribution Score public display: §5.4 private trend vs §13 default shown with range option | TRUST-PROFILE-02, PRIV-SCORE-01 | Partially resolved in implementation (default HIDDEN) |
| ODD-07 | Proposed stack (Next.js + Supabase + RLS) vs any Django implementation | STACK-* | Accepted deviation — Django monolith is manageable |
| ODD-08 | Phase 1 "basic home page" vs §7.4 full modular Knowledge Hub | ROAD-P1-HOME, KNOW-HUB-01 | Unresolved — scope of Phase 1 home undefined |
| ODD-09 | Sentiment: NLTK/TextBlob + BERT + Anthropic — unclear which handles sentiment vs LLM-only | AI-SENT-01, STACK-AI-01 | Unresolved in design |
| ODD-10 | Background jobs: Supabase Edge Functions + pg_cron vs Celery-style workers | STACK-JOBS-01 | Unresolved in design |
| ODD-11 | Payment providers listed in donation UX but absent from §15 stack | ACT-DONATE-01, STACK-PAY-01 | Unresolved |
| ODD-12 | AI "learns from moderators" vs ethical AI logging/opt-out — no training governance | AI-PHIL-01, PRIV-AI-01 | Unresolved |
| ODD-13 | Full vision (§3–14) vastly exceeds four-phase roadmap — phase completion metrics need separate columns | All Vision rows | Documented — use Roadmap vs Vision scope |

---

## 1.3 Principles Traceability Index

| Principle | Governs requirement IDs |
|-----------|-------------------------|
| P1 Prosocial Over Popularity | SOC-FEED-02, SOC-REACT-01, KNOW-DISC-02, GAME-XP-01, TRUST-ETS-02, TRUST-PTS-02 |
| P2 Visibility as Responsibility | TRUST-ROLE-01, TRUST-PROFILE-01, SOC-FEED-02, KNOW-DISC-03 |
| P3 Gentle Friction Before Harm | MOD-WORKFLOW-01, AI-INTERVENT-01, MOD-APPEAL-01 |
| P4 Earn Your Privacy Upgrades | PRIV-GROUP-01, PRIV-ANON-01, TRUST-ROLE-01 |
| P5 Knowledge Outlasts Conversation | KNOW-CLIP-01, KNOW-COL-01, KNOW-THREAD-01, AI-SUMMARY-01 |
| P6 Growth Is the Metric | PHIL-NORTH-01, GAME-PHIL-01, ENG-LOOP-01 |
| P7 AI Is a Coach, Not a Cop | AI-PHIL-01, MOD-WORKFLOW-02, AI-INTERVENT-02 |

---

## 1.4 Requirements Checklist

### Purpose and Guiding Philosophy

| ID | Requirement | Classification | DesignPhase | AuditPriority |
|----|-------------|----------------|-------------|---------------|
| PHIL-NORTH-01 | North star: growth in prosocial skill, not daily active time | Design principle | Vision | Foundation |
| PHIL-MISSION-01 | Platform incentivizes empathy, cooperation, altruism over engagement extraction | Design principle | Vision | Foundation |
| PHIL-AUDIENCE-01 | Serves givers, learners, mentors, cause communities, burnout refugees | Aspirational | Vision | Deferred |

### Core Design Principles (P1–P7)

| ID | Requirement | Classification | DesignPhase | AuditPriority |
|----|-------------|----------------|-------------|---------------|
| P1 | Helpful depth outweighs shallow likes in ranking and rewards | Design principle | Vision | Foundation |
| P2 | Prominence earned through prosocial behavior, not tenure/followers | Design principle | Vision | Foundation |
| P3 | Soft reflection before harm; never block silently; always explain | Design principle | Vision | Foundation |
| P4 | Private groups, mentorship, anonymous posting gated by trust | Design principle | Vision | Foundation |
| P5 | Threads are lasting knowledge artifacts | Design principle | 1 | Roadmap |
| P6 | KPI is prosocial skill improvement | Design principle | Vision | Foundation |
| P7 | AI advises; user has last word; humans confirm moderation | Design principle | 3 | Roadmap |

### Baseline Social Features (§3)

| ID | Requirement | Classification | DesignPhase | AuditPriority |
|----|-------------|----------------|-------------|---------------|
| SOC-PROFILE-01 | Customizable profiles: bio, interests, photos, external links | Explicit functional | 1 | Roadmap |
| SOC-PROFILE-02 | Profile displays prosocial standing (trust, badges, XP) | UI/UX | Vision | Foundation |
| SOC-FEED-01 | Personalized feed from connections, follows, groups | Explicit functional | 1 | Roadmap |
| SOC-FEED-02 | Feed weighted toward positive sentiment and diversity | Design principle | Vision | Foundation |
| SOC-FEED-03 | "You're caught up" endpoint; no infinite-scroll trap | UI/UX | Vision | Foundation |
| SOC-FOLLOW-01 | Bidirectional friend connections | Explicit functional | Vision | Deferred |
| SOC-FOLLOW-02 | Unidirectional follows | Explicit functional | 2 | Roadmap |
| SOC-MSG-01 | Private 1:1 messaging | Explicit functional | Vision | Foundation |
| SOC-MSG-02 | Public/private group chats | Explicit functional | Vision | Deferred |
| SOC-MSG-03 | Optional voice/video | Future-phase | Vision | Deferred |
| SOC-CONTENT-01 | Text posts | Explicit functional | 1 | Roadmap |
| SOC-CONTENT-02 | Image sharing | Explicit functional | 1 | Roadmap |
| SOC-CONTENT-03 | Video sharing | Future-phase | Vision | Deferred |
| SOC-CONTENT-04 | External links | Explicit functional | Vision | Foundation |
| SOC-CONTENT-05 | Live streaming | Future-phase | Vision | Deferred |
| SOC-REACT-01 | Comments plus emotional reactions beyond simple like | Explicit functional | 1 | Roadmap |
| SOC-UX-01 | Simple, friendly interface | UI/UX | 1 | Roadmap |
| SOC-UX-02 | WCAG-accessible design | UI/UX | Vision | Foundation |
| SOC-UX-03 | Intuitive navigation | UI/UX | 1 | Roadmap |
| SOC-UX-04 | Prosocial features prominently placed | UI/UX | Vision | Foundation |
| SOC-UX-05 | Positive emotional valence in content surfacing | Design principle | Vision | Foundation |
| SOC-UX-06 | Impact statistics and participation instructions | UI/UX | Vision | Deferred |

### Dedicated Prosocial-Action Features (§4)

| ID | Requirement | Classification | DesignPhase | AuditPriority |
|----|-------------|----------------|-------------|---------------|
| ACT-VOL-01 | Volunteering: interest/skill matching, scheduling, hour tracking | Explicit functional | Vision | Deferred |
| ACT-DONATE-01 | Donation gateways to verified non-profits and campaigns | Explicit functional | Vision | Deferred |
| ACT-DONATE-02 | Minimal-step mobile-responsive donation forms | UI/UX | Vision | Deferred |
| ACT-DONATE-03 | Multiple payment options (cards, Apple/Google Pay, PayPal) | Explicit functional | Vision | Deferred |
| ACT-DONATE-04 | Transparent processing fees before checkout | UI/UX | Vision | Deferred |
| ACT-DONATE-05 | Donation history and receipts | Explicit functional | Vision | Deferred |
| ACT-SKILL-01 | Users offer and request skills | Explicit functional | Vision | Foundation |
| ACT-SKILL-02 | Workshops/tutorials online or in-person | Explicit functional | Vision | Deferred |
| ACT-SKILL-03 | Skill-specific forums and mentorship | Explicit functional | Vision | Deferred |
| ACT-FORUM-01 | Themed community support forums with moderation | Explicit functional | Vision | Foundation |
| ACT-FORUM-02 | User-created sub-forums | Future-phase | Vision | Deferred |

### Trust and Identity Architecture (§5)

| ID | Requirement | Classification | DesignPhase | AuditPriority |
|----|-------------|----------------|-------------|---------------|
| TRUST-ETS-01 | Engagement Trust Score from sentiment, peer ratings, challenges, moderation, journal, crisis | Data-model | Vision | Foundation |
| TRUST-ETS-02 | ETS gates high-privilege roles before PTS | Design principle | Vision | Foundation |
| TRUST-PTS-01 | Popularity Trust Score from followers, clips, endorsements, nominations | Data-model | Vision | Foundation |
| TRUST-PTS-02 | PTS alone cannot unlock high-privilege roles | Design principle | Vision | Foundation |
| TRUST-CCS-01 | Contribution Score = (ETS × 0.65) + (PTS × 0.35) | Data-model | Vision | Foundation |
| TRUST-HELPER-01 | Helper Style onboarding questionnaire (5 styles) | Explicit functional | Vision | Foundation |
| TRUST-HELPER-02 | Helper Style evolves over time | Future-phase | Vision | Deferred |
| TRUST-PROFILE-01 | Public: Helper Style, level/XP, badges, pinned contributions, Ripple, spotlights | UI/UX | Vision | Foundation |
| TRUST-PROFILE-02 | Private: full XP history, journal, contribution trend, streaks, challenges | UI/UX | Vision | Foundation |

### Gamification Framework (§6)

| ID | Requirement | Classification | DesignPhase | AuditPriority |
|----|-------------|----------------|-------------|---------------|
| GAME-PHIL-01 | Mechanics reward prosocial behavior, not addiction | Design principle | Vision | Foundation |
| GAME-XP-01 | XP calibrated tables for Helping, Knowledge, Community actions | Explicit functional | Vision | Foundation |
| GAME-XP-02 | Crisis emotional support highest XP tier (90 base) | Explicit functional | Vision | Foundation |
| GAME-MULT-01 | Multipliers stack to 4× cap with streak tiers and grace day | Explicit functional | Vision | Foundation |
| GAME-LEVEL-01 | Four level tiers (Helper Initiate through Community Leader) | Explicit functional | Vision | Foundation |
| GAME-SKILL-01 | Branch skill trees (Emotional Support, Knowledge, Mentorship) | Future-phase | Vision | Deferred |
| GAME-BADGE-01 | Tiered badges gated on sustained positive sentiment | Explicit functional | Vision | Foundation |
| GAME-ACHIEVE-01 | Daily/weekly/monthly/rare achievement celebrations | Explicit functional | Vision | Deferred |

### Knowledge and Forum System (§7)

| ID | Requirement | Classification | DesignPhase | AuditPriority |
|----|-------------|----------------|-------------|---------------|
| KNOW-THREAD-01 | Threads with title, tags, sentiment indicator | Explicit functional | 1 | Roadmap |
| KNOW-THREAD-02 | Threaded sentiment-scored replies | Explicit functional | 1 | Roadmap |
| KNOW-THREAD-03 | AI-generated summary pinned on long threads | Explicit functional | 3 | Roadmap |
| KNOW-THREAD-04 | LLM "most helpful" highlights | Explicit functional | 3 | Roadmap |
| KNOW-THREAD-05 | Evolution trail (updates/forks/citations) | Future-phase | 4 | Roadmap |
| KNOW-THREAD-06 | Aggregate Prosocial Rating per thread | Explicit functional | Vision | Foundation |
| KNOW-THREAD-07 | Thread types: Discussion, Help Request, Knowledge Share, Support Circle, Challenge, Quest | Explicit functional | Vision | Foundation |
| KNOW-CLIP-01 | Clip whole post, passage/sentence, or entire thread | Explicit functional | 1 | Roadmap |
| KNOW-CLIP-02 | Auto source reference on clips | Data-model | 1 | Roadmap |
| KNOW-CLIP-03 | Personal Vault for clips | Explicit functional | 1 | Roadmap |
| KNOW-CLIP-04 | Private notes on clips | Explicit functional | 2 | Roadmap |
| KNOW-CLIP-05 | XP bonus to original author when clipped by others | Explicit functional | Vision | Foundation |
| KNOW-COL-01 | Collections: clips + threads + links + intros | Explicit functional | 1 | Roadmap |
| KNOW-COL-02 | Collection visibility: Private, Guild-shared, Public | Explicit functional | 2 | Roadmap |
| KNOW-COL-03 | Public collections earn Knowledge Sharing XP | Explicit functional | Vision | Foundation |
| KNOW-HUB-01 | Modular home: feed, challenges, guild, followed threads, collections, ripple, XP | UI/UX | Vision | Foundation |
| KNOW-HUB-02 | Drag-and-drop home customization | Future-phase | 4 | Roadmap |
| KNOW-DISC-01 | Tag browsing | Explicit functional | 2 | Roadmap |
| KNOW-DISC-02 | Most Clipped, Most Referenced discovery surfaces | Explicit functional | Vision | Foundation |
| KNOW-DISC-03 | Sentiment-boosted content preference | Design principle | Vision | Foundation |
| KNOW-DISC-04 | Semantic search | Future-phase | 3 | Roadmap |
| KNOW-DISC-05 | Suppress net-negative and moderation-flagged content | Explicit functional | Vision | Foundation |

### Collaboration and Community (§8)

| ID | Requirement | Classification | DesignPhase | AuditPriority |
|----|-------------|----------------|-------------|---------------|
| COLLAB-GUILD-01 | Guilds with internal roles and collective XP | Explicit functional | Vision | Foundation |
| COLLAB-GUILD-02 | Guild customizations (banners, emblems, themes) | Future-phase | Vision | Deferred |
| COLLAB-QUEST-01 | Multi-stage collaborative quests | Explicit functional | Vision | Foundation |
| COLLAB-BOARD-01 | Shared task boards with sentiment de-escalation | Future-phase | Vision | Deferred |
| COLLAB-LIVE-01 | Live collaboration rooms with LLM facilitation | Future-phase | Vision | Deferred |
| COLLAB-SEASON-01 | Seasonal community-wide challenges | Explicit functional | Vision | Foundation |
| COLLAB-SPOT-01 | Community spotlights and LLM impact narratives | Explicit functional | Vision | Foundation |

### AI and LLM Layer (§9)

| ID | Requirement | Classification | DesignPhase | AuditPriority |
|----|-------------|----------------|-------------|---------------|
| AI-PHIL-01 | AI never makes binding decisions; explains; dismissible; learns from moderators | AI/moderation | 3 | Roadmap |
| AI-SENT-01 | Score every post, comment, message for sentiment | AI/moderation | Vision | Foundation |
| AI-SENT-02 | Sentiment feeds ETS and badge gating | Data-model | Vision | Foundation |
| AI-FORECAST-01 | Prosocial Trajectory Score per thread | AI/moderation | Vision | Deferred |
| AI-INTERVENT-01 | Pre-post reflection prompt for flagged content | AI/moderation | Vision | Foundation |
| AI-INTERVENT-02 | Positive reinforcement on helpful behavior | AI/moderation | Vision | Foundation |
| AI-INTERVENT-03 | Comment ranking: boost positive, collapse negative | UI/UX | Vision | Foundation |
| AI-ELEVATE-01 | Uplifting content when community sentiment trends negative | AI/moderation | Vision | Deferred |
| AI-JOURNAL-01 | Private LLM-prompted reflection journal | Explicit functional | Vision | Foundation |
| AI-RIPPLE-01 | Interactive Ripple Effect visualization on profiles | Explicit functional | Vision | Foundation |
| AI-COACH-01 | Personalized challenges adapted to Helper Style and sentiment | AI/moderation | Vision | Foundation |
| ROAD-P3-SUM | Thread summaries (roadmap Phase 3) | Explicit functional | 3 | Roadmap |
| ROAD-P3-HIGH | Key-post highlights (roadmap Phase 3) | Explicit functional | 3 | Roadmap |
| ROAD-P3-SUGG | AI related content and collection suggestions | Explicit functional | 3 | Roadmap |
| ROAD-P3-GRAPH | Internal knowledge graph | Data-model | 3 | Roadmap |

### Roles, Moderation and Safety (§10)

| ID | Requirement | Classification | DesignPhase | AuditPriority |
|----|-------------|----------------|-------------|---------------|
| TRUST-ROLE-01 | Role ladder with ETS and Contribution Score thresholds | Explicit functional | Vision | Foundation |
| TRUST-ROLE-02 | Dynamic continuous role evaluation | Explicit functional | Vision | Foundation |
| TRUST-ROLE-03 | Leadership role rotation (6-month max) | Explicit functional | Vision | Deferred |
| MOD-WORKFLOW-01 | AI scan → Clean/Borderline/Flagged → human review → notify → transparency log | AI/moderation | Vision | Foundation |
| MOD-WORKFLOW-02 | AI flags; humans decide | AI/moderation | Vision | Foundation |
| MOD-SUPPORT-01 | Support Circles: extra moderation, anonymity, crisis detection | Explicit functional | Vision | Foundation |
| MOD-CRISIS-01 | Crisis protocol: resources, soft-flag, moderator notify, no auto-ban | Security/privacy | Vision | Foundation |
| MOD-REPORT-01 | User content reporting | Explicit functional | Vision | Foundation |
| MOD-BLOCK-01 | Block and mute users | Explicit functional | Vision | Foundation |
| MOD-APPEAL-01 | Appeals and explanation on moderation actions | Explicit functional | Vision | Foundation |

### Engagement and Well-Being (§11)

| ID | Requirement | Classification | DesignPhase | AuditPriority |
|----|-------------|----------------|-------------|---------------|
| ENG-LOOP-01 | Daily loop with natural exit ("you're caught up") | Design principle | Vision | Foundation |
| ENG-LOOP-02 | Weekly loop: challenges, ETS report, spotlights | Explicit functional | Vision | Deferred |
| ENG-REENG-01 | Day 7/14/30+ warm re-engagement without guilt | Explicit functional | Vision | Foundation |
| ENG-REENG-02 | Never streak-shaming or guilt trips | Design principle | Vision | Foundation |
| ENG-REST-01 | Rest Mode: pause streak, keep status, mute notifications | Explicit functional | Vision | Foundation |
| ENG-BURNOUT-01 | Burnout detection and lighter challenges | AI/moderation | Vision | Deferred |

### Emotionally Aware UX (§12)

| ID | Requirement | Classification | DesignPhase | AuditPriority |
|----|-------------|----------------|-------------|---------------|
| UX-MOOD-01 | UI adapts to user sentiment (calmer/celebratory) | UI/UX | Vision | Deferred |
| UX-METER-01 | Group emotion meters | UI/UX | Vision | Deferred |
| UX-NOTIF-01 | Sentiment-driven wellness notifications | UI/UX | Vision | Deferred |
| UX-REC-01 | Supportive content recommendations by mood | UI/UX | Vision | Deferred |
| UX-A11Y-01 | Multilingual, assistive tech, text resize, minor protections | UI/UX | Vision | Foundation |

### Privacy, Security and Ethics (§13)

| ID | Requirement | Classification | DesignPhase | AuditPriority |
|----|-------------|----------------|-------------|---------------|
| PRIV-MIN-01 | Minimum necessary data collection | Security/privacy | Vision | Foundation |
| PRIV-EXPORT-01 | Full data export (profile, XP, clips, collections, journal) | Security/privacy | Vision | Foundation |
| PRIV-DELETE-01 | Full account deletion within 30 days | Security/privacy | Vision | Foundation |
| PRIV-VIS-01 | Profile visibility: Public/Guild/Private | Security/privacy | Vision | Foundation |
| PRIV-SCORE-01 | Contribution Score show/hide/range control | Security/privacy | Vision | Foundation |
| PRIV-JOURNAL-01 | Journal always private | Security/privacy | Vision | Foundation |
| PRIV-AI-01 | Opt-out of AI personalization | Security/privacy | Vision | Foundation |
| PRIV-ANON-01 | Anonymous posting in Support Circles | Security/privacy | Vision | Foundation |
| SEC-HASH-01 | Strong password hashing | Security/privacy | 1 | Roadmap |
| SEC-MFA-01 | Optional MFA | Security/privacy | Vision | Deferred |
| SEC-GDPR-01 | GDPR/CCPA compliance readiness | Security/privacy | Vision | Foundation |
| SEC-XSS-01 | XSS/SQLi protection | Security/privacy | 1 | Roadmap |
| SEC-REPORT-01 | User reporting + admin review | Security/privacy | Vision | Foundation |
| ETH-AI-01 | AI decisions logged, bias audits, human override, labeled output | Security/privacy | Vision | Foundation |

### Moral-Values Foundation (§14)

| ID | Requirement | Classification | DesignPhase | AuditPriority |
|----|-------------|----------------|-------------|---------------|
| MORAL-01 | Values operationalized via XP and badges for prosocial actions | Design principle | Vision | Foundation |

### Technology Stack and Data Model (§15)

| ID | Requirement | Classification | DesignPhase | AuditPriority |
|----|-------------|----------------|-------------|---------------|
| STACK-FE-01 | Next.js/React/TypeScript client | Data-model | Vision | N/A (design only) |
| STACK-BE-01 | Supabase PostgreSQL + Auth + Realtime + Storage | Data-model | Vision | N/A (design only) |
| STACK-RLS-01 | Row-Level Security for data isolation | Security/privacy | Vision | N/A (design only) |
| STACK-AI-01 | Anthropic API for LLM; NLTK/TextBlob → BERT for sentiment | AI/moderation | 3 | Roadmap |
| STACK-JOBS-01 | Background jobs for badges, roles, sentiment snapshots | Data-model | Vision | Foundation |
| STACK-TABLE-01 | Core tables: users, profiles, threads, posts, clips, collections, follows, reactions, notifications, media, trust_events, journal, sentiment, moderation, ripple | Data-model | 1–3 | Roadmap |
| STACK-IDX-01 | Indexes for threads, trust events, sentiment ranking, clips, search | Data-model | Vision | Foundation |

### Phased Implementation Roadmap (§16)

| ID | Requirement | Classification | DesignPhase | AuditPriority |
|----|-------------|----------------|-------------|---------------|
| ROAD-P1-AUTH | User authentication | Explicit functional | 1 | Roadmap |
| ROAD-P1-THREAD | Threads and replies | Explicit functional | 1 | Roadmap |
| ROAD-P1-CLIP | Clip-to-vault | Explicit functional | 1 | Roadmap |
| ROAD-P1-COL | Basic collections | Explicit functional | 1 | Roadmap |
| ROAD-P1-HOME | Basic home page | Explicit functional | 1 | Roadmap |
| ROAD-P2-NOTE | Clip notes/tags | Explicit functional | 2 | Roadmap |
| ROAD-P2-COLVIS | Public/private collections | Explicit functional | 2 | Roadmap |
| ROAD-P2-FOLLOW | Follow users/threads | Explicit functional | 2 | Roadmap |
| ROAD-P2-TAG | Tag browsing + basic search | Explicit functional | 2 | Roadmap |
| ROAD-P2-NOTIF | Notification system | Explicit functional | 2 | Roadmap |
| ROAD-P3-SUM | Thread summaries | Explicit functional | 3 | Roadmap |
| ROAD-P3-SEM | Semantic search | Explicit functional | 3 | Roadmap |
| ROAD-P4-FORK | Structured/forkable threads | Explicit functional | 4 | Roadmap |
| ROAD-P4-ART | Collections-to-articles | Explicit functional | 4 | Roadmap |
| ROAD-P4-REP | Curator reputation | Explicit functional | 4 | Roadmap |
| ROAD-P4-HOME | Drag-and-drop home customization | Explicit functional | 4 | Roadmap |

**Total checklist rows:** 147

---

## 1.5 Stage 1 Exit Criteria

- [x] Every design §1–16 section represented
- [x] Every row classified
- [x] DesignPhase and AuditPriority assigned
- [x] 13 open design decisions logged (not silently resolved)
- [x] P1–P7 principles mapped to requirement IDs
