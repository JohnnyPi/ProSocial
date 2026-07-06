# Prosocial Social Platform

## Final Setup → Initial Implementation → Phased Implementation Plan

## 1. Product Direction

The application should begin as a **small, secure social platform**, not as a fully developed alternative to conventional social media.

Its initial purpose is to let users:

* Create an account and profile.
* Post text updates and images.
* Reply to other users.
* Share playful, casual, serious, supportive, critical, or practical content.
* Express gratitude.
* Find and complete small prosocial actions.
* Control whose content reaches them.
* Gradually build contextual trust through real interactions.

The platform should optimize for:

> **Long-term social health and meaningful prosocial activity, rather than raw engagement.**

The north-star metric should eventually be:

> **Meaningful prosocial acts per weekly active user.**

A meaningful act may include:

* A substantive supportive reply.
* A fulfilled help request.
* A useful explanation.
* A thank-you sent after receiving help.
* A completed commitment.
* A verified volunteer, mutual-aid, or donation action.
* A successful invitation that causes another person to act.

Likes, views, comments, and time-on-site may still be measured, but they should not become the primary definition of success.

---

# 2. Foundational Product Rules

These rules should guide every phase.

## 2.1 Private by default

Helping, commitments, ratings, and trust relationships should normally be private unless the user deliberately makes them visible.

Avoid forcing users to publicly display generosity, virtue, donations, streaks, or reputation.

## 2.2 Truthful by design

Do not use:

* Fabricated social proof.
* Fake scarcity.
* Inflated participation counts.
* Manipulative guilt.
* Misleading impact claims.
* Defaults that are difficult to change.

Local or community social proof should only appear when it is accurate and sufficiently supported by real activity.

## 2.3 Behavior over performance

Reward completed, useful behavior rather than the appearance of helping.

For example:

* A fulfilled request matters more than a like on the request.
* A completed donation matters more than a pledge.
* A substantive reply matters more than a reaction.
* Repeat helping matters more than a one-time public gesture.

## 2.4 Emotional negativity is not misconduct

The platform must distinguish negative emotion from destructive behavior.

Permitted content can include:

* Grief.
* Anger.
* Strong criticism.
* Political disagreement.
* Personal distress.
* Dark humor.
* Frustration.
* Unpopular opinions.

Moderation should focus on conduct such as:

* Harassment.
* Threats.
* Dehumanization.
* Dogpiling.
* Repeated personal targeting.
* Manipulation.
* Coordinated abuse.
* Spam.
* Deliberate derailment.

The product must not enforce happiness or create a culture of toxic positivity.

## 2.5 Reputation is contextual

Do not create a single universal karma score.

Trust should eventually be:

* Relationship-relative.
* Topic-relative.
* Community-relative.
* Behavior-based.
* Revisable.
* Time-decayed.

A user may be highly trusted for emotional support, moderately trusted for technical explanations, and poorly trusted in confrontational political discussions.

---

# 3. Technical Setup

## 3.1 Recommended technology stack

Use a **Django modular monolith**.

| Area                     | Technology                                                     |
| ------------------------ | -------------------------------------------------------------- |
| Backend                  | Python and Django 6.0.x                                        |
| Server-rendered frontend | Django templates                                               |
| Partial page interaction | HTMX and small amounts of vanilla JavaScript                   |
| Database                 | PostgreSQL                                                     |
| Styling                  | Organized plain CSS initially                                  |
| Image handling           | Pillow                                                         |
| Development uploads      | Local filesystem                                               |
| Production uploads       | S3-compatible object storage                                   |
| Authentication           | Django server-side sessions                                    |
| Deployment               | Containerized Django application behind an HTTPS reverse proxy |
| Administration           | Django Admin                                                   |
| Testing                  | Django test framework or pytest-django                         |

Do not begin with:

* Rust microservices.
* A separate Svelte or React frontend.
* A public API-first architecture.
* A graph database.
* Event streaming infrastructure.
* Multiple independently deployed services.

