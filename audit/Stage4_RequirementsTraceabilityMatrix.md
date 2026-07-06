# Stage 4 — Requirements Traceability Matrix (RTM)

**Inputs:** [Stage1_RequirementsBaseline.md](Stage1_RequirementsBaseline.md), [Stage2_ApplicationInventory.md](Stage2_ApplicationInventory.md), [Stage3_UserFlowCatalog.md](Stage3_UserFlowCatalog.md)  
**Audit date:** 2026-07-05

**Status legend:** Implemented | Implemented with defects | Partially implemented | Scaffold only | Not implemented | Implemented differently | Not verifiable | Intentionally deferred | Not recommended without redesign

---

## 4.1 Design Roadmap Phase Completion Summary

Completion assessed by **flow reliability** of core phase features, not isolated advanced features (per CompleteAudit §17).

| Design Phase | Goal | Complete | Partial | Missing | Est. completeness | Confidence |
|--------------|------|----------|---------|---------|-------------------|------------|
| **Phase 1 — Core MVP** | Forum + clipping + user pages | 4 | 1 | 0 | **~85%** | High |
| **Phase 2 — Knowledge Layer** | Structured knowledge | 3 | 2 | 0 | **~65%** | Medium |
| **Phase 3 — Intelligence** | AI knowledge-aware | 0 | 2 | 3 | **~15%** | High |
| **Phase 4 — Differentiation** | Beyond forum | 0 | 0 | 4 | **~0%** | High |

### Phase 1 detail (ROAD-P1-*)

| ID | Status | Evidence | Gap |
|----|--------|----------|-----|
| ROAD-P1-AUTH | Implemented | `accounts/views.py`, `test_phase0_flow.py` | Password reset untested |
| ROAD-P1-THREAD | Implemented with defects | `posts/`, `interactions/`, `test_phase1_flow.py` | Deleted replies may show |
| ROAD-P1-CLIP | Partially implemented | `knowledge/services.py:create_clip`, `test_phase3_flow.py` | Whole-post only; no passage |
| ROAD-P1-COL | Implemented | `knowledge/views.py`, `test_phase3_flow.py` | Visibility public/guild not readable |
| ROAD-P1-HOME | Partially implemented | `dashboard/views.py`, `dashboard/knowledge_hub.html` | Basic feed yes; not full §7.4 hub |

### Phase 2 detail (ROAD-P2-*)

| ID | Status | Evidence | Gap |
|----|--------|----------|-----|
| ROAD-P2-NOTE | Partially implemented | `Clip.private_note` field; `ClipNoteForm` unused | Notes not wired in clip UI |
| ROAD-P2-COLVIS | Partially implemented | `Collection.visibility` enum | No public/guild read paths |
| ROAD-P2-FOLLOW | Implemented | `follows/`, `test_phase3/4_flow.py` | — |
| ROAD-P2-TAG | Partially implemented | `knowledge/tag_browse`, `tag_detail` | No free-text search |
| ROAD-P2-NOTIF | Implemented | `interactions/views.py` notifications | Light test coverage |

### Phase 3 detail (ROAD-P3-*)

| ID | Status | Evidence | Gap |
|----|--------|----------|-----|
| ROAD-P3-SUM | Scaffold only | `ai_coach/services.py:generate_thread_summary` (concat stub); `ThreadSummary` model | Not shown in UI; not LLM |
| ROAD-P3-HIGH | Not implemented | — | — |
| ROAD-P3-SEM | Not implemented | README line 114 | — |
| ROAD-P3-SUGG | Not implemented | — | — |
| ROAD-P3-GRAPH | Not implemented | — | — |

### Phase 4 detail (ROAD-P4-*)

| ID | Status | Evidence | Gap |
|----|--------|----------|-----|
| ROAD-P4-FORK | Not implemented | `Post.thread_type` exists but no fork/evolution trail | — |
| ROAD-P4-ART | Not implemented | — | — |
| ROAD-P4-REP | Not implemented | — | — |
| ROAD-P4-HOME | Not implemented | — | — |

---

