# Stage 5 — Core Prosocial Principles Evaluation

**Method:** CompleteAudit §5 — behavioral assessment of P1–P7 against live code paths
**Inputs:** [Stage1_RequirementsBaseline.md](Stage1_RequirementsBaseline.md), [Stage4_RequirementsTraceabilityMatrix.md](Stage4_RequirementsTraceabilityMatrix.md)
**Audit date:** 2026-07-05
**Application:** [prosocial_platform](../prosocial_platform)
**Test baseline:** 80 passed (`pytest tests/`)

---

## 5.1 Evaluation Method

Each principle is assessed by tracing **what the product actually rewards, surfaces, or restricts** — not whether related models or routes exist. Evidence cites file paths and symbols. Conformance ratings: **Aligned** | **Partial** | **Not aligned** | **Not applicable**.

---

## 5.2 P1 — Prosocial Over Popularity

**Design intent (P1, SOC-FEED-02, TRUST-ETS-02):** Helpful depth outweighs shallow likes, follower count, posting frequency, and controversy.

### Observed behavior

| Surface | What is rewarded / ranked | Evidence |
|---------|---------------------------|----------|
| Main feed | Chronological order (`-created_at`) | `apps/posts/selectors.py:get_dashboard_feed` L21 |
| Following feed | Same chronological order with boundary filters | `get_dashboard_feed` L29–35 |
| Thank-yous | Count displayed; toggle creates notification; **no trust/XP** | `apps/interactions/services.py:toggle_thank_you`, `posts/views.py:post_detail` L42–46 |
| Peer ratings | ETS weight +2.0 per positive rating; **no UI on threads** | `apps/trust/services.py:create_peer_rating`, `apps/trust/forms.py` (positive dims only) |
| ProsocialReaction | Model exists; **not wired to views** | `apps/interactions/models.py:ProsocialReaction`, `test_phase4_flow.py` (ORM only) |
| Discovery | Clip-count ranking + sentiment-boosted lists | `apps/discovery/selectors.py:get_most_clipped_posts`, `get_sentiment_boosted_posts` |
| Ranked feed | Clip-count ordering; trust profile loaded but unused in sort | `get_prosocial_ranked_feed` L37–42 |
| XP | Clip bonus (25), reflection (20), daily challenge (30); streak multipliers up to 2× | `apps/gamification/services.py:award_xp`, `apps/knowledge/services.py:create_clip` L88–92 |

### Confirmed alignment

- Discovery and clip-based ranking favor content others found worth saving (clip count proxy for helpfulness).
- Peer ratings weight constructive dimensions when used.

### Gaps and risks

| ID | Severity | Finding |
|----|----------|---------|
| P1-G01 | **High** | Main feed is purely chronological — posting frequency and recency dominate the home experience. |
| P1-G02 | **Medium** | Thank-yous and `ProsocialReaction` do not feed trust or ranking; popularity signals are disconnected from quality signals. |
| P1-G03 | **Medium** | PTS includes raw follower count (`followers × 2` in `recalculate_trust_scores` L74–76), partially re-introducing popularity weighting. |
| P1-G04 | **Low** | `get_prosocial_ranked_feed` is computed in `discovery/views.py` but not rendered in `discovery/home.html`. |

**Conformance:** **Partial**
**Fix priority:** Should — wire helpful signals into feed ranking after Phase 1–2 defects are closed.

---

## 5.3 P2 — Visibility as Responsibility

**Design intent (P2, TRUST-ROLE-01):** Prominence and privileges earned through prosocial behavior; server-enforced authorization.

### Observed behavior

| Mechanism | Behavior | Evidence |
|-----------|----------|----------|
| Platform roles | 9 roles with ETS + contribution thresholds | `apps/moderation/models.py:ROLE_THRESHOLDS` |
| Role evaluation | `evaluate_user_role` picks highest eligible role | `apps/moderation/services.py:L67–72` |
| Role sync | `sync_user_role` deactivates old, creates new assignment | `sync_user_role` L76–84 — **not auto-called after trust recalc** |
| Moderator queue | Gated by `MODERATOR`, `COMMUNITY_GUIDE`, `COMMUNITY_LEADER` | `apps/moderation/views.py:_is_moderator` |
| Feed visibility | Not score-weighted; block/mute/hidden filters only | `apply_user_boundaries_to_feed` |
| Profile badges | Static HTML “Verified helper” in shell | `templates/components/shell_right.html` — not tied to `UserTrustProfile` |
| Score visibility | Default HIDDEN; user can opt into RANGE/EXACT | `apps/trust/models.py:ScoreVisibility`, default HIDDEN |

### Confirmed alignment

- Moderator endpoints use server-side role checks, not client-only hiding.
- ETS must clear threshold before role promotion (`role_eligible` L102–106).

### Gaps and risks