Those may become useful later, but they would slow down the initial product without solving an immediate problem.

## 3.2 Architectural style

Use a modular monolith:

```text
Browser
   |
   v
Django URLs and Views
   |
   +-- Forms and validation
   +-- Services for state changes
   +-- Selectors for queries
   +-- Permissions
   +-- Templates and HTMX fragments
   |
   v
Django ORM
   |
   v
PostgreSQL
```

This provides one deployable application while keeping business areas separated well enough to extract them later if necessary.

## 3.3 Initial project structure

```text
prosocial_platform/
├── manage.py
├── pyproject.toml
├── README.md
├── .env.example
├── compose.yaml
│
├── config/
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── settings/
│       ├── base.py
│       ├── development.py
│       ├── testing.py
│       └── production.py
│
├── apps/
│   ├── accounts/
│   ├── profiles/
│   ├── posts/
│   ├── dashboard/
│   └── common/
│
├── templates/
│   ├── base.html
│   ├── registration/
│   ├── components/
│   └── errors/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/
├── tests/
│   ├── integration/
│   └── security/
│
├── scripts/
└── deploy/
```

Additional Django applications should be introduced only when their phase begins:

```text
apps/
├── interactions/
├── prosocial_actions/
├── communities/
├── trust/
├── moderation/
├── recommendations/
└── analytics/
```

## 3.4 Internal Django separation

Each application should follow the same internal pattern:

| File             | Purpose                           |
| ---------------- | --------------------------------- |
| `models.py`      | Database entities and invariants  |
| `forms.py`       | Browser input and validation      |
| `validators.py`  | Reusable validation rules         |
| `services.py`    | State-changing operations         |
| `selectors.py`   | Read queries                      |
| `views.py`       | Request and response coordination |
| `permissions.py` | Authorization                     |
| `admin.py`       | Administrative tools              |
| `templates/`     | Presentation                      |
| `tests/`         | Application-specific tests        |

Views should remain small. Business operations should live in services, while query composition should live in selectors.

Do not build a generic repository abstraction over Django’s ORM.

---

# 4. Initial Data Model

The first implementation should remain small.

## 4.1 Accounts

Create a custom user model before the first production migration.

```text
User
├── id
├── public_id
├── email
├── username
├── is_active
├── is_staff
├── date_joined
└── last_login
```

Identity and authentication belong here.

## 4.2 Profiles

```text
Profile
├── user
├── handle
├── display_name
├── biography
├── profile_image
├── created_at
└── updated_at
```

Public profile information should remain separate from authentication credentials.

## 4.3 Posts

```text
Post
├── id
├── public_id
├── author
├── body
├── image
├── created_at
├── updated_at
├── is_deleted
└── moderation_status
```

Require at least one of:

* Text.
* Image.

Store plain text rather than user-authored HTML.

Keep one image directly on the post initially. Add a separate attachment model only when multiple uploads or video become real requirements.

## 4.4 Activity events

Even before advanced analytics exists, record a small set of structured product events.

```text
ActivityEvent
├── actor
├── event_type
├── target_type
├── target_id
├── community_id
├── metadata
└── created_at
```

Initial events may include:

* Account created.
* Login completed.
* Profile updated.
* Post created.
* Post edited.
* Image uploaded.
* Post viewed.
* Post deleted.

This event history will later support experimentation, trust calculations, retention analysis, and abuse detection.

Do not calculate trust scores yet.

---

# 5. Security Baseline

Security should be part of the initial implementation rather than a later cleanup phase.

## 5.1 Authentication

Use Django session authentication.

* Store the session identifier in a secure HTTP-only cookie.
* Use Django CSRF protection for state-changing requests.
* Destroy sessions on logout.
* Require authentication for private and state-changing views.
* Use generic login failure messages.
* Apply login and registration throttling.

Do not store JWTs in browser local storage for the initial same-origin website.

## 5.2 Authorization

Every edit, deletion, moderation, and privacy operation must check permissions on the server.

For example, post ownership must be part of the query:

