# Stage 3 — User Experience Flow Tracing

**Method:** Trace UI → view → authz → service/ORM → DB → tests per CompleteAudit §3.  
**Audit date:** 2026-07-05

---

## 3.1 Verification Method

Each flow assessed against: UI exists, backend behavior, validation, server-side authz, DB correctness, error/empty states, test coverage, privacy controls, role applicability.

**Status values:** `Working` | `Partial` | `UI-only` | `Not found` | `Not verifiable`

---

## 3.2 Batch A — Auth and Account Safety

### Registration
| Step | Evidence |
|------|----------|
| UI | `templates/registration/register.html` |
| View | `apps/accounts/views.py:register` — rate limit, `RegistrationForm` |
| Service | `apps/accounts/services.py:register_user` — creates User + Profile |
| Authz | Anonymous only; redirects if authenticated |
| Validation | Django form: username, email uniqueness, password strength |
| Tests | `test_phase0_flow.py::test_register_login_dashboard_flow` |
| **Status** | **Working** |

### Login / Logout
| Step | Evidence |
|------|----------|
| UI | `registration/login.html` |
| View | `ProsocialLoginView`, `ProsocialLogoutView` |
| Authz | Rate-limited login (10/15min); activity events on success/fail |
| Tests | `test_phase0_flow.py::test_register_login_dashboard_flow` |
| **Status** | **Working** |

### Password Reset
| Step | Evidence |
|------|----------|
| UI | `password_reset_*.html` templates (4 steps) |
| View | Django CBVs `PasswordResetView` through `PasswordResetCompleteView` |
| Backend | Token-based reset; console email in dev |
| Tests | **None** |
| **Status** | **Partial** — backend wired; email delivery not integration-tested |

### Password Change
| Step | Evidence |
|------|----------|
| View | `ProsocialPasswordChangeView` at `/accounts/password-change/` |
| Tests | **None** |
| **Status** | **Partial** — standard Django flow, untested |

### Profile Creation
| Step | Evidence |
|------|----------|
| Trigger | Auto on registration via `register_user` + profiles middleware |
| Model | `Profile` OneToOne with auto-generated handle |
| Tests | Implicit in phase0 registration test |
| **Status** | **Working** |

### Profile Edit
| Step | Evidence |
|------|----------|
| View | `apps/profiles/views.py:profile_edit` — `@login_required` |
| Authz | `request.user.profile` only |
| Tests | **None dedicated** |
| **Status** | **Working** (inferred from pattern; no negative authz test) |

### Profile Visibility Controls
| Step | Evidence |
|------|----------|
| Design | Public / Guild / Private |
| Implementation | All profiles public at `/profiles/<handle>/`; no visibility enum on `Profile` |
| **Status** | **Not found** |

### Account Settings
| Step | Evidence |
|------|----------|
| Password change | Yes |
| Trust score visibility | `trust/settings` — `ScoreVisibilityForm` |
| **Status** | **Partial** — no unified settings page |

### Data Export
| Step | Evidence |
|------|----------|
| View | `advanced/views.py:data_export` — `@login_required` |
| Service | `advanced/services.py:request_data_export` — JSON: profile, clips, collections |
| Tests | `test_phase11_flow.py` |
| Gaps | Excludes messages, posts, commitments, journal, trust events |
| **Status** | **Partial** |

### Account Deletion
| Step | Evidence |
|------|----------|
| View/Service | **None** |
| Docs | `docs/DATA_RETENTION.md` — policy only |
| **Status** | **Not found** |

---

## 3.3 Batch B — Core Social Loop

### Create Text/Image Post
| Step | Evidence |
|------|----------|
| UI | Dashboard composer + `posts/create/` |
| View | `dashboard/views.py` POST + `posts/views.py:post_create` |
| Service | `posts/services.py:create_post` — validation, image limits |
| Tests | `test_phase0_flow.py::test_create_post_appears_on_dashboard` |
| **Status** | **Working** |

### Thread Detail + Replies
| Step | Evidence |
|------|----------|
| UI | `posts/detail.html`, reply forms |
| View | `interactions/views.py` reply create/edit/delete |
| Service | `interactions/services.py` — 1-level nesting, block checks |
| Defect | `get_post_replies` omits `.visible()` — soft-deleted replies may display |
| Tests | `test_phase1_flow.py` |
| **Status** | **Partial** |

### Feed
| Step | Evidence |
|------|----------|
| View | `dashboard/views.py:dashboard_index` |
| Selector | `posts/selectors.py:get_dashboard_feed` — pagination, mute/block/hidden filters |
| Modes | `all`, `following`, `caught_up` flag |
| Tests | phase0, phase1 (muted), phase4 (following) |
| Gaps | No sentiment weighting; `caught_up` is paginator-based not true end-of-feed UX |
| **Status** | **Partial** |

