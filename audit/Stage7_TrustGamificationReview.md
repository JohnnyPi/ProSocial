# Stage 7 — Trust, Reputation, Roles, and Gamification Review

**Method:** CompleteAudit §7 — mechanism matrix, gaming/ethics register, phase-appropriate recommendation
**Inputs:** Stages 1–6, codebase trace
**Audit date:** 2026-07-05
**Test baseline:** 80 passed

---

## 7.1 Mechanism Inventory Matrix

| Mechanism | Trigger | Who triggers | Idempotent? | Self-reward | Sybil risk | Admin audit | Logged | Deterministic | Tests |
|-----------|---------|--------------|-------------|-------------|------------|-------------|--------|---------------|-------|
| **ETS recalc** | TrustEvents (200 window) | System on peer rating | Yes per recalc | N/A | Medium | Admin TrustEvent | ActivityEvent TRUST_SCORE_UPDATED | Yes | phase5 |
| **PTS recalc** | Followers + clips-by-others | System on peer rating | Yes | N/A | High (fake follows/clips) | Admin | Same | Yes | phase5 indirect |
| **Contribution score** | 65% ETS + 35% PTS | Derived | Yes | N/A | Inherited | Admin profile | Same | Yes | phase5 |
| **Peer rating (+)** | `create_peer_rating` positive dim | Any user ≠ author | Unique per dim | Blocked | Medium | PeerRating admin | TrustEvent + ActivityEvent | Yes | phase5 |
| **Peer rating (−)** | Model supports | **UI excludes** | Unique | Blocked | Low | Admin | TrustEvent | Yes | ❌ |
| **Clip TrustEvent** | `create_clip` by other | Clip owner ≠ author | Dedup on clip tuple | Blocked | Medium | TrustEvent | CLIP_CREATED | Yes | ❌ recalc |
| **Clip XP** | Same | Same | Dedup on clip | Blocked | Medium | XPTransaction | XP_AWARDED | Yes | phase3 indirect |
| **Reflection XP** | `create_journal_entry` | Self | **No** — per entry | Self | Low | XPTransaction | — | Yes | phase7 |
| **Challenge XP** | `complete_challenge` | Self | Yes — skip if done | Self | Low | XPTransaction | — | Yes | phase9 |
| **Streak multiplier** | `award_xp` daily | Self activity | Once/day | Self | Low | Profile fields | — | Yes | ❌ |
| **Badge auto-award** | XP threshold | System in `award_xp` | get_or_create | N/A | N/A | UserBadge admin | — | Yes | ❌ |
| **Achievement** | `record_achievement` | — | **Never called** | — | — | Admin | — | — | ❌ |
| **Platform role** | `sync_user_role` | **Manual only** | Deactivates prior | N/A | N/A | UserRoleAssignment | — | Yes | phase8 |
| **Thank-you** | `toggle_thank_you` | Sender ≠ author | Toggle | Blocked | Low | — | Notification | Yes | phase1 |
| **Guild role** | Guild create | Creator | — | N/A | Low | Membership | — | Yes | phase4 |

---

## 7.2 Trust Event Types — Wired vs Schema-Only

| TrustEventType | Wired? | Trigger location |
|----------------|--------|------------------|
| PEER_RATING_POSITIVE | ✅ | `trust/services.py:create_peer_rating` |
| PEER_RATING_NEGATIVE | 🔒 | Form excludes negative dimensions |
| CLIP_BY_OTHER | ⚠️ | `knowledge/services.py` — **no `recalculate_trust_scores` call** |
| THANK_YOU | ❌ | — |
| COMMITMENT_VERIFIED | ❌ | — |
| MODERATION_UPHELD | ❌ | — |
| MODERATION_FRIVOLOUS | ❌ | — |

---

## 7.3 XP Sources — Wired vs Schema-Only

| XPSource | Base | Wired? |
|----------|------|--------|
| CLIP_BONUS | 25 | ✅ clip by other |
| REFLECTION | 20 | ✅ journal |
| DAILY_CHALLENGE | 30 | ✅ challenge |
| WELCOME | — | Test only |
| DIRECT_SUPPORT, DETAILED_GUIDANCE, CRISIS_SUPPORT, KNOWLEDGE_TIP, TUTORIAL, GUILD_MISSION, COMMITMENT | 15–90 | ❌ schema only |

---

## 7.4 Role Thresholds vs Design

| Role | ETS min | Contrib min | Enforced? |
|------|---------|-------------|-----------|
| MEMBER | 40 | 30 | ⚠️ sync not auto |
| COMMUNITY_SUPPORTER | 60 | 50 | ⚠️ |
| MENTOR | 75 | 70 | ⚠️ |
| COMMUNITY_GUIDE | 80 | 75 | ⚠️ + mod queue access |
| MODERATOR | 85 | 80 | ⚠️ |
| COMMUNITY_LEADER | 90 | 90 | ⚠️ |
| LEGENDARY_STEWARD | — | — | No threshold defined |

**Design rule verified:** `role_eligible` checks ETS first, then contribution (`trust/services.py:L102–106`). PTS alone cannot promote.

**Gap:** `sync_user_role` not called after trust updates — roles are stale.

---

## 7.5 Gaming and Ethics Register

| ID | Severity | Finding | Impact |
|----|----------|---------|--------|
| TRUST-E01 | **High** | Clip TrustEvents don't trigger recalc — authors don't receive ETS credit until unrelated event | Under-rewards helpful content |
| TRUST-E02 | **High** | Roles never auto-sync — privilege drift | P2 violation |
| TRUST-E03 | **Medium** | PTS from follower count gameable via sybil follows | Popularity inflation |
| TRUST-E04 | **Medium** | Unlimited clip XP per post (dedup per user+target only) | Farming via multi-account clips |
| TRUST-E05 | **Medium** | Reflection XP per entry without quality gate | Volume over depth (P6) |
| TRUST-E06 | **Medium** | Keyword sentiment not used for ETS today — but if wired without governance, risks dialect/grief bias | Discrimination risk |
| TRUST-E07 | **Low** | Streak multipliers reward daily login over prosocial quality | Engagement metric creep |
| TRUST-E08 | **Low** | Static shell badges misrepresent trust | UX deception |
| TRUST-E09 | **Informational** | Crisis XP source defined but unwired — appropriate deferral | — |

---

## 7.6 Smallest Trustworthy Model for Current Phase

Per CompleteAudit §7: do not implement full design scoring immediately.

**Recommendation for Phase 1–2 stabilization:**

1. **Keep:** Peer ratings (positive only in UI), clip-by-other TrustEvent + XP, default HIDDEN scores.
2. **Wire immediately:** `recalculate_trust_scores` after clip; `sync_user_role` after recalc.
3. **Defer:** Negative peer ratings in UI, sentiment-in-ETS, skill trees, titles, full badge catalog, MODERATION_* trust events (blocked on moderation workflow).
4. **Cap:** Consider daily XP cap per source before expanding gamification surface.

---

## 7.7 Test Coverage Summary

| Area | File | Gaps |
|------|------|------|
| Peer rating + ETS | `test_phase5_flow.py` | Negative ratings, rate_post block |
| XP + level | `test_phase6_flow.py` | Streaks, badges |
| Roles | `test_phase8_flow.py` | Threshold promotion, auto sync |
| Clip → trust | — | **Missing** |
| Export trust/XP | `test_phase11_flow.py` | — |

---

## 7.8 Stage 7 Exit Criteria

- [x] Every live scoring path has a mechanism row
- [x] Schema-only event types documented
- [x] Phase-appropriate scoring recommendation included
- [x] Gaming/ethics register with severity