```python
post = get_object_or_404(
    Post,
    public_id=public_id,
    author=request.user,
)
```

Hiding an edit button is not authorization.

## 5.3 Image uploads

Allow only:

* JPEG.
* PNG.
* WebP.

For every upload:

1. Enforce a request-size limit at the reverse proxy.
2. Enforce an application-level file-size limit.
3. Decode the image with Pillow.
4. Validate dimensions and total pixel count.
5. Reject malformed image data.
6. Re-encode the image into a known format.
7. Generate a random server-side filename.
8. Strip unnecessary metadata.
9. Store it outside the source tree.
10. Serve it from non-executable storage.

## 5.4 Production settings

Production configuration should include:

```python
DEBUG = False

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Lax"

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
```

Add a Content Security Policy after asset sources are settled.

## 5.5 Operational safeguards

Include:

* Secrets outside source control.
* Database backups.
* Authentication audit logging.
* Upload failure logging.
* Rate limiting.
* Dependency update checks.
* Custom 400, 403, 404, and 500 pages.
* No passwords, cookies, tokens, or uploaded content in routine logs.

---

# 6. Initial Implementation

This is the first complete vertical slice.

## Step 1: Bootstrap the project

* Create the Django project.
* Split settings into base, development, testing, and production.
* Configure PostgreSQL.
* Add environment-based secrets.
* Add Docker Compose for local Django and PostgreSQL development.
* Configure static and media paths.
* Create the custom user model.
* Run the initial migrations.

### Completion gate

The project launches locally, connects to PostgreSQL, and creates users through Django Admin.

## Step 2: Implement account access

Add:

* Registration.
* Login.
* Logout.
* Password change.
* Password reset.
* Account activation and suspension fields.
* Authentication event logging.
* Login and registration throttling.

### Initial routes

```text
/accounts/register/
/accounts/login/
/accounts/logout/
/accounts/password-change/
/accounts/password-reset/
```

### Completion gate

A new user can register, log in, reset a password, and log out securely.

## Step 3: Implement profiles

Add:

* Profile creation.
* Public handle.
* Display name.
* Biography.
* Profile image.
* Profile editing.
* Public profile page.

### Routes

```text
/profiles/<handle>/
/profiles/edit/
```

### Completion gate

Users can edit only their own profile, and public profiles expose no private account data.

## Step 4: Implement text posts

Add:

* Text post creation.
* Post detail.
* Post editing.
* Soft deletion.
* Ownership checks.
* Character limits.
* Whitespace validation.
* Pagination.

### Routes

```text
/posts/create/
/posts/<public-id>/
/posts/<public-id>/edit/
/posts/<public-id>/delete/
```

### Completion gate

Authenticated users can create and manage their own posts, but cannot modify another user’s content.

## Step 5: Implement the dashboard

The dashboard should contain:

* Current-user summary.
* Post composer.
* Recent feed.
* Pagination.
* Profile navigation.
* Logout access.

The dashboard should query posts and profiles rather than owning their data.

### Completion gate

A user can log in, publish an update, and immediately see it in the dashboard feed.

## Step 6: Add single-image posting

* Add strict image validation.
* Add image preview.
* Re-encode images through Pillow.
* Generate safe filenames.
* Add upload tests.
* Use local media storage only in development.

### Completion gate

A post can contain text, an image, or both, and malformed uploads are rejected.

## Step 7: Add HTMX enhancements

Use HTMX for:

* Inline post submission.
* Feed insertion.
* Post editing.
* Post deletion confirmation.
* Pagination or “load more.”
* Form error replacement.

The site should still function through ordinary HTTP requests without JavaScript.

## Step 8: Add initial tests

Required tests:

* Registration flow.
* Login flow.
* Password reset flow.
* Profile ownership.
* Post ownership.
* Post validation.
* CSRF protection.
* Upload type validation.
* Upload size validation.
* Unauthorized access.
* Soft deletion.
* Dashboard pagination.

## Step 9: Prepare production deployment