| ID | Severity | Finding |
|----|----------|---------|
| P2-G01 | **High** | Roles do not auto-update when trust scores change — users can remain `NEW_MEMBER` despite qualifying. |
| P2-G02 | **Medium** | Feed does not boost high-contribution authors; visibility is not responsibility-weighted in discovery surfaces. |
| P2-G03 | **Low** | Shell UI misrepresents trust state with static badges. |

**Conformance:** **Partial**
**Fix priority:** Must — auto `sync_user_role` after `recalculate_trust_scores`.

---

## 5.4 P3 — Gentle Friction Before Harm

**Design intent (P3, MOD-WORKFLOW-01, AI-INTERVENT-01):** Soft reflection before harm; never block silently; always explain.

### Observed behavior

| Mechanism | Wired? | Evidence |
|-----------|--------|----------|
| `pre_send_prompt` | **Service only** — keyword sentiment heuristic | `apps/ai_coach/services.py:L46–50` |
| Post/reply compose | No prompt integration | `templates/components/post_composer.html`, `interactions/templates/interactions/reply_form.html` |
| Crisis phrase detection | `flag_crisis_content` exists; **not called on create** | `apps/moderation/services.py:L20–45`; `apps/posts/services.py:create_post` (no call) |
| Content removal | Moderator must supply `explanation`; logged to `TransparencyLogEntry` | `review_content` L49–58 |
| Report flow | Form + `submit_report`; no auto-punishment | `apps/interactions/services.py:submit_report` |
| Block/mute | User-initiated with confirm forms | `interactions/views.py` |

### Confirmed alignment

- No silent auto-removal on AI sentiment alone.
- Moderator review requires explanation text.

### Gaps and risks

| ID | Severity | Finding |
|----|----------|---------|
| P3-G01 | **High** | Pre-send reflection prompt is not shown to users before posting — P3 core UX missing. |
| P3-G02 | **High** | Crisis content not auto-flagged at publish time — safety gap. |
| P3-G03 | **Medium** | Reports do not enter moderation queue automatically — friction exists for reporters but not for harmful content pipeline. |
| P3-G04 | **Low** | No appeal workflow; punitive paths lack user-facing explanation beyond moderator note. |

**Conformance:** **Partial**
**Fix priority:** Blocker (crisis on create, report→queue); Must (pre-send prompt UI).

---

## 5.5 P4 — Earn Your Privacy Upgrades

**Design intent (P4, PRIV-GROUP-01, PRIV-ANON-01):** Private groups, mentorship, anonymous posting gated by trust.

### Observed behavior

| Feature | Trust-gated? | Evidence |
|---------|--------------|----------|
| Guilds | No — any user can create/join | `apps/guilds/` |
| Messaging | No — any authenticated user | `apps/messaging/services.py` |
| Collections visibility | Enum exists; **not enforced on create/read** | `Collection.visibility`, `create_collection` ignores form field |
| Profile visibility | All profiles public | Stage 3 FLOW — no visibility enum on `Profile` |
| Anonymous posting | Not implemented | — |

### Equity/safety note (per CompleteAudit §5)

Gating privacy behind trust can harm vulnerable users who need anonymity before establishing reputation. No implementation exists today — this is **not aligned** but also **not yet harmful** because gating is absent.

**Conformance:** **Not aligned** (feature absent)
**Fix priority:** Defer — requires product/legal review (ODD-06, ODD-13).

---

## 5.6 P5 — Knowledge Outlasts Conversation

**Design intent (P5, KNOW-CLIP-01, KNOW-COL-01, AI-SUMMARY-01):** Threads become lasting knowledge artifacts via clips, collections, summaries.

### Observed behavior

| Mechanism | Status | Evidence |
|-----------|--------|----------|
| Whole-post clip | Working | `knowledge/views.py:clip_post`, `knowledge/services.py:create_clip` |
| Passage clip | Schema + service; **no UI** | `ClipKind.SELECTION`, offsets on `Clip` model |
| Thread/reply clip | Service-validated; **no UI** | `ClipKind.WHOLE_THREAD`, `WHOLE_REPLY` |
| Vault | Paginated personal library | `knowledge/views.py:vault_list` |
| Collections | Create/add; visibility not saved | `create_collection` L104–109 |
| Thread summaries | Concatenation stub; **not invoked or displayed** | `ai_coach/services.py:generate_thread_summary` |
| Source attribution | `quoted_text` snapshot; link breaks on soft-delete | `Clip.quoted_text`; `get_post_for_display` uses `.visible()` |
| Tags on posts | `set_post_tags` exists; **no compose UI** | `knowledge/services.py:set_post_tags` |

### Confirmed alignment

- Clipping creates durable `quoted_text` snapshots.
- Knowledge hub links vault, tags, followed threads (`dashboard/knowledge_hub.html`).

### Gaps and risks