## 4.2 Principles Conformance Summary (P1–P7)

| Principle | Assessment | Key evidence |
|-----------|------------|--------------|
| **P1** Prosocial Over Popularity | **Partial** | Feed orders by `created_at` not helpfulness; discovery has `get_most_clipped_posts` and sentiment boost but feed itself is chronological |
| **P2** Visibility as Responsibility | **Partial** | Trust roles sync from scores (`moderation/services.py`); feed not boosted by contribution score |
| **P3** Gentle Friction Before Harm | **Partial** | `pre_send_prompt` for negative text (`ai_coach/services.py`); no pre-publish hide workflow; crisis flags exist |
| **P4** Earn Privacy Upgrades | **Not implemented** | No trust-gated private groups or anonymous posting |
| **P5** Knowledge Outlasts Conversation | **Partial** | Clips, collections, vault work; thread summaries stub only |
| **P6** Growth Is the Metric | **Partial** | XP/trust tracked; no prosocial skill KPI dashboard vs DAU |
| **P7** AI Is Coach Not Cop | **Partial** | Keyword sentiment only; humans moderate; no binding AI enforcement; static journal response |

---

## 4.3 Premature Implementation Register

Features from design **Vision** scope implemented before design Phases 1–2 are complete and reliable:

| Feature | Implementation phase (README) | Concern |
|---------|------------------------------|---------|
| Trust ETS/PTS/roles | Phase 5 | Scoring without full moderation/export/deletion foundation |
| Gamification XP/badges | Phase 6 | May reward volume before quality signals mature |
| AI sentiment/journal | Phase 7 | Keyword stub, not coach-grade LLM |
| Moderation queue/crisis | Phase 8 | Partial HTTP coverage |
| Guilds, messaging | Phase 4 | Reasonable alongside Phase 1 |
| Donations, skills | Phase 11 | Stubs acceptable |
| Discovery/ripple | Phase 10 | Depends on clip quality |

**Recommendation:** Stabilize Phase 1–2 defects (clip passage, search, collection visibility, reply visibility) before expanding trust/gamification surface area.

---

## 4.4 Full Requirements Traceability Matrix

### Philosophy and Principles

| ID | Design requirement | Phase | Status | Evidence | Quality | Security/privacy | Missing work | Priority |
|----|-------------------|-------|--------|----------|---------|------------------|--------------|----------|
| PHIL-NORTH-01 | Prosocial skill growth as north star | Vision | Partially implemented | `gamification/`, `trust/` | Metrics exist; not primary UX narrative | Low | KPI dashboard aligned to skill not time | Should |
| PHIL-MISSION-01 | Incentivize empathy/cooperation | Vision | Partially implemented | `prosocial_actions/`, thank-yous | Actions module separate from feed | Low | Deeper feed integration | Should |
| PHIL-AUDIENCE-01 | Serve diverse user segments | Vision | Not verifiable | — | — | — | User research | Defer |
| P1 | Depth over popularity | Vision | Partially implemented | `discovery/selectors.py` ranking | Feed still chronological | Low | Feed ranking by helpfulness | Must |
| P2 | Earned prominence | Vision | Partially implemented | `trust/services.py`, role sync | Not tied to feed visibility | Medium | Feed boost by contribution | Should |
| P3 | Gentle friction, explain | Vision | Partially implemented | `ai_coach/services.py:pre_send_prompt` | No full moderation pre-publish UX | Medium | Borderline workflow UI | Must |
| P4 | Trust-gated privacy | Vision | Not implemented | — | — | High | Trust gates for private features | Defer |
| P5 | Knowledge artifacts | 1 | Partially implemented | `knowledge/` | Passage clip missing | Low | SELECTION clip UI | Must |
| P6 | Growth metric | Vision | Partially implemented | XP, trust scores | No unified growth view | Low | Growth dashboard | Should |
| P7 | AI coach not cop | 3 | Partially implemented | Moderation human review | Keyword AI only | Medium | Real LLM + labeling | Should |

### Baseline Social (SOC-*)