* Create the production container.
* Add the HTTPS reverse proxy.
* Configure object storage.
* Enable secure cookie settings.
* Enable CSP.
* Configure structured logs.
* Configure backups.
* Run Django’s deployment checks.

### Initial release result

At the end of the initial implementation, the application is a secure social posting site with:

* Accounts.
* Profiles.
* Text posts.
* Single-image posts.
* A dashboard feed.
* Administrative control.
* Basic behavioral event recording.

No trust score, recommendation algorithm, payment system, or LLM moderation should exist yet.

---

# 7. Phased Step-by-Step Implementation Plan

# Phase 1: Social Interaction Foundation

## Objective

Enable direct interaction without reproducing a simplistic popularity system.

## Steps

1. Add replies to posts.
2. Initially limit replies to one nesting level.
3. Add reply editing and deletion.
4. Add a dedicated one-tap **Thank You** response.
5. Add optional private appreciation notes.
6. Add notifications for replies and thanks.
7. Add mute, hide, block, and report controls.
8. Add basic reply and notification rate limits.
9. Record structured interaction events.
10. Add moderation status fields without automatic suppression.

## Suggested models

```text
Reply
ThankYou
Notification
UserBlock
UserMute
ContentReport
```

## Design constraints

* Do not add a public dislike count.
* Do not add public reputation scores.
* Do not rank solely by reaction count.
* Do not force appreciation messages to be public.
* Preserve casual and playful conversation.

## Completion gate

Users can hold conversations, thank one another, and establish personal boundaries without needing centralized moderator action.

---

# Phase 2: Prosocial Action Layer

## Objective

Move beyond ordinary posting by making concrete prosocial action easy and repeatable.

## Steps

1. Add post or card types:

   * General update.
   * Request for help.
   * Offer of help.
   * Encouragement request.
   * Local action.
   * Volunteer opportunity.
2. Add a small “action of the day” or session-level suggestion.
3. Allow users to save an action privately.
4. Add scheduled commitments.
5. Add optional reminders.
6. Add recurring commitments.
7. Add completion confirmation.
8. Allow a recipient or organizer to verify completion when appropriate.
9. Add a Thank You step after completion.
10. Add friend invitations for joint actions.

## Evidence-informed interface rules

* Present one small, concrete action rather than a vague call to “do good.”
* Keep commitments private by default.
* Frequency-cap reminders.
* Make reminders easy to dismiss.
* Avoid congratulatory feedback that implies the user has already done enough.
* Pair positive impact feedback with a clear optional next action.
* Use truthful local or community norm cues.
* Use public recognition only when the user opts in.

## Example norm cue

Good:

> “Members of this neighborhood usually respond to urgent requests within one day.”

Bad:

> “Everyone is helping—why aren’t you?”

## Completion gate

The application can distinguish between posting about helping and completing a meaningful action.

---

# Phase 3: Interaction-Quality Ratings and User Boundaries

## Objective

Collect multidimensional interaction signals without collapsing them into likes and dislikes.

## Positive reply dimensions

* Helpful.
* Thoughtful.
* Supportive.
* Insightful.
* Clarifying.
* Calming.
* Constructive disagreement.
* Funny or playful.

## Negative reply dimensions

* Dismissive.
* Escalatory.
* Bad faith.
* Manipulative.
* Dogpiling.
* Needlessly cruel.
* Spammy.
* Derailing.

## Steps

1. Add a compact interaction-rating interface.
2. Let users choose one or two dimensions rather than completing a survey.
3. Keep negative evaluations anonymous to the rated user.
4. Prevent users from repeatedly rating the same content.
5. Weight ratings only after meaningful exposure or interaction.
6. Detect rapid coordinated rating activity.
7. Let users undo or revise ratings.
8. Add “show me less like this” as a personal preference signal.
9. Keep ratings separate from formal reports.
10. Record the topic and community context of each rating.

## Important distinction

A rating such as **escalatory** should influence personal filtering and later trust analysis, but it should not automatically delete content.