| ID | Severity | Finding |
|----|----------|---------|
| P5-G01 | **High** | Passage-level clipping (Phase 1–2 requirement) not user-accessible. |
| P5-G02 | **Medium** | Soft-deleted source posts leave clips with stale quotes and broken source links. |
| P5-G03 | **Medium** | Thread summaries are scaffold-only; knowledge does not outlast conversation in summarized form. |
| P5-G04 | **Medium** | Public/guild collections not readable by non-owners. |

**Conformance:** **Partial**
**Fix priority:** Should — passage clip, collection visibility, basic search.

---

## 5.7 P6 — Growth Is the Metric

**Design intent (P6, PHIL-NORTH-01, GAME-PHIL-01):** KPI is prosocial skill improvement, not DAU or engagement volume.

### Observed behavior

| Metric surfaced | Where | Competes with skill growth? |
|-----------------|-------|----------------------------|
| XP, level, streak | `gamification/progress.html` | Yes — streak multipliers reward daily activity |
| Trust scores (private) | `trust/settings.html` — owner only | Aligned when visible |
| Contribution range label | `UserTrustProfile.contribution_range_label` | Aligned — not on public profile by default |
| Dashboard copy | “Show up for each other” | Neutral |
| Caught-up message | Feed endpoint when following exhausted | **Aligned** — anti-infinite-scroll |
| Activity events | `XP_AWARDED`, `POST_CREATED` logged | Operational, not user-facing KPI |

### Confirmed alignment

- “You're caught up” feed endpoint discourages endless scrolling (`get_dashboard_feed` L41–47).
- Trust default visibility is HIDDEN — scores are not performative by default.

### Gaps and risks

| ID | Severity | Finding |
|----|----------|---------|
| P6-G01 | **Medium** | XP/streak/level are the most developed gamification UX — risk of rewarding volume over quality. |
| P6-G02 | **Medium** | No prosocial skill KPI dashboard or narrative tying metrics to growth. |
| P6-G03 | **Low** | Journal XP (20 per entry) may incentivize reflection quantity over depth. |

**Conformance:** **Partial**
**Fix priority:** Defer expansion of gamification until quality signals mature (per Stage 4 §4.3).

---

## 5.8 P7 — AI Is a Coach, Not a Cop

**Design intent (P7, AI-PHIL-01, MOD-WORKFLOW-02):** AI advises; user has last word; humans confirm moderation; no binding AI enforcement.

### Observed behavior

| AI touchpoint | Binding? | Labeled? | Human review? | Evidence |
|---------------|----------|----------|---------------|----------|
| Sentiment analysis | No | No | N/A | `analyze_sentiment` — keyword lists |
| Pre-send prompt | No (when wired) | No | N/A | Advisory string only |
| Journal response | No | Partial (“AI” in model field) | N/A | Static template response L69 |
| Thread summary | No | `is_ai_generated=True` | N/A | Not shown in UI |
| Crisis flag | **Flags only** — no auto-removal | No | Moderator notified | `flag_crisis_content` |
| Moderation | Humans decide | Explanation required | Yes | `review_content` |
| Trust ETS from sentiment | **Not wired** | — | — | ETS from TrustEvents only |

### Confirmed alignment

- No automatic content removal based on AI sentiment.
- Crisis handling creates flag + moderator notification, not punitive action.
- Moderation decisions require human reviewer.

### Gaps and risks

| ID | Severity | Finding |
|----|----------|---------|
| P7-G01 | **Medium** | AI is keyword heuristic, not coach-grade LLM — mislabels dialect/sarcasm/grief (CompleteAudit §9 risk). |
| P7-G02 | **Medium** | No user-facing AI labeling on compose prompts or journal responses. |
| P7-G03 | **Low** | `ai_sentiment_label` field on `ModerationReview` unused in workflow. |
| P7-G04 | **Informational** | No opt-out or consent flow for AI processing. |

**Conformance:** **Partial**
**Fix priority:** Defer LLM integration to Phase 3; Must label AI-assisted prompts when wired.

---

## 5.9 Principles Summary Dashboard

| Principle | Rating | Top gap | Priority |
|-----------|--------|---------|----------|
| P1 Prosocial over popularity | Partial | Chronological feed | Should |
| P2 Visibility as responsibility | Partial | Roles not auto-synced | Must |
| P3 Gentle friction | Partial | Pre-send + crisis not wired | Blocker/Must |
| P4 Earned privacy | Not aligned | Not implemented | Defer |
| P5 Knowledge outlasts conversation | Partial | Passage clips, summaries | Should |
| P6 Growth is the metric | Partial | XP/streak over skill KPI | Defer |
| P7 AI coach not cop | Partial | Heuristic only; prompt not wired | Must (wiring) |

---

## 5.10 Stage 5 Exit Criteria

- [x] All seven principles rated with file-path evidence
- [x] Each principle lists confirmed behavior and gap/risk
- [x] Cross-referenced to Stage 1 requirement IDs (P1–P7, SOC-*, TRUST-*, MOD-*, KNOW-*, AI-*)
- [x] Equity note included for P4 (CompleteAudit §5 requirement)