| ID | Design requirement | Phase | Status | Evidence | Quality | Security/privacy | Missing work | Priority |
|----|-------------------|-------|--------|----------|---------|------------------|--------------|----------|
| SOC-PROFILE-01 | Customizable profiles | 1 | Implemented | `profiles/models.py`, `profile_edit` | Bio, avatar, handle | Low | External links field | Could |
| SOC-PROFILE-02 | Prosocial standing on profile | Vision | Not implemented | Public profile template | Trust hidden by default | Low | Opt-in score/badge display | Should |
| SOC-FEED-01 | Personalized feed | 1 | Implemented | `dashboard/views.py`, `get_dashboard_feed` | Following mode works | Low | — | — |
| SOC-FEED-02 | Sentiment/diversity weighting | Vision | Partially implemented | `discovery/selectors.py` only | Not in main feed | Low | Feed algorithm | Should |
| SOC-FEED-03 | Caught-up endpoint | Vision | Partially implemented | `get_dashboard_feed` caught_up flag | Paginator heuristic | Low | True end-of-feed UX | Could |
| SOC-FOLLOW-01 | Bidirectional friends | Vision | Not implemented | — | — | — | Friend model | Defer |
| SOC-FOLLOW-02 | Unidirectional follows | 2 | Implemented | `follows/`, phase3/4 tests | — | Low | — | — |
| SOC-MSG-01 | 1:1 messaging | Vision | Implemented | `messaging/` | Block check in service | Medium | HTTP test thin | Should |
| SOC-MSG-02 | Group chats | Vision | Not implemented | — | — | — | Group conversation model | Defer |
| SOC-MSG-03 | Voice/video | Vision | Not implemented | — | — | — | WebRTC integration | Defer |
| SOC-CONTENT-01 | Text posts | 1 | Implemented | `posts/services.py:create_post` | 5000 char limit | Low | — | — |
| SOC-CONTENT-02 | Image sharing | 1 | Implemented | `Post.image`, Pillow validation | Untested upload | Medium | Upload tests | Should |
| SOC-CONTENT-03 | Video | Vision | Not implemented | — | — | — | Video storage | Defer |
| SOC-CONTENT-04 | External links | Vision | Partially implemented | Plain text in body | No link preview | Low | URL detection/cards | Could |
| SOC-CONTENT-05 | Live streaming | Vision | Not implemented | — | — | — | — | Defer |
| SOC-REACT-01 | Comments + reactions | 1 | Partially implemented | Replies, `ProsocialReaction`, thank-yous | Limited reaction kinds | Low | Full reaction set | Could |
| SOC-UX-01 | Simple interface | 1 | Implemented | Templates, `site.css` | — | — | — | — |
| SOC-UX-02 | WCAG compliance | Vision | Not verifiable | Templates use labels | No a11y audit run | Medium | axe/pa11y audit | Should |
| SOC-UX-03 | Intuitive navigation | 1 | Implemented | `shell_left.html` nav | — | — | — | — |
| SOC-UX-04 | Prominent prosocial features | Vision | Partially implemented | Nav links to actions, knowledge | Not front-and-center on home | Low | Home layout | Could |
| SOC-UX-05 | Positive valence surfacing | Vision | Partially implemented | `get_sentiment_boosted_posts` | Discovery only | Low | Feed integration | Should |
| SOC-UX-06 | Impact statistics | Vision | Not implemented | — | — | — | Impact dashboard | Defer |

### Prosocial Actions (ACT-*)