A formal report should be reserved for suspected rule violations.

## Completion gate

The system captures interaction quality while preserving criticism, humor, dissent, and negative emotional expression.

---

# Phase 4: Community and Context

## Objective

Create the contexts required for localized norms and trust.

## Steps

1. Add communities or circles.
2. Add topic labels.
3. Allow communities to define a concise values statement.
4. Add practical examples of constructive and destructive behavior.
5. Add newcomer onboarding.
6. Show community-specific expectations before the first post.
7. Add community moderator roles.
8. Add community-specific reports and filters.
9. Add local or group-level action cards.
10. Record whether interactions occur:

    * Between followers.
    * Between strangers.
    * Inside a community.
    * Across communities.
    * Around a specific topic.

## Community onboarding

Onboarding should explain:

* What the community is for.
* What constructive participation looks like.
* How disagreement is handled.
* What actions are prohibited.
* How moderation decisions can be appealed.

Avoid long legalistic rule pages as the only form of onboarding.

## Completion gate

Trust and moderation data can be interpreted within a real social context instead of globally.

---

# Phase 5: Contextual Trust Topology

## Objective

Create a distributed trust network that answers:

> “Who consistently improves interactions for whom, and in what contexts?”

## Core trust concepts

Trust is represented as relationships between users rather than as a universal score.

Possible dimensions include:

* Informational trust.
* Emotional trust.
* Reliability.
* Constructive-conflict trust.
* Humor affinity.
* Mentorship.
* Creativity.
* Newcomer support.
* Follow-through.

## Suggested relational model

```text
TrustObservation
├── observer
├── subject
├── source_interaction
├── community
├── topic
├── dimension
├── value
├── confidence
└── created_at

TrustEdge
├── observer
├── subject
├── community
├── topic
├── dimension
├── current_weight
├── confidence
├── last_recalculated
└── observation_count
```

The graph can remain in PostgreSQL initially. A graph database is unnecessary until relational queries demonstrably become a bottleneck.

## Calculation principles

1. Require repeated interactions before strong trust emerges.
2. Apply time decay.
3. Give recent behavior more influence than distant behavior.
4. Limit the effect of a single rater.
5. Reduce the weight of coordinated rating bursts.
6. Keep separate dimensions separate.
7. Keep community and topic contexts separate.
8. Allow trust to recover after improved behavior.
9. Avoid permanent labels.
10. Never expose a universal trust score.

## Reputation firewalls

Users should be able to choose settings such as:

* Prioritize people trusted by people I trust.
* Do not use second-degree trust signals.
* Prioritize direct interaction history.
* Reduce content from unfamiliar trust clusters.
* Increase exposure to constructive disagreement.
* Show more newcomer content.
* Show less hostile content.
* Do not personalize using trust data.

## Explainability

When trust affects ranking, offer explanations such as:

> “Shown higher because people you have rated as helpful often find this person’s technical replies useful.”

Or:

> “Shown lower because you have repeatedly marked similar interactions as escalatory.”

Do not expose private raters or sensitive trust relationships.

## Completion gate

Trust influences personalization in a limited, explainable experiment without becoming public status or permanent social class.

---

# Phase 6: Graduated Moderation

## Objective

Use the least restrictive effective response before resorting to bans.

## Level 0: Personal control

User-directed tools:

* Mute.
* Hide.
* Block.
* Show less.
* Deprioritize.
* Filter specific interaction patterns.

These are preference actions, not punishments.

## Level 1: Soft community signals

Signals such as:

* Not constructive.
* Escalatory.
* Off-topic.
* Spammy.
* Dogpiling.

Possible effects:

* Lower recommendation weight.
* Reduced thread prominence.
* Moderator review prioritization.
* Temporary reply collapsing.

## Level 2: Contextual friction

For repeated harmful interaction patterns:

* Posting cooldown.
* Reply delay.
* Pre-send reconsider prompt.
* Reduced posting frequency.
* Temporary removal from recommendations.
* Limits on entering unfamiliar threads.

