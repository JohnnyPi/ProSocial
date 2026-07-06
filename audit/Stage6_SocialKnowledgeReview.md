# Stage 6 — Social and Knowledge Features Review

**Method:** CompleteAudit §6 — per-feature evaluation with clip integrity scenarios  
**Inputs:** Stages 1–5 artifacts, codebase trace  
**Audit date:** 2026-07-05  
**Test baseline:** 80 passed

**Status key:** ✅ Working | ⚠️ Partial | ❌ Missing | 🔒 Schema only

---

## 6.1 Feature Status Matrix

| Feature | UI | Backend | Authz | Tests | Clip/attribution | Status | Gaps | Priority |
|---------|----|---------|-------|-------|------------------|--------|------|----------|
| **Profiles** | ✅ | ✅ | ✅ owner edit | Implicit phase0 | N/A | ✅ | No visibility controls | Low |
| **Feed** | ✅ | ✅ | ✅ boundaries | phase1/3/4 | N/A | ✅ | Chronological only | Should |
| **User follow** | ❌ button | ✅ | ✅ | phase3/4 | N/A | ⚠️ | No profile Follow button | Low |
| **Thread follow** | ✅ | ✅ | ✅ | phase3 | N/A | ✅ | — | — |
| **Posts/threads** | ✅ | ✅ | ✅ owner | phase1 | N/A | ⚠️ | `thread_type`/`title` not in composer | Low |
| **Replies (nested)** | ✅ | ✅ | ✅ block | phase1 + unit | N/A | ✅ | One-level nesting only | — |
| **Reactions** | ⚠️ thank-you | ⚠️ | ✅ | phase4 model | N/A | ⚠️ | `ProsocialReaction` UI missing | Medium |
| **Messaging** | ✅ | ✅ | ✅ block | phase4 | N/A | ⚠️ | No profile Message link | Low |
| **Media** | ✅ post image | ✅ | ✅ | phase1 | N/A | ⚠️ | No reply attachments | Low |
| **Tags** | ✅ browse | ⚠️ | Public read | phase3 | N/A | ⚠️ | No tag assignment on posts | Medium |
| **Search** | ❌ | ❌ | — | ❌ | N/A | ❌ | No user-facing search | Must |
| **Clip whole post** | ✅ | ✅ | ✅ login | phase3 | ✅ snapshot | ✅ | — | — |
| **Clip passage** | ❌ | ✅ service | — | ❌ | ✅ offsets | 🔒 | No selection UI/endpoint | Must |
| **Clip whole thread** | ❌ | ✅ service | — | ❌ | ✅ | 🔒 | No UI | Medium |
| **Clip whole reply** | ❌ | ✅ service | — | ❌ | ✅ | 🔒 | No UI | Medium |
| **Vault** | ✅ | ✅ | ✅ owner | phase3 | ⚠️ stale links | ⚠️ | See §6.2 | Medium |
| **Collections** | ✅ | ⚠️ | ✅ owner | phase3 | N/A | ⚠️ | Visibility not saved | Must |
| **Collection items** | ✅ add | ✅ | ✅ owner | phase3 | N/A | ⚠️ | No remove/reorder | Low |
| **Source attribution** | ⚠️ | ✅ `quoted_text` | N/A | ❌ | ⚠️ | ⚠️ | No author in vault; broken links | Medium |
| **Discovery** | ⚠️ | ✅ | Public | phase10 | N/A | ⚠️ | Ranked feed not rendered | Low |
| **Knowledge summaries** | ❌ | ⚠️ stub | — | ❌ | N/A | 🔒 | Not invoked | Defer (P3) |
| **Helpful ranking** | ❌ | ⚠️ API | ⚠️ partial | phase5 | N/A | ⚠️ | Replies by `created_at` only | Medium |
| **Dashboard/home** | ✅ | ✅ | ✅ | phase0/1 | N/A | ✅ | Basic feed, not full §7.4 hub | Low |

---

## 6.2 Clipping Integrity Scenarios

### Scenario A — Soft-delete source post after clip