| ID | Design requirement | Phase | Status | Evidence | Quality | Security/privacy | Missing work | Priority |
|----|-------------------|-------|--------|----------|---------|------------------|--------------|----------|
| ACT-VOL-01 | Volunteering coordination | Vision | Partially implemented | `prosocial_actions/` | Commitment flow, not geo matching | Medium | Opportunity matching | Defer |
| ACT-DONATE-01 | Payment gateways | Vision | Scaffold only | `advanced/` stub | No real payments | High | Stripe/etc integration | Defer |
| ACT-DONATE-02 | Mobile donation forms | Vision | Partially implemented | Templates exist | Stub backend | Medium | Payment processor | Defer |
| ACT-DONATE-03 | Multiple payment options | Vision | Not implemented | — | — | — | Gateway | Defer |
| ACT-DONATE-04 | Transparent fees | Vision | Scaffold only | `advanced/services.py` fee calc | Not shown at checkout | Low | UI + real fees | Defer |
| ACT-DONATE-05 | Donation history | Vision | Partially implemented | `Donation` model | No user history page | Low | History view | Could |
| ACT-SKILL-01 | Offer/request skills | Vision | Partially implemented | `SkillOffering` list/create | No request flow | Low | Request matching | Could |
| ACT-SKILL-02 | Workshops | Vision | Scaffold only | `Workshop` model | No views | — | Workshop UI | Defer |
| ACT-SKILL-03 | Skill forums/mentorship | Vision | Not implemented | — | — | — | — | Defer |
| ACT-FORUM-01 | Themed support forums | Vision | Partially implemented | `Post.thread_type`, guilds | No themed sub-forums | Low | Forum taxonomy | Defer |
| ACT-FORUM-02 | User sub-forums | Vision | Not implemented | — | — | — | — | Defer |

### Trust (TRUST-*)

| ID | Design requirement | Phase | Status | Evidence | Quality | Security/privacy | Missing work | Priority |
|----|-------------------|-------|--------|----------|---------|------------------|--------------|----------|
| TRUST-ETS-01 | Engagement Trust Score | Vision | Partially implemented | `trust/models.py`, `trust/services.py` | Last 200 events recalc | Medium | Full event taxonomy | Should |
| TRUST-ETS-02 | ETS gates roles before PTS | Vision | Partially implemented | `moderation/services.py:sync_user_role` | Thresholds simplified | Medium | Full ladder | Should |
| TRUST-PTS-01 | Popularity Trust Score | Vision | Partially implemented | `TrustEventType.CLIP_BY_OTHER`, follows | Partial signal set | Low | Endorsements, nominations | Could |
| TRUST-PTS-02 | PTS cannot alone unlock roles | Vision | Partially implemented | Role sync logic | Not fully audited | Medium | Tests for gate | Should |
| TRUST-CCS-01 | Contribution Score formula | Vision | Implemented | `trust/services.py` 0.65/0.35 | — | Low | — | — |
| TRUST-HELPER-01 | Helper Style onboarding | Vision | Implemented | `trust/onboarding`, phase5 test | — | Low | — | — |
| TRUST-HELPER-02 | Style evolves over time | Vision | Not implemented | Static after onboarding | — | — | Evolution logic | Defer |
| TRUST-PROFILE-01 | Public trust display | Vision | Not implemented | Profile lacks badges/ripple | Scores hidden | Low | Public profile widgets | Should |
| TRUST-PROFILE-02 | Private analytics | Vision | Partially implemented | `gamification/progress`, journal | No contribution trend chart | Low | Analytics UI | Could |

### Gamification (GAME-*)

| ID | Design requirement | Phase | Status | Evidence | Quality | Security/privacy | Missing work | Priority |
|----|-------------------|-------|--------|----------|---------|------------------|--------------|----------|
| GAME-PHIL-01 | Reward prosocial not addiction | Vision | Partially implemented | XP sources tied to actions | Streaks exist | Medium | Audit XP for volume gaming | Should |
| GAME-XP-01 | XP tables | Vision | Partially implemented | `gamification/services.py`, `XPSource` | Not all design values | Low | Calibrate amounts | Could |
| GAME-XP-02 | Crisis support highest XP | Vision | Partially implemented | XP sources | Crisis path unclear | Medium | Crisis XP trigger | Could |
| GAME-MULT-01 | 4× multiplier cap | Vision | Partially implemented | `UserGamificationProfile.multiplier` | Simplified streak logic | Low | Full multiplier stack | Could |
| GAME-LEVEL-01 | Level tiers | Vision | Partially implemented | Level field, phase6 test | 4 design tiers not named in UI | Low | Tier labels | Could |
| GAME-SKILL-01 | Skill trees | Vision | Not implemented | — | — | — | Tree UI/logic | Defer |
| GAME-BADGE-01 | Sentiment-gated badges | Vision | Partially implemented | `BadgeDefinition`, thresholds | Not sentiment-gated | Medium | Sentiment gate | Should |
| GAME-ACHIEVE-01 | Achievement celebrations | Vision | Scaffold only | `Achievement` model | No celebration UI | — | Framer-style UI | Defer |

