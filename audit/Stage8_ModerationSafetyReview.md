# Stage 8 — Moderation and Safety Review

**Method:** CompleteAudit §8 — 10-step lifecycle trace, crisis vs misconduct separation  
**Inputs:** Stages 1–7, codebase trace  
**Audit date:** 2026-07-05  
**Test baseline:** 80 passed  
**Note:** Crisis tests use synthetic phrases only (no real PII).

---

## 8.1 Moderation Lifecycle Trace

| Step | Description | Status | Evidence | Gap |
|------|-------------|--------|----------|-----|
| 1 | Content creation | ✅ | `posts/services.py:create_post`, `interactions/services.py:create_reply` | Crisis not invoked |
| 2 | Automated checks | ⚠️ | `ai_coach/services.py:analyze_sentiment`, `pre_send_prompt` | Not wired to publish |
| 3 | Publication / restriction | ✅ | Posts visible by default; `ModerationStatus` on model | No pre-publish hold |
| 4 | User reports | ✅ | `submit_report` → `ContentReport` OPEN | — |
| 5 | Moderator queue | ⚠️ | `ModerationReview` PENDING in queue view | **Reports don't create reviews** |
| 6 | Human decision | ✅ | `review_content` with status + explanation | Reply removal missing |
| 7 | User notification | ❌ | — | No reporter/author notify on decision |
| 8 | Appeal / review | ❌ | — | No appeal model or views |
| 9 | Audit logging | ⚠️ | `TransparencyLogEntry` on review | Weak actor ID; no report linkage |
| 10 | Restoration / escalation | ⚠️ | REMOVED sets post `moderation_status` | No restore path; ESCALATED unused |

---

## 8.2 Lifecycle Diagram (Actual vs Intended)

```mermaid
sequenceDiagram
  participant User
  participant Create as create_post_or_reply
  participant Auto as ai_coach_heuristics
  participant Report as submit_report
  participant Queue as ModerationReview
  participant Mod as review_content
  participant Log as TransparencyLogEntry

  User->>Create: publish
  Note over Create,Auto: crisis check NOT called
  User->>Report: ContentReport OPEN
  Note over Report,Queue: no bridge
  Mod->>Queue: manual review only
  Mod->>Log: explanation logged
```

---

## 8.3 Report Flow Detail

| Aspect | Implementation | Gap |
|--------|----------------|-----|
| Report categories | `ReportForm` reason choices | — |
| Report evidence | `details` text field | No screenshot/attachment |
| Duplicate reports | No dedup | Multiple OPEN reports per target |
| Report status updates | `OPEN`, `assigned_to`, `resolution_*` on model | **Never updated on review** |
| Link to review | `ModerationReview.content_report` FK | Optional; not populated from `submit_report` |

**Files:** `interactions/models.py:ContentReport`, `interactions/services.py:submit_report` L194–204

---

## 8.4 Block, Mute, and Harassment Protections

| Control | Feed | Replies | Thank-you | Rate | Message |
|---------|------|---------|-----------|------|---------|
| Block | ✅ `apply_user_boundaries_to_feed` | ✅ `create_reply` | ✅ | Reply ✅ Post ❌ | ✅ |
| Mute | ✅ feed exclude | ❌ replies still visible | ✅ | — | — |
| Hide post | ✅ per-user | N/A | N/A | N/A | N/A |

**Files:** `interactions/selectors.py`, `interactions/services.py`, `trust/views.py`

---

## 8.5 Crisis Response (Separate from Misconduct)

| Requirement (§8) | Status | Evidence |
|------------------|--------|----------|
| Severe distress not treated as misconduct | ✅ | `flag_crisis_content` flags only; no auto-removal |
| Phrase detection | ✅ | `CRISIS_PHRASES` tuple | `moderation/services.py:L16` |
| Moderator notification | ✅ | Up to 5 active MODERATOR role users | L37–44 |
| Resources shown | ⚠️ | `resources_shown=True` set | **No user-facing crisis resource UI** |
| Auto-invoke on publish | ❌ | Not in `create_post`/`create_reply` | Blocker |
| Third-party contact | ✅ absent | No auto outreach | Appropriate |

### Synthetic test scenario (documented)

```
POST body: "I want to die and need help"
Expected after fix: CrisisFlag created, moderators notified, no post removal
Current: flag_crisis_content works when called directly (test_phase8_flow.py)
```

---

## 8.6 Automated Checks Assessment

| Check | Integrated? | Binding? | Risk |
|-------|-------------|----------|------|
| Keyword sentiment | ❌ standalone | No | Misclassification of grief/anger |
| Pre-send prompt | ❌ standalone | No | P3 gap |
| Crisis phrases | ❌ standalone | No | Safety gap |
| AI on ModerationReview | Field unused | No | — |

---

## 8.7 Moderator Permissions and COI

- Queue access: `MODERATOR`, `COMMUNITY_GUIDE`, `COMMUNITY_LEADER` (`moderation/views.py:_is_moderator`).
- No conflict-of-interest check (reviewer vs author relationship).
- No rate limits on reports or moderation actions.
- No spam/bot-specific controls beyond standard auth rate limits on login/register.

---

## 8.8 Findings Register

| ID | Severity | Finding | Remediation |
|----|----------|---------|-------------|
| MOD-F01 | **Critical** | Reports do not enter moderation queue | Bridge `submit_report` → `ModerationReview` |
| MOD-F02 | **High** | Crisis detection not invoked at publish | Call `flag_crisis_content` in create paths |
| MOD-F03 | **High** | No crisis resource UI for author | Show resources when flag created |
| MOD-F04 | **Medium** | `ContentReport` resolution fields never updated | Update on `review_content` |
| MOD-F05 | **Medium** | Reply removal not implemented in review | Extend `review_content` for replies |
| MOD-F06 | **Medium** | No appeal workflow | Defer — document |
| MOD-F07 | **Medium** | No decision notifications | Defer |
| MOD-F08 | **Low** | Transparency log uses truncated actor ID | Improve audit trail |
| MOD-F09 | **Low** | Duplicate reports unhandled | Dedup or merge |

---

## 8.9 Test Coverage

| Test | Coverage |
|------|----------|
| `test_phase8_flow.py::test_crisis_flag_detection` | Direct `flag_crisis_content` call |
| `test_phase8_flow.py::test_sync_user_role` | Roles only |
| `test_phase1_flow.py` | Block/mute basics |
| `test_phase7_flow.py` | Sentiment helpers |
| Report → queue E2E | **Missing** |
| Crisis on create E2E | **Missing** |

---

## 8.10 Stage 8 Exit Criteria

- [x] All 10 lifecycle steps marked with evidence
- [x] Crisis handling assessed separately from misconduct
- [x] Synthetic test scenarios documented
- [x] No real PII used in audit examples