| Step | Expected (design) | Actual |
|------|-------------------|--------|
| User A posts; User B clips whole post | Clip created with `quoted_text` | ✅ `create_clip` L70–78 |
| User A soft-deletes post | Clip retained | ✅ FK remains; post `deleted_at` set |
| User B views vault | Shows quote + source link | ⚠️ Quote shown; link 404s (`get_post_for_display` → `.visible()`) |
| Clip content | Should indicate source removed | ❌ No “source unavailable” state |

**Reproduction:** `create_clip` → `soft_delete_post` → visit `/knowledge/vault/`  
**RTM:** KNOW-CLIP-01, ROAD-P1-CLIP  
**Severity:** Medium

### Scenario B — Moderated/removed post

| Step | Actual |
|------|--------|
| Clip creation on removed post | Blocked at create time ✅ `create_clip` L56–57 |
| Existing clip after moderation | Not tested; clip FK remains |

### Scenario C — Hard delete post (CASCADE)

| Step | Actual |
|------|--------|
| Post hard-deleted | `Clip.post` CASCADE deletes clip ✅ `knowledge/models.py` L44–45 |

### Scenario D — Passage clip with offsets

| Step | Actual |
|------|--------|
| User selects text on post detail | ❌ No UI |
| Service accepts `SELECTION` + offsets | ✅ `create_clip` L42–46 |
| Attribution preserves selection | ✅ `quoted_text`, `selection_start/end` fields |

### Scenario E — Self-clip

| Step | Actual |
|------|--------|
| User clips own post | Allowed; no XP/trust ✅ `create_clip` L87 `author.pk != owner.pk` |

---

## 6.3 Search Assessment

- **User-facing search:** Not implemented. No route in `config/urls.py` or `knowledge/urls.py`.
- **README:** States semantic search scaffolded for future work.
- **Admin search:** Django admin `search_fields` on some models only.
- **Tag browse:** `/knowledge/tags/` provides taxonomy navigation, not free-text search.

**RTM:** ROAD-P2-TAG  
**Priority:** Must for Phase 2 completion

---

## 6.4 Helpful-Answer Ranking

| Component | Status | Evidence |
|-----------|--------|----------|
| Peer rating dimensions | HELPED_ME, HELPFUL, SUPPORTIVE, INSIGHTFUL | `trust/models.py:PeerRatingDimension` |
| Rate endpoints | POST `/trust/rate/reply/<uuid>/`, `/trust/rate/post/<uuid>/` | `trust/views.py`, `trust/urls.py` |
| Rate UI | **None** on reply items | `interactions/reply_item.html` — thank-you only |
| Reply ordering | `created_at` ascending | `interactions/selectors.py:get_post_replies` L33 |
| Block guard on rate | Reply yes; post **no** | `trust/views.py:rate_reply` L43–44 vs `rate_post` |

---

## 6.5 Reactions: Thank-You vs ProsocialReaction

User-visible “positive reaction” today is **ThankYou** toggle (`interactions/thank_you_button.html`).  
`ProsocialReaction` (Constructive/Supportive/Insightful) is persisted in tests only — no scoring, no UI.

---

## 6.6 Collection Visibility

- `CollectionForm` includes `visibility` field (`knowledge/forms.py`).
- `create_collection` does not accept or persist `visibility` (`knowledge/services.py:L104–109`).
- `get_collection_for_owner` restricts to owner only — no public read path.
- `CollectionVisibility.PUBLIC` / `GUILD` are schema-only.

**RTM:** ROAD-P2-COLVIS, KNOW-COL-02

---

## 6.7 Test Coverage Gaps (Stage 6)

| Area | Covered? | File |
|------|----------|------|
| Whole-post clip + vault | ✅ | `test_phase3_flow.py` |
| Passage clip | ❌ | — |
| Search | ❌ | — |
| Clip on source soft-delete | ❌ | — |
| Collection visibility | ❌ | — |
| Prosocial reaction UX | ❌ | — |
| Helpful reply ordering | ❌ | — |

---

## 6.8 Stage 6 Exit Criteria

- [x] All §6 feature areas (22) have a matrix row with evidence
- [x] Clipping deletion/privacy scenarios documented with reproduction steps
- [x] Clip gaps cross-linked to RTM IDs (`KNOW-CLIP-01`, `ROAD-P2-*`)
- [x] Search absence explicitly confirmed
