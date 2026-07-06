## General summary of issues

**Major errors / correctness risks**

The most serious problems are performance and correctness landmines in the trust subsystem. `clusters.py._build_adjacency()` re-queries `GuildMembership` once per membership row and rebuilds the full member list every time, which is O(members²) per guild. Worse, `get_user_cluster_id()` recomputes *the entire platform's* clusters synchronously whenever a single user has no cached cluster — and `anti_gaming._rater_cluster_concentration()` calls that (via `_get_cluster_for_user_id`) in a loop over up to ~40 rater IDs, each doing its own `User.objects.get()`. So a single reaction can trigger a full-graph recompute multiple times inside a request. This needs to be moved off the request path.

The rate limiter (`rate_limit.py`) has a read-then-write race (two concurrent requests can both pass the check because `get`/`set` isn't atomic), and production keeps the base `LocMemCache`, so limits aren't shared across workers — meaning registration/login/export throttling is largely ineffective in a real deployment.

`signals.py` connects `post_save` with `sender=settings.AUTH_USER_MODEL`, which is a *string*. Django compares the signal sender by class identity, so this receiver never fires. Profile creation happens to still work because the middleware does the same job — but that means you have a dead signal plus duplicated logic.

**Conflicting / inconsistent code**

There are two independent hostile-language detectors that can disagree: `conduct.py` (comprehensive patterns, used by the analyzer/content-review panel) and a second copy of `HOSTILE_PATTERNS` living in `services.py` that `classify_civility()` uses for the civility prompt. A message can be flagged by one path and not the other. The civility check should delegate to `detect_conduct_flags()`.

Error handling across the reply views is inconsistent: `reply_create` catches `BlockedInteractionError`, `ValidationError`, and `InteractionError`, but `reply_edit` catches only `ValidationError` — an `InteractionError` from `update_reply` will 500. `reply_edit` also re-imports `ValidationError` and `enforce_content_review` locally even though both are already imported at module top.

There are also missing authorization checks: `context_note_rate` fetches a `ContextNote` by raw `pk` with no ownership/permission gate, and `react_reply`/`report_reply` don't apply the block check that `reply_create` does.

**Redundant / dead code**

`POSITIVE_WORDS` and `NEGATIVE_WORDS` in `services.py` are defined but never referenced — leftovers superseded by the lexicon system. `score_content`, `analyze_sentiment`, and `pre_send_prompt` are only reachable from tests, duplicating the real pipeline (`analyze_content`, `score_from_review_event`, `classify_civility`). `_is_htmx` (views.py) and `is_htmx` (view_helpers.py) are identical. `_iso()` in export_builders has two branches that do the same thing. The `and score < -0.5` clause in `classify_civility` is always true whenever the label is already `NEGATIVE`, so it's redundant.

**Unimplemented functionality**

Several features are modeled and migrated but never wired: `AIIntervention` has a model + admin registration but nothing ever creates or surfaces one. `ThreadSummary` / `generate_thread_summary()` exist but nothing calls the generator. `brigading_score()` is defined but unused. `finalize_content_review_event` and the civility `create_civility_prompt_event` / `finalize_civility_event` are exercised only by tests, not by any production view path I can see — so the pre-send civility prompt appears half-wired (the record-action endpoint exists, but the creation trigger doesn't). These need verification against the `posts`/`interactions` service modules that aren't in this file set.

**UI polish**

`knowledge_hub.html` ships two "placeholder" panels, one literally saying "coming soon to this panel." The reply/post composer (`reply_form.html`) has no real submit button — submission depends entirely on `content_review.js` (which isn't in this set) with no `<noscript>` fallback, so the form is non-functional without JavaScript. `prosocial_reactions.html` renders `category_totals` using raw slug keys (e.g. `good_faith`) instead of human labels. The `shell_context` context processor also fires ~6 queries on every authenticated page render.

One thing I couldn't fully verify: `content_review.js`, the `posts`/`interactions`/`accounts` service modules, and the ai_coach view aren't in the provided files, so a few "appears unwired" items above should be confirmed against those.

## Phased remediation plan

**Phase 1 — Correctness & security (do first)**
1. Fix rate limiting: switch to an atomic counter (`cache.add` + `cache.incr`) and configure a shared cache backend (Redis/Memcached) in `production.py`; the current `LocMemCache` makes throttling per-process.
2. Fix the dead profile-creation signal: register it against the resolved user model (`get_user_model()` / `AppConfig.ready`) or remove it and rely solely on the middleware — then delete the duplicated path.
3. Add the missing authorization check to `context_note_rate` (verify rater eligibility / note visibility) and apply the block check to `react_reply` and `report_reply` to match `reply_create`.
4. Add `InteractionError`/`BlockedInteractionError` handling to `reply_edit` so it degrades to a form error instead of a 500.

**Phase 2 — Performance (trust subsystem)**
5. Rewrite `clusters._build_adjacency()` to fetch all guild memberships once and group in memory (eliminate the per-row re-query).
6. Remove the on-demand full recompute from `get_user_cluster_id()`; make cluster assignment a background/scheduled job (`sync_trust_clusters` command already exists) and have the getter return a cheap fallback on cache miss.
7. Batch `anti_gaming._rater_cluster_concentration()` so it resolves all rater clusters in a single query instead of per-ID `User.objects.get()` calls.
8. Reduce `shell_context` query load (cache counts, or defer non-critical rail data to lazy HTMX loads).

**Phase 3 — Resolve conflicts & consolidate**
9. Make `classify_civility()` delegate to `detect_conduct_flags()`; delete the duplicate `HOSTILE_PATTERNS` block in `services.py`.
10. Consolidate `is_htmx`/`_is_htmx` into one shared helper and import it in both places.
11. Remove the redundant local re-imports in `reply_edit`.

**Phase 4 — Remove or finish dead features (decide per item)**
12. Delete `POSITIVE_WORDS`/`NEGATIVE_WORDS`, and either delete or clearly mark `score_content`/`analyze_sentiment`/`pre_send_prompt` as test-only/legacy.
13. For `AIIntervention`, `ThreadSummary`/`generate_thread_summary`, and `brigading_score`: confirm intent — either wire them into a real trigger and surface them in the UI, or remove the models/functions (and their migrations/admin registrations) to avoid schema cruft.
14. Verify the content-review and civility finalization functions are actually invoked by the `posts`/`interactions` create paths; if not, wire finalization so `is_consumed`/`is_finalized` are set after publish.

**Phase 5 — UI polish**
15. Replace the "coming soon" placeholder panels in `knowledge_hub.html` with real content or remove them.
16. Add a working no-JS submit path (or at least a `<noscript>` notice) to the composer/reply forms so posting isn't silently broken without `content_review.js`.
17. Map `category_totals` slugs to display labels in `prosocial_reactions.html`.
18. Tidy `export_builders._iso()` (collapse the duplicate branch) — trivial cleanup to fold in here.