## Level 3: Trust isolation

For persistent but not necessarily ban-worthy behavior:

* Reduced discoverability.
* Reduced recommendation spread.
* Reduced injection into unrelated conversations.
* Lower propagation beyond direct followers.

The user may still post, but the platform stops amplifying the behavior.

## Level 4: Hard moderation

Reserved for:

* Credible threats.
* Harassment.
* Stalking.
* Coordinated abuse.
* Illegal content.
* Severe manipulation.
* Repeated evasion.
* Dangerous impersonation.

Possible actions:

* Content removal.
* Temporary suspension.
* Permanent suspension.
* Device or network-level safeguards where justified.
* Preservation of evidence for legal or safety review.

## Procedural requirements

Every platform-imposed restriction should include:

* A reason category.
* A human-readable explanation.
* Duration.
* Scope.
* Appeal path.
* Record of the decision.
* Identification of whether the action was automatic or human-reviewed.

## Completion gate

The moderation system responds proportionally and transparently rather than relying on deletion or banning as its only tools.

---

# Phase 7: LLM-Assisted Moderation

## Objective

Use language models to interpret interaction dynamics while keeping human and user control over consequential decisions.

## Initial LLM uses

1. Pre-send reconsider prompts.
2. Detection of likely escalation.
3. Detection of personal attacks.
4. Distinguishing grief or distress from hostility.
5. Identifying constructive disagreement.
6. Detecting likely dogpiling or coordinated hostility.
7. Categorizing reports.
8. Prioritizing the moderator queue.
9. Drafting plain-language moderation explanations.
10. Suggesting calmer rewrites without requiring them.

## The model should evaluate dynamics such as:

* Is the reply escalating conflict?
* Is it dismissive?
* Is it a harsh but substantive critique?
* Is it supportive?
* Is it sarcastic banter between familiar users?
* Is it manipulating or humiliating someone?
* Is it an attempt at reconciliation?
* Is it merely expressing anger or sadness?
* Is a group converging on one target?
* Is the user repeatedly entering conversations to provoke conflict?

## Restrictions

At first, the LLM should not autonomously:

* Permanently suspend accounts.
* Make legal determinations.
* Infer protected personal traits.
* Publicly label users.
* Generate permanent reputation records.
* Suppress political views based on ideology.
* Treat negative emotional tone as abuse.
* Reveal private model assessments to other users.

## Recommended decision flow

```text
Content or interaction
        |
        v
Rule-based checks
        |
        v
LLM classification with confidence and reason codes
        |
        +-- Low risk: no action
        +-- Medium risk: optional prompt or queue prioritization
        +-- High risk: temporary containment and human review
```

Model outputs should be stored as revisable assessments, not facts.

## Completion gate

LLM assistance reduces moderator workload or harmful interactions without causing unacceptable false-positive, fairness, or appeal rates.

---

# Phase 8: Prosocial Feed and Recommendations

## Objective

Replace engagement-maximizing ranking with explainable, socially healthy curation.

## Ranking inputs

A feed may combine:

* Recency.
* Direct relationship.
* User-selected interests.
* Community membership.
* Topic relevance.
* Interaction-quality history.
* Contextual trust.
* Newcomer support.
* Action urgency.
* Content diversity.
* User boundary settings.

## Content worth elevating

* Reliable helpers.
* Constructive critics.
* Bridge-builders.
* Users who clarify confusion.
* Users who de-escalate conflict.
* Insightful dissenters.
* Community newcomers receiving useful engagement.
* Verified help requests.
* Offers of concrete assistance.
* Playful content that strengthens relationships.

## Ranking constraints

* Do not use outrage or reply volume as automatic positive signals.
* Limit repeated exposure to one user or cluster.
* Prevent high-trust users from permanently dominating.
* Reserve feed space for unfamiliar or newer participants.
* Keep chronological feed access available.
* Let users control major ranking preferences.
* Explain important ranking decisions.

## Completion gate