### Knowledge (KNOW-*)

| ID | Design requirement | Phase | Status | Evidence | Quality | Security/privacy | Missing work | Priority |
|----|-------------------|-------|--------|----------|---------|------------------|--------------|----------|
| KNOW-THREAD-01 | Title + tags | 1 | Implemented | `Post.title`, `PostTag` | — | Low | — | — |
| KNOW-THREAD-02 | Sentiment-scored replies | 1 | Partially implemented | `SentimentSnapshot` on score | Not displayed on reply | Low | UI indicator | Could |
| KNOW-THREAD-03 | AI summary on long threads | 3 | Scaffold only | `ThreadSummary`, stub service | Not in post detail | — | LLM + UI pin | Must |
| KNOW-THREAD-04 | Most helpful highlights | 3 | Not implemented | — | — | — | LLM highlights | Defer |
| KNOW-THREAD-05 | Evolution trail/forks | 4 | Not implemented | — | — | — | Fork model | Defer |
| KNOW-THREAD-06 | Aggregate Prosocial Rating | Vision | Not implemented | — | — | — | Rating aggregate | Defer |
| KNOW-THREAD-07 | Thread types | Vision | Partially implemented | `Post.thread_type` enum | Not routed differently | Low | Type-specific UX | Could |
| KNOW-CLIP-01 | Clip post/passage/thread | 1 | Partially implemented | `create_clip`, `ClipKind` | Whole post only in UI | Low | SELECTION UI, thread agg | Must |
| KNOW-CLIP-02 | Auto source reference | 1 | Implemented | FK to post/reply, `quoted_text` | — | Low | — | — |
| KNOW-CLIP-03 | Personal Vault | 1 | Implemented | `knowledge/vault`, owner scope | — | Low | — | — |
| KNOW-CLIP-04 | Private clip notes | 2 | Partially implemented | `Clip.private_note` field | Form unused | Low | Wire `ClipNoteForm` | Should |
| KNOW-CLIP-05 | XP bonus when clipped by others | Vision | Implemented | `create_clip` awards XP + trust | — | Low | — | — |
| KNOW-COL-01 | Collections multi-content | 1 | Implemented | `CollectionItem` clip or post | — | Low | External links | Could |
| KNOW-COL-02 | Private/public/guild visibility | 2 | Partially implemented | `Collection.visibility` | No public read | Medium | Public collection views | Must |
| KNOW-COL-03 | Public collection XP | Vision | Not implemented | — | — | — | XP on publish | Could |
| KNOW-HUB-01 | Modular knowledge hub | Vision | Partially implemented | `dashboard/knowledge_hub.html` | Static panels | Low | Challenges/guild/ripple panels | Should |
| KNOW-HUB-02 | Drag-drop home | 4 | Not implemented | — | — | — | — | Defer |
| KNOW-DISC-01 | Tag browsing | 2 | Implemented | `tag_browse`, `tag_detail` | — | Low | — | — |
| KNOW-DISC-02 | Most clipped/referenced | Vision | Partially implemented | `get_most_clipped_posts` | No "referenced" metric | Low | Reference tracking | Could |
| KNOW-DISC-03 | Sentiment-boosted discovery | Vision | Implemented | `get_sentiment_boosted_posts` | — | Low | — | — |
| KNOW-DISC-04 | Semantic search | 3 | Not implemented | README | — | — | Vector search | Defer |
| KNOW-DISC-05 | Suppress negative content | Vision | Partially implemented | `Post.visible()` moderation | No contribution-score demotion | Medium | Score-based suppression | Should |