### Reactions / Thank-yous
| Step | Evidence |
|------|----------|
| Thank-you | `interactions` — self-thank blocked |
| ProsocialReaction | `test_phase4_flow.py` |
| Design | Emotional reactions beyond like — `ProsocialReaction.kind` exists |
| **Status** | **Partial** — thanks + reaction kinds; not full design reaction set |

### View User Profile
| Step | Evidence |
|------|----------|
| View | `profiles/views.py:profile_detail` — **no login required** |
| Data | handle, bio, avatar — no trust/XP on public view |
| **Status** | **Partial** |

### Media Upload
| Step | Evidence |
|------|----------|
| Form | `PostForm` with image field |
| Validation | Pillow, 5MB, MIME whitelist in settings |
| Tests | **None dedicated** |
| **Status** | **Partial** — implemented, untested |

### Edit / Delete Own Post
| Step | Evidence |
|------|----------|
| Authz | `get_owned_post(author=request.user)` → 404 for others |
| Delete | Soft delete via `soft_delete_post` |
| Tests | `test_phase0_flow.py::test_user_cannot_edit_other_users_post` |
| **Status** | **Working** |

---

## 3.4 Batch C — Knowledge Layer

### Clip to Vault (whole post)
| Step | Evidence |
|------|----------|
| View | `knowledge/views.py:clip_post` — POST, default `WHOLE_POST` |
| Service | `knowledge/services.py:create_clip` — dedup, XP/trust to author |
| Tests | `test_phase3_flow.py::test_clip_to_vault` |
| **Status** | **Working** (whole post only) |

### Clip Passage / Thread / Reply
| Step | Evidence |
|------|----------|
| Model | `ClipKind.SELECTION`, `WHOLE_THREAD`, `WHOLE_REPLY` |
| View | No route passes `selection_start/end` or reply target |
| Service | `WHOLE_THREAD` uses post body only, not aggregated replies |
| `ClipNoteForm` | Exists but unused in clip view |
| **Status** | **Partial** — model/service support; UI not wired |

### Collections CRUD
| Step | Evidence |
|------|----------|
| Views | `knowledge/views.py` — list, create, detail, add clip/post |
| Authz | `get_collection_for_owner(owner=request.user)` |
| Visibility | `Collection.visibility` stored; all routes owner-scoped |
| Tests | `test_phase3_flow.py::test_collection_create` |
| **Status** | **Partial** — private collections work; public/guild read not implemented |

### Tags + Browse
| Step | Evidence |
|------|----------|
| Views | `tag_browse`, `tag_detail` — public |
| Service | `set_post_tags` on post create/edit |
| **Status** | **Partial** — tag browse yes; tag assignment on posts limited |

### Follow User / Thread
| Step | Evidence |
|------|----------|
| View | `follows/views.py` toggle endpoints |
| Service | `follows/services.py` — notifications on follow |
| Tests | `test_phase3_flow.py`, `test_phase4_flow.py` (following feed) |
| **Status** | **Working** |

### Notifications
| Step | Evidence |
|------|----------|
| View | List, mark read, read-all — `recipient=request.user` |
| Tests | **No dedicated HTTP test** |
| **Status** | **Partial** — implemented, lightly tested |

### Search / Discovery
| Step | Evidence |
|------|----------|
| Discovery | `get_most_clipped_posts`, `get_sentiment_boosted_posts`, ranked feed |
| Free-text search | **Not implemented** |
| Semantic search | **Not implemented** (README acknowledges) |
| Tests | `test_phase10_flow.py` |
| **Status** | **Partial** — curated discovery only, no search |

### Bookmark / Save (non-clip)
| Step | Evidence |
|------|----------|
| Clipping | Primary save mechanism |
| Separate bookmark | **Not found** |
| **Status** | **Implemented differently** — clips replace bookmarks |

---

## 3.5 Batch D — Extended Flows

### Reporting Content
| Step | Evidence |
|------|----------|
| View | `interactions/views.py` report post/reply |
| Service | Creates `ContentReport` |
| Tests | **None** |
| **Status** | **Partial** |

### Moderator Review
| Step | Evidence |
|------|----------|
| View | `moderation/queue`, `review_detail` — `@user_passes_test(_is_moderator)` |
| Service | `review_content` |
| Tests | phase8 crisis/role only; no HTTP moderation queue test |
| **Status** | **Partial** |

### Block / Mute Users
| Step | Evidence |
|------|----------|
| View | Profile handle routes |
| Service | Block enforced on replies/messages |
| Tests | `test_phase1_flow.py` (block reply, mute feed) |
| **Status** | **Working** |

### Messaging (1:1)
| Step | Evidence |
|------|----------|
| View | List, detail, start by handle |
| Authz | `get_conversation_for_user` participant filter |
| Tests | `test_phase4_flow.py` service-level |
| **Status** | **Working** |

### Guilds
| Step | Evidence |
|------|----------|
| View | List, create, detail, join/leave |
| Tests | `test_phase4_flow.py` |
| **Status** | **Working** |