The feed improves meaningful interaction or action completion without increasing complaints, hostility, or concentration of visibility.

---

# Phase 9: Experiments and Measurement

## Objective

Evaluate real behavior rather than assuming prosocial-looking features work.

## Five measurement layers

### 1. Immediate behavior

* Help action started.
* Supportive reply sent.
* Request accepted.
* Donation completed.
* Volunteer signup completed.
* Commitment scheduled.

### 2. Action quality

* Request fulfilled.
* Reply rated as substantive.
* Commitment completed.
* Recipient acknowledged receiving help.
* Moderator found no manipulation or spam.

### 3. Retention and habit

* Seven-day repeat-helper rate.
* Thirty-day repeat-helper rate.
* Time to next prosocial act.
* Continued action after reminders stop.

### 4. Network effects

* Invite-to-action conversion.
* Joint action completion.
* Newcomer activation.
* Cross-community constructive interaction.
* Friend-pair completion rate.

### 5. Guardrails

* Churn.
* Unsubscribe rate.
* Blocks and mutes.
* Reports.
* Complaints.
* Appeal rate.
* Moderation workload.
* Felt manipulation.
* Subgroup fairness gaps.
* Performative or low-quality helping.

## Initial experiments

### Small-action prompt

Compare:

* Plain call to action.
* Call to action plus honest norm cue.
* Call to action plus implementation prompt.

Target:

* Approximately 5% relative increase in action completion.
* No material increase in complaints or churn.

### Gratitude loop

Compare:

* No dedicated thanks.
* One-tap thanks.
* Thanks plus optional note.

Measure:

* Thirty-day repeat helping.

### Commitment scheduling

Compare:

* Immediate action.
* Scheduled action.
* Scheduled action plus reminder.

Measure:

* Completion within seven days.

### Local social proof

Compare:

* Global norm.
* Community norm.
* Friend or trusted-network norm.
* No social proof.

Measure:

* Action-start rate and avoidance behavior.

### Dyad action

Compare:

* Solo action.
* Invite-one-friend action.
* Shared progress.

Measure:

* Invite conversion and joint completion.

## Experimental design

* Use user-level randomization for private prompts.
* Use cluster randomization for community or network effects.
* Predefine one or two primary outcomes.
* Predefine guardrails.
* Maintain longitudinal holdout groups.
* Analyze subgroup differences.
* Do not ship an intervention solely because it increases clicks.

## Completion gate

A feature advances only when it improves the intended behavioral outcome without meaningful deterioration in trust, retention, safety, or fairness.

---

# Phase 10: Optional Payments, Donations, and External Action Integrations

## Objective

Add financial or externally verified actions only after the core trust and action system is stable.

## Possible features

* One-dollar quick donations.
* Round-up donations.
* Recurring micro-donations.
* Volunteer organization integrations.
* Event registration.
* Mutual-aid fulfillment tracking.
* Charity or project verification.
* Shared fundraising actions.

## Rules

* Defaults must be easy to edit.
* Personalized defaults should reflect prior user choices.
* Do not imply endorsement without verification.
* Keep financial activity private by default.
* Do not publicly rank donors.
* Separate donation metrics from volunteering metrics.
* Treat refunds, disputes, fraud, and financial compliance as first-class requirements.

## Completion gate

Payments and external actions are accurate, auditable, reversible where appropriate, and do not become a public virtue leaderboard.

---

# Phase 11: Hardening and Scale

## Objective

Prepare the platform for sustained public use.

## Steps

1. Move uploads to production object storage.
2. Add malware scanning where appropriate.
3. Add Redis only when caching, queues, or distributed throttling require it.
4. Add a background worker for:

   * Image processing.
   * Notifications.
   * Trust recalculation.
   * Moderation analysis.
   * Email delivery.
5. Add database indexes based on measured queries.
6. Add feed-query performance tests.
7. Add moderator audit tools.
8. Add privacy export and deletion tools.
9. Add disaster-recovery procedures.
10. Add security scanning and dependency automation.
11. Add accessibility testing.
12. Add abuse simulations and adversarial testing.