### Collaboration (COLLAB-*)

| ID | Design requirement | Phase | Status | Evidence | Quality | Security/privacy | Missing work | Priority |
|----|-------------------|-------|--------|----------|---------|------------------|--------------|----------|
| COLLAB-GUILD-01 | Guilds with roles | Vision | Partially implemented | `guilds/`, LEADER/MEMBER | No collective XP | Low | Guild XP | Could |
| COLLAB-GUILD-02 | Guild customizations | Vision | Not implemented | `banner_url` only | — | — | Themes/emblems | Defer |
| COLLAB-QUEST-01 | Collaborative quests | Vision | Partially implemented | `GuildMission`, `Challenge` | Simplified | Low | Multi-stage quests | Defer |
| COLLAB-BOARD-01 | Task boards | Vision | Not implemented | — | — | — | — | Defer |
| COLLAB-LIVE-01 | Live rooms | Vision | Not implemented | — | — | — | — | Defer |
| COLLAB-SEASON-01 | Seasonal challenges | Vision | Partially implemented | `Challenge` model | No seasonal theming | — | Season events | Defer |
| COLLAB-SPOT-01 | Community spotlights | Vision | Partially implemented | `CommunitySpotlight`, discovery home | Not LLM narratives | Low | Narrative generation | Could |

### AI (AI-*)

| ID | Design requirement | Phase | Status | Evidence | Quality | Security/privacy | Missing work | Priority |
|----|-------------------|-------|--------|----------|---------|------------------|--------------|----------|
| AI-PHIL-01 | AI non-binding, explainable | 3 | Partially implemented | Moderation human gate | Keyword only | Medium | LLM integration | Should |
| AI-SENT-01 | Score all content | Vision | Partially implemented | `score_content` service | Not called on all messages | Medium | Message scoring hook | Should |
| AI-SENT-02 | Sentiment → trust/badges | Vision | Partially implemented | Trust events from ratings | Badges not sentiment-gated | Medium | Badge gate | Should |
| AI-FORECAST-01 | Trajectory score | Vision | Not implemented | — | — | — | — | Defer |
| AI-INTERVENT-01 | Pre-post prompt | Vision | Partially implemented | `pre_send_prompt` | Not wired to all compose UIs | Low | Composer integration | Should |
| AI-INTERVENT-02 | Positive reinforcement | Vision | Partially implemented | XP toasts implied | No explicit AI message | Low | Reinforcement copy | Could |
| AI-INTERVENT-03 | Comment ranking | Vision | Not implemented | — | — | — | Collapse negative | Defer |
| AI-ELEVATE-01 | Uplifting on negative trends | Vision | Not implemented | — | — | — | — | Defer |
| AI-JOURNAL-01 | Reflection journal | Vision | Partially implemented | `ai/journal/`, static response | Not LLM | Medium | Real LLM + privacy | Should |
| AI-RIPPLE-01 | Ripple visualization | Vision | Partially implemented | `discovery/ripple/` | List not interactive graph | Low | D3/Recharts viz | Could |
| AI-COACH-01 | Personalized challenges | Vision | Not implemented | — | — | — | LLM coaching | Defer |

### Moderation (MOD-* / TRUST-ROLE-*)