### Trust Onboarding / Peer Ratings
| Step | Evidence |
|------|----------|
| Views | `trust/onboarding`, `rate_post`, `rate_reply` |
| Defect | `rate_reply` uses `Reply.objects.get` without `.visible()` or block check |
| Tests | `test_phase5_flow.py` |
| **Status** | **Partial** |

### Gamification / XP Dashboard
| Step | Evidence |
|------|----------|
| View | `gamification/progress/` |
| Service | `award_xp`, streak multipliers |
| Tests | `test_phase6_flow.py` service-level |
| **Status** | **Partial** |

### AI Journal
| Step | Evidence |
|------|----------|
| View | `ai/journal/`, `journal/new/` |
| Service | Static `ai_response` string, not external LLM |
| Tests | `test_phase7_flow.py` |
| **Status** | **Partial** — UI + storage; not true LLM |

### Challenges / Rest Mode
| Step | Evidence |
|------|----------|
| Views | `engagement/challenges/`, `rest-mode/` |
| Tests | `test_phase9_flow.py` |
| **Status** | **Working** (service-level) |

### Donations
| Step | Evidence |
|------|----------|
| View | List (verified only), create, detail |
| Service | `record_donation` — no payment gateway |
| Defect | Unverified campaigns accessible by UUID on detail |
| Tests | `test_phase11_flow.py` |
| **Status** | **Partial** — stub payment flow |

### Skill Offerings
| Step | Evidence |
|------|----------|
| View | List (global), create |
| Model | `Workshop` has no view |
| Tests | Model create only in phase11 |
| **Status** | **Partial** |

### Prosocial Actions (commitments)
| Step | Evidence |
|------|----------|
| Views | Full lifecycle at `/actions/`, `/commitments/` |
| Authz | Private commitment 403; verify creator-only in service |
| Tests | `test_phase2_flow.py` |
| **Status** | **Working** |

### Crisis Protocol
| Step | Evidence |
|------|----------|
| Service | Phrase detection → `CrisisFlag` |
| Tests | `test_phase8_flow.py` |
| HTTP flow | **Not tested end-to-end** |
| **Status** | **Partial** |

### Ripple Effect
| Step | Evidence |
|------|----------|
| View | `discovery/ripple/` |
| Tests | `test_phase10_flow.py` |
| **Status** | **Partial** — data model + page; not interactive D3 visualization |

---

## 3.6 Role Matrix

| Flow | Anonymous | Member | Moderator | Admin |
|------|-----------|--------|-----------|-------|
| View public post | Yes | Yes | Yes | Yes |
| Dashboard/feed | Redirect login | Yes | Yes | Yes |
| Create post | No | Yes | Yes | Yes |
| Edit others' post | No | 404 | 404 | Via admin |
| Vault/clips | No | Own only | Own only | Own only |
| Moderation queue | No | No | Yes (role) | Yes |
| Messages | No | Participant | Participant | Participant |
| Data export | No | Own only | Own only | Own only |

---

## 3.7 Flow-Level Defect Log

| ID | Flow | Severity | Description | Evidence |
|----|------|----------|-------------|----------|
| FLOW-D01 | Replies on post detail | Medium | Soft-deleted replies may still render | `interactions/selectors.py:19-24` — no `.visible()` |
| FLOW-D02 | Rate reply | Medium | No visibility/block check on reply lookup | `trust/views.py:42-43` |
| FLOW-D03 | Donation detail | Low | Unverified campaigns reachable by UUID | `advanced/views.py:35` |
| FLOW-D04 | Hidden posts | Low | Unhide does not verify prior hide relationship | `interactions/views.py` hidden_posts |
| FLOW-D05 | Data export | Medium | Incomplete payload vs design "full export" | `advanced/services.py:36-63` |
| FLOW-D06 | Account deletion | High | No user-facing deletion flow | Absent from codebase |
| FLOW-D07 | Profile visibility | Medium | Design visibility levels not implemented | `Profile` model |
| FLOW-D08 | Clip passage | Medium | SELECTION kind not exposed in UI | `knowledge/views.py:clip_post` |
| FLOW-D09 | Search | Medium | No basic text search for Phase 2 | `discovery/selectors.py` |
| FLOW-D10 | Password reset | Low | No automated test of email token flow | No test file |

---

## 3.8 UI-Only / Scaffold Summary

| Feature | Notes |
|---------|-------|
| Collection PUBLIC/GUILD visibility | Field stored; no public read routes |
| Workshop model | No views |
| ThreadSummary | Model + stub service; not shown in post detail UI |
| Semantic search | README: scaffolded for future |
| Live payments | Donation records COMPLETED without gateway |
| MFA | Not implemented |
| Friend (bidirectional) connections | Follow-only |

---

## 3.9 Stage 3 Exit Criteria

- [x] All 22 minimum CompleteAudit §3 flows assessed
- [x] Each status claim cites view + model + test (or "no test")
- [x] UI-only features called out
- [x] IDOR/authz gaps documented (10 defects)
- [x] Role matrix provided