## Future extraction criteria

Consider a separate service only when one area demonstrates a genuine operational need.

Possible future services:

* CPU-intensive moderation inference.
* Recommendation computation.
* Media processing.
* Notification delivery.
* Public API.
* Mobile application backend.

Rust may be appropriate later for a high-throughput or CPU-intensive service, but it should not replace the Django application without a demonstrated reason.

---

# 8. Features Deliberately Deferred

Do not build these during the initial implementation:

* Universal karma.
* Public trust scores.
* Public leaderboards.
* Mandatory recognition.
* Complex badges or streak economies.
* Cryptocurrency or token rewards.
* Multi-image posts.
* Video hosting.
* Rich-text HTML editing.
* Full direct messaging.
* Arbitrary third-party plugins.
* A graph database.
* Autonomous LLM moderation.
* A separate frontend application.
* Microservices.
* Complex donation processing.
* Infinite-scroll engagement optimization.

Deferral protects the project from spending its earliest development time on risky or weakly validated systems.

---

# 9. Recommended Release Milestones

## Milestone A: Secure Social Core

Includes:

* Accounts.
* Profiles.
* Text and image posts.
* Dashboard feed.
* Admin tools.
* Security tests.
* Deployment configuration.

## Milestone B: Interaction and Boundaries

Includes:

* Replies.
* Thank-you actions.
* Notifications.
* Mute, hide, block, and report.
* Basic interaction events.

## Milestone C: Prosocial Actions

Includes:

* Requests and offers.
* Small action cards.
* Commitments.
* Scheduling.
* Reminders.
* Completion tracking.
* Friend pairing.

## Milestone D: Contextual Communities

Includes:

* Communities.
* Topics.
* Community onboarding.
* Community-specific norms.
* Moderator roles.

## Milestone E: Trust Topology

Includes:

* Multidimensional ratings.
* Trust observations.
* Contextual trust edges.
* Time decay.
* Reputation firewalls.
* Ranking explanations.

## Milestone F: Graduated and LLM-Assisted Moderation

Includes:

* Friction interventions.
* Trust isolation.
* Moderator queues.
* Pre-send prompts.
* Model-assisted classification.
* Appeals and explanations.

## Milestone G: Prosocial Recommendation System

Includes:

* Contextual ranking.
* Diversity controls.
* Newcomer visibility.
* Constructive-disagreement promotion.
* User-controlled feed settings.

## Milestone H: Evidence-Based Optimization

Includes:

* A/B testing.
* Longitudinal holdouts.
* Subgroup analysis.
* Behavioral KPI dashboards.
* Guardrail monitoring.

---

# 10. Final Recommended Build Order

The complete build order is:

1. Establish the Django modular monolith.
2. Configure PostgreSQL and split settings.
3. Create the custom user model.
4. Implement authentication.
5. Implement profiles.
6. Implement text posts.
7. Add the dashboard feed.
8. Add secure image uploads.
9. Add HTMX enhancements.
10. Add integration and security tests.
11. Deploy the secure social core.
12. Add replies and gratitude.
13. Add mute, hide, block, and report.
14. Add prosocial request, offer, and action types.
15. Add commitments, scheduling, and reminders.
16. Add communities and topics.
17. Add multidimensional interaction ratings.
18. Accumulate enough interaction data for meaningful analysis.
19. Implement contextual trust edges with decay.
20. Add explainable trust-informed feed experiments.
21. Add graduated moderation.
22. Introduce limited LLM moderation assistance.
23. Build the prosocial recommendation engine.
24. Add formal experimentation and guardrail dashboards.
25. Add payments or external action integrations only after the core system is stable.
26. Scale individual components only when measured usage requires it.

The essential sequencing principle is:

> **Build secure interaction first, meaningful action second, contextual data third, trust fourth, and algorithmic influence last.**

This prevents the trust system from becoming a disguised popularity score and gives the platform enough real behavioral evidence to support responsible personalization.