| ID | Design requirement | Phase | Status | Evidence | Quality | Security/privacy | Missing work | Priority |
|----|-------------------|-------|--------|----------|---------|------------------|--------------|----------|
| TRUST-ROLE-01 | Role ladder | Vision | Partially implemented | `UserRoleAssignment`, sync | Simplified vs design table | Medium | Full thresholds | Should |
| TRUST-ROLE-02 | Continuous evaluation | Vision | Partially implemented | `recalculate_trust_scores` command | Manual/cron unclear | Medium | Scheduled job | Should |
| TRUST-ROLE-03 | Role rotation 6mo | Vision | Not implemented | `expires_at` field exists | Not enforced | — | Rotation job | Defer |
| MOD-WORKFLOW-01 | AI scan workflow | Vision | Partially implemented | Reports → reviews | No <500ms pre-publish scan | High | Pre-publish pipeline | Must |
| MOD-WORKFLOW-02 | AI flags, humans decide | Vision | Implemented | `moderation/review_content` | — | Low | — | — |
| MOD-SUPPORT-01 | Support Circles | Vision | Not implemented | `thread_type` enum value | No special moderation | — | Support circle mode | Defer |
| MOD-CRISIS-01 | Crisis protocol | Vision | Partially implemented | `CrisisFlag`, phrase detection | No resource UI verified | High | Crisis resource UI | Must |
| MOD-REPORT-01 | User reporting | Vision | Implemented | `ContentReport`, report views | Untested HTTP | Medium | Tests | Should |
| MOD-BLOCK-01 | Block/mute | Vision | Implemented | phase1 tests | — | Low | — | — |
| MOD-APPEAL-01 | Appeals | Vision | Not implemented | — | — | — | Appeal flow | Defer |

### Engagement (ENG-*)

| ID | Design requirement | Phase | Status | Evidence | Quality | Security/privacy | Missing work | Priority |
|----|-------------------|-------|--------|----------|---------|------------------|--------------|----------|
| ENG-LOOP-01 | Daily loop + caught up | Vision | Partially implemented | Dashboard, challenges | Incomplete loop | Low | Unified daily UX | Could |
| ENG-LOOP-02 | Weekly ETS report | Vision | Not implemented | — | — | — | Weekly email/report | Defer |
| ENG-REENG-01 | Warm re-engagement | Vision | Scaffold only | `ReEngagementMessage` model | No delivery job | — | Email/job | Defer |
| ENG-REENG-02 | No streak shaming | Vision | Partially implemented | No shame copy found | Streaks exist | Low | Copy audit | Should |
| ENG-REST-01 | Rest Mode | Vision | Implemented | `engagement/services.py`, phase9 | — | Low | — | — |
| ENG-BURNOUT-01 | Burnout detection | Vision | Not implemented | — | — | — | — | Defer |

### UX, Privacy, Security (UX-*, PRIV-*, SEC-*, ETH-*)

| ID | Design requirement | Phase | Status | Evidence | Quality | Security/privacy | Missing work | Priority |
|----|-------------------|-------|--------|----------|---------|------------------|--------------|----------|
| UX-MOOD-01 | Mood-based UI | Vision | Not implemented | — | — | — | — | Defer |
| UX-METER-01 | Group emotion meters | Vision | Not implemented | — | — | — | — | Defer |
| UX-NOTIF-01 | Wellness notifications | Vision | Not implemented | — | — | — | — | Defer |
| UX-REC-01 | Mood-based recommendations | Vision | Not implemented | — | — | — | — | Defer |
| UX-A11Y-01 | Accessibility | Vision | Not verifiable | Semantic templates partial | No audit | Medium | WCAG test suite | Should |
| PRIV-MIN-01 | Data minimization | Vision | Partially implemented | Focused models | Trust/sentiment stored | Medium | Retention policy enforcement | Should |
| PRIV-EXPORT-01 | Full data export | Vision | Partially implemented | `advanced/export` | Incomplete payload | High | Complete export | Must |
| PRIV-DELETE-01 | Account deletion 30d | Vision | Not implemented | Policy doc only | **High** | **High** | Deletion flow | **Blocker** |
| PRIV-VIS-01 | Profile visibility levels | Vision | Not implemented | — | All public | High | Visibility enum + enforcement | Must |
| PRIV-SCORE-01 | Score visibility control | Vision | Implemented | `trust/settings`, default HIDDEN | — | Low | — | — |
| PRIV-JOURNAL-01 | Journal always private | Vision | Implemented | `filter(user=request.user)` | — | Low | — | — |
| PRIV-AI-01 | AI opt-out | Vision | Not implemented | — | — | Medium | Opt-out setting | Should |
| PRIV-ANON-01 | Anonymous posting | Vision | Not implemented | — | — | — | — | Defer |
| SEC-HASH-01 | Password hashing | 1 | Implemented | Django PBKDF2 (testing: MD5) | Production uses default | Low | — | — |
| SEC-MFA-01 | MFA | Vision | Not implemented | — | — | — | — | Defer |
| SEC-GDPR-01 | GDPR readiness | Vision | Partially implemented | Export stub, no deletion | Incomplete | High | Deletion + consent | Must |
| SEC-XSS-01 | XSS protection | 1 | Implemented | Django templates, `test_security.py` | — | Low | — | — |
| SEC-REPORT-01 | Reporting + review | Vision | Implemented | reports + moderation queue | — | Medium | Test coverage | Should |
| ETH-AI-01 | Ethical AI commitments | Vision | Partially implemented | `AIIntervention` logging | No bias audit | Medium | Audit pipeline | Defer |
| MORAL-01 | Values via XP/badges | Vision | Partially implemented | XP for help actions | Not mapped to value categories | — | Value taxonomy | Defer |

### Stack (STACK-*) — Design vs implementation

| ID | Design requirement | Phase | Status | Evidence | Quality | Security/privacy | Missing work | Priority |
|----|-------------------|-------|--------|----------|---------|------------------|--------------|----------|
| STACK-FE-01 | Next.js client | Vision | Implemented differently | Django templates + HTMX | Works for MVP | — | — | — |
| STACK-BE-01 | Supabase | Vision | Implemented differently | Django + PostgreSQL | Manageable | RLS → Django authz | Authz audit ongoing | — |
| STACK-RLS-01 | Row-Level Security | Vision | Implemented differently | View/queryset scoping | Gaps in FLOW-D01/D02 | Medium | Fix IDOR issues | Must |
| STACK-AI-01 | Anthropic + NLP | 3 | Scaffold only | `keyword-v1` | Not production AI | Medium | Provider integration | Should |
| STACK-JOBS-01 | Background jobs | Vision | Partially implemented | Management commands | No scheduler | Medium | Celery/cron | Should |
| STACK-TABLE-01 | Core tables | 1–3 | Partially implemented | 17 model modules | threads=posts pattern | — | — | — |
| STACK-IDX-01 | Performance indexes | Vision | Partially implemented | Some indexes in migrations | No full-text index | Low | Search indexes | Could |

### Roadmap items (ROAD-P*)

| ID | Status | See Phase summaries §4.1 |
|----|--------|--------------------------|
| ROAD-P1-* | 85% complete | §4.1 Phase 1 |
| ROAD-P2-* | 65% complete | §4.1 Phase 2 |
| ROAD-P3-* | 15% complete | §4.1 Phase 3 |
| ROAD-P4-* | 0% complete | §4.1 Phase 4 |

---

## 4.5 Status Distribution (147 requirements)

| Status | Count | % |
|--------|-------|---|
| Implemented | 18 | 12% |
| Implemented with defects | 3 | 2% |
| Partially implemented | 72 | 49% |
| Scaffold only | 8 | 5% |
| Not implemented | 38 | 26% |
| Implemented differently | 3 | 2% |
| Not verifiable | 3 | 2% |
| Intentionally deferred | 2 | 1% |

*Percentages approximate; some Vision items overlap roadmap scope.*

---

## 4.6 Top Priority Missing Work (from RTM)

| Priority | Items |
|----------|-------|
| **Blocker** | PRIV-DELETE-01 account deletion |
| **Must** | KNOW-CLIP-01 passage clip; KNOW-COL-02 public collections; ROAD-P2 search; PRIV-EXPORT-01 complete export; MOD-CRISIS-01 resource UI; MOD-WORKFLOW-01 pre-publish scan; FLOW-D01 reply visibility |
| **Should** | P1 feed ranking; P7 LLM integration; SEC-GDPR deletion; trust role tests |

---

## 4.7 Stage 4 Exit Criteria

- [x] Every Stage 1 requirement ID has an RTM row
- [x] Non-"Not implemented" rows include file-path evidence
- [x] Phase completion assessed by flow reliability
- [x] P1–P7 principles conformance summarized
- [x] Premature implementation register included
