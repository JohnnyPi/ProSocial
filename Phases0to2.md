# Prosocial Platform: Phase 0–2 Engineering Backlog

## Scope

This backlog defines three deliverable phases:

* **Phase 0 — Secure Social Core:** project setup, authentication, profiles, posts, images, dashboard, deployment baseline.
* **Phase 1 — Interaction and Boundaries:** replies, gratitude, notifications, hiding, muting, blocking, and reporting.
* **Phase 2 — Prosocial Actions:** requests, offers, commitments, scheduling, reminders, completion, verification, and invitations.

Each phase should end in a deployable and testable product increment.

---

# Shared Engineering Standards

## Application structure

```text
apps/
├── accounts/
├── profiles/
├── posts/
├── dashboard/
├── interactions/
├── prosocial_actions/
└── common/
```

Each application should use:

```text
models.py
forms.py
validators.py
services.py
selectors.py
views.py
urls.py
admin.py
migrations/
templates/<app_name>/
tests/
```

## General definition of done

A backlog item is complete when:

1. Models and constraints are implemented.
2. Migrations run successfully on an empty PostgreSQL database.
3. Views enforce authentication and authorization.
4. Templates are keyboard-accessible and display validation errors.
5. State-changing actions use POST requests.
6. Unit and integration tests pass.
7. Admin support exists where operationally useful.
8. User-facing errors do not expose internal details.
9. Relevant activity events are recorded.
10. The feature works without JavaScript unless JavaScript is essential.

---

# Phase 0 — Secure Social Core

## Phase objective

Deliver a secure Django application in which a user can:

* Register.
* Log in and out.
* Reset a password.
* Edit a profile.
* Create text or image posts.
* Edit or delete their own posts.
* View a paginated dashboard feed.

---

## Phase 0A — Project and Environment Setup

### P0-001: Create project skeleton

**Files**

```text
manage.py
pyproject.toml
README.md
.env.example
compose.yaml
config/
deploy/
```

**Tasks**

* Create the Django project.
* Configure PostgreSQL.
* Add development, testing, and production settings.
* Add environment-variable loading.
* Configure static and media paths.
* Add Docker Compose services for Django and PostgreSQL.
* Add `.gitignore`.
* Add basic logging configuration.
* Add `/health/` endpoint.

**Acceptance criteria**

* `docker compose up` starts Django and PostgreSQL.
* The application connects to PostgreSQL.
* `/health/` returns HTTP 200 and does not require authentication.
* No production secret is committed to source control.
* Development and testing settings do not use the production database.

---

### P0-002: Add development tooling

**Tasks**

* Add formatter and linter configuration.
* Add type-checking configuration where practical.
* Add pytest or Django test configuration.
* Add pre-commit hooks.
* Add a continuous-integration workflow.
* Add Django deployment checks to CI.

**Acceptance criteria**

* Formatting, linting, and tests can be run with documented commands.
* CI fails when tests or linting fail.
* CI creates a temporary PostgreSQL database.
* `python manage.py check --deploy` is run against production settings.

---

## Phase 0 Models

### P0-003: Common timestamp model

**Application:** `common`

```python
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

**Acceptance criteria**

* Other models can inherit timestamps without creating a database table for `TimeStampedModel`.
* Timestamps are timezone-aware.

---

### P0-004: Custom user model

**Application:** `accounts`

Recommended fields:

```text
User
├── id
├── public_id: UUID, unique, non-editable
├── username: unique
├── email: unique
├── is_active
├── is_staff
├── date_joined
└── last_login
```

Extend Django’s `AbstractUser`.

**Rules**

* Email addresses should be normalized.
* Public URLs must use `public_id` or handle, not sequential database IDs.
* The custom model must exist before other applications create foreign keys to users.

**Acceptance criteria**

* `AUTH_USER_MODEL` is configured before the first migration.
* Duplicate usernames are rejected.
* Duplicate normalized email addresses are rejected.
* A superuser can be created.
* Django Admin can manage users.
* Sequential database IDs are not exposed in public URLs.

---

### P0-005: Profile model

**Application:** `profiles`

```text
Profile
├── user: one-to-one User
├── handle: unique
├── display_name
├── biography
├── profile_image
├── created_at
└── updated_at
```

**Rules**

* Handle validation permits a restricted safe character set.
* Handle comparison should be case-insensitive.
* Biography is plain text.
* Profile image uses the same safe image-processing pipeline as post images.

**Acceptance criteria**

* A profile is created automatically or transactionally when a user registers.
* A user cannot own multiple profiles.
* Handles are unique regardless of capitalization.
* A profile can exist without an uploaded image.
* Private authentication fields are not displayed on public profiles.

---

### P0-006: Post model

**Application:** `posts`

```text
Post
├── id
├── public_id: UUID
├── author: User
├── body
├── image
├── image_alt_text
├── created_at
├── updated_at
├── deleted_at
└── moderation_status
```

Suggested status values:

```text
ACTIVE
HIDDEN
REMOVED
```

**Rules**

* At least one of `body` or `image` is required.
* Body is stored as plain text.
* Deleted posts are soft-deleted.
* The default query path should exclude deleted posts.
* Image alt text is optional initially but presented in the form.

**Acceptance criteria**

* Empty posts are rejected.
* Whitespace-only posts are rejected.
* Text-only posts are valid.
* Image-only posts are valid.
* Text-and-image posts are valid.
* Soft-deleted posts disappear from ordinary feeds.
* Deleting a user follows a documented retention policy.

---

### P0-007: Activity event model

**Application:** `common`

```text
ActivityEvent
├── actor: nullable User
├── event_type
├── object_type
├── object_public_id
├── metadata: JSON
├── request_id
└── created_at
```

Initial event types:

```text
ACCOUNT_REGISTERED
LOGIN_SUCCEEDED
LOGIN_FAILED
PROFILE_UPDATED
POST_CREATED
POST_UPDATED
POST_DELETED
IMAGE_UPLOAD_REJECTED
```

**Rules**

* Do not store passwords, cookies, tokens, or full post bodies.
* Metadata should contain identifiers and operational context only.
* Event creation failures must not normally break user-facing actions.

**Acceptance criteria**

* Important authentication and content actions produce events.
* Sensitive values are not present in event metadata.
* Events are visible to authorized staff in Django Admin.

---

## Phase 0 Migrations

### Required migration order

```text
accounts/
└── 0001_initial.py

common/
└── 0001_activity_event.py

profiles/
└── 0001_initial.py

posts/
└── 0001_initial.py
```

### Migration tasks

* Add database constraints for unique public IDs.
* Add case-insensitive handle and email uniqueness where supported.
* Add an index on `Post(created_at)`.
* Add an index on `Post(author, created_at)`.
* Add an index on `Post(moderation_status, created_at)`.
* Add an index on `ActivityEvent(event_type, created_at)`.

**Acceptance criteria**

* All migrations run on a new empty database.
* All migrations reverse successfully in development.
* Migration tests do not depend on preexisting local data.
* The custom user migration is the first user-related migration.

---

## Phase 0 Forms and Validation

### P0-008: Registration form

Fields:

* Username.
* Email.
* Password.
* Password confirmation.
* Agreement to platform terms.

**Acceptance criteria**

* Password validation uses Django’s configured validators.
* Duplicate username and email errors are understandable.
* Registration does not reveal whether an email belongs to a suspended account.
* Registration is rate-limited.

---

### P0-009: Profile form

Fields:

* Handle.
* Display name.
* Biography.
* Profile image.

**Acceptance criteria**

* Users can edit only their own profile.
* Invalid handles are rejected.
* Oversized or malformed images are rejected.
* Existing profile images remain unchanged when no replacement is uploaded.

---

### P0-010: Post form

Fields:

* Body.
* Image.
* Image alt text.

**Validation**

* Maximum body length.
* At least one content field.
* JPEG, PNG, or WebP only.
* Maximum file size.
* Maximum dimensions and pixel count.
* Actual image decoding through Pillow.
* Safe re-encoding.
* Randomized server filename.

**Acceptance criteria**

* A renamed executable is not accepted as an image.
* Invalid image data produces a form error.
* Image metadata is stripped where configured.
* Upload errors do not expose storage paths.

---

## Phase 0 Services and Selectors

### Services

```text
accounts.services.register_user()
profiles.services.update_profile()
posts.services.create_post()
posts.services.update_post()
posts.services.soft_delete_post()
posts.services.process_uploaded_image()
```

### Selectors

```text
profiles.selectors.get_public_profile()
posts.selectors.get_dashboard_feed()
posts.selectors.get_post_for_display()
posts.selectors.get_owned_post()
```

**Acceptance criteria**

* Views do not contain image-processing logic.
* Views do not duplicate ownership checks.
* State-changing operations are wrapped in transactions where needed.
* Feed selectors exclude deleted and removed posts.

---

## Phase 0 Views and Routes

### Authentication

```text
/accounts/register/              accounts:register
/accounts/login/                 accounts:login
/accounts/logout/                accounts:logout
/accounts/password-change/       accounts:password_change
/accounts/password-reset/        accounts:password_reset
```

### Profiles

```text
/profiles/<handle>/              profiles:detail
/profiles/edit/                  profiles:edit
```

### Posts

```text
/posts/create/                   posts:create
/posts/<uuid:public_id>/         posts:detail
/posts/<uuid:public_id>/edit/    posts:edit
/posts/<uuid:public_id>/delete/  posts:delete
```

### Dashboard

```text
/                               redirect based on authentication
/dashboard/                     dashboard:index
/health/                        common:health
```

**Acceptance criteria**

* Unauthenticated users are redirected from protected views.
* Authenticated users visiting `/` are sent to the dashboard.
* Anonymous users visiting `/` are sent to login.
* Edit and delete views retrieve posts by both public ID and owner.
* Destructive operations cannot be triggered by GET requests.
* A missing or inaccessible post returns 404 without revealing ownership information.

---

## Phase 0 Templates

```text
templates/
├── base.html
├── registration/
│   ├── login.html
│   ├── register.html
│   ├── password_reset_form.html
│   ├── password_reset_done.html
│   └── password_reset_confirm.html
├── components/
│   ├── navigation.html
│   ├── form_errors.html
│   ├── flash_messages.html
│   ├── post_card.html
│   └── pagination.html
└── errors/
    ├── 400.html
    ├── 403.html
    ├── 404.html
    └── 500.html

apps/profiles/templates/profiles/
├── detail.html
└── edit.html

apps/posts/templates/posts/
├── create.html
├── detail.html
├── edit.html
└── confirm_delete.html

apps/dashboard/templates/dashboard/
└── index.html
```

**Template requirements**

* Visible keyboard focus.
* Proper form labels.
* Accessible validation summaries.
* Image alt text rendered when supplied.
* Post text escaped by Django.
* Delete actions require confirmation.
* Pagination remains functional without JavaScript.

---

## Phase 0 HTMX Tasks

### P0-011: Progressive post creation

* Submit the dashboard composer through HTMX.
* Return the new post-card fragment.
* Return the normal redirect for non-HTMX requests.
* Replace the form with validation errors when invalid.

### P0-012: Progressive post deletion

* Request a confirmation fragment.
* Remove the post card after successful deletion.
* Preserve the ordinary confirmation page fallback.

**Acceptance criteria**

* Core posting and deletion work with JavaScript disabled.
* HTMX requests receive fragments rather than complete pages.
* CSRF protection remains enabled.
* Browser back and refresh behavior remains understandable.

---

## Phase 0 Tests

### Model tests

* Custom user creation.
* Unique email and username.
* Profile one-to-one relationship.
* Case-insensitive handle uniqueness.
* Post content requirement.
* Soft deletion behavior.
* Public UUID generation.
* Activity-event creation.

### Form tests

* Valid and invalid registration.
* Password mismatch.
* Invalid handle.
* Empty post.
* Text-only post.
* Image-only post.
* Invalid MIME extension.
* Corrupt image.
* Excessive file size.
* Excessive pixel dimensions.

### View tests

* Anonymous redirect behavior.
* Login success and failure.
* Logout.
* Password reset request.
* Profile visibility.
* Profile ownership.
* Post creation.
* Post editing.
* Post deletion.
* Cross-user edit attempt.
* Cross-user delete attempt.
* Dashboard pagination.

### Security tests

* CSRF rejection.
* Secure-cookie production settings.
* Upload filename randomization.
* HTML escaping in post body.
* No destructive GET routes.
* Generic authentication failure messages.
* Rate-limit behavior.
* Custom error pages.

### Integration tests

1. Register → profile created → login → dashboard.
2. Create text post → appears in feed.
3. Upload image → processed image appears.
4. Edit post → updated content appears.
5. Delete post → removed from dashboard.
6. Another user cannot edit or delete it.

---

## Phase 0 Release Acceptance Criteria

Phase 0 is complete when:

* A fresh environment can be created from the repository documentation.
* A user can complete the full account and posting flow.
* Text and image uploads are validated safely.
* Ownership is enforced on the server.
* The dashboard is paginated.
* Core actions work without JavaScript.
* Required tests pass against PostgreSQL.
* Production settings pass Django deployment checks.
* The system can be deployed behind HTTPS.
* No trust score, public reputation, or recommendation algorithm exists.

---

# Phase 1 — Interaction and User Boundaries

## Phase objective

Allow users to converse, express gratitude, and control unwanted interactions without introducing public dislike counts or universal reputation.

---

## Phase 1 Models

### P1-001: Reply model

**Application:** `interactions`

```text
Reply
├── public_id: UUID
├── post: Post
├── author: User
├── parent: nullable Reply
├── body
├── created_at
├── updated_at
└── deleted_at
```

**Rules**

* Only one reply nesting level is allowed.
* Parent replies must belong to the same post.
* Empty replies are invalid.
* Replies use soft deletion.
* Deleted replies may display a neutral placeholder when descendants exist.

**Acceptance criteria**

* A user can reply to a post.
* A user can reply to a top-level reply.
* A user cannot create a third nesting level.
* A user cannot attach a reply to a parent from another post.
* Only the author or authorized moderator can edit or delete a reply.

---

### P1-002: Thank-you model

```text
ThankYou
├── sender: User
├── post: nullable Post
├── reply: nullable Reply
├── created_at
└── optional_note
```

**Constraints**

* Exactly one target must be populated.
* One thank-you per sender per target.
* A user cannot thank deleted or removed content.
* Self-thanks are rejected.

**Acceptance criteria**

* A user can thank a post or reply once.
* Repeating the action is idempotent or returns a clear response.
* Removing a thank-you does not delete its historical activity event.
* Public totals may be shown, but sender visibility is private by default.

---

### P1-003: Notification model

```text
Notification
├── recipient
├── actor: nullable User
├── kind
├── post: nullable Post
├── reply: nullable Reply
├── thank_you: nullable ThankYou
├── payload: JSON
├── read_at
└── created_at
```

Initial kinds:

```text
REPLY_RECEIVED
REPLY_TO_REPLY
THANK_YOU_RECEIVED
REPORT_RESOLVED
```

**Acceptance criteria**

* Users receive notifications for replies and thanks.
* Users do not receive notifications for their own actions.
* Notifications have stable destination URLs.
* Marking a notification read is restricted to its recipient.

---

### P1-004: Hidden post model

```text
HiddenPost
├── user
├── post
└── created_at
```

Unique constraint:

```text
(user, post)
```

**Acceptance criteria**

* Hidden posts disappear only for the user who hid them.
* Hiding content is not treated as a misconduct report.
* A user can restore hidden content from settings.

---

### P1-005: Mute model

```text
UserMute
├── muting_user
├── muted_user
└── created_at
```

**Acceptance criteria**

* Muted users’ content is excluded from the muting user’s normal feed.
* The muted user is not notified.
* Muting does not prevent direct profile access unless separately configured.
* Users cannot mute themselves.

---

### P1-006: Block model

```text
UserBlock
├── blocking_user
├── blocked_user
├── created_at
└── optional_reason_code
```

**Behavior**

* Blocked users cannot reply to or interact with the blocker’s content.
* The blocker does not see the blocked user in normal feeds.
* Existing content remains retained for moderation and audit purposes.
* The block relationship is not publicly visible.

**Acceptance criteria**

* A blocked user cannot add replies or thanks to the blocker’s content.
* Both users’ normal recommendation and feed paths exclude one another.
* Unblocking restores future interaction eligibility.
* Users cannot block themselves.

---

### P1-007: Content report model

```text
ContentReport
├── reporter
├── post: nullable Post
├── reply: nullable Reply
├── reason
├── details
├── status
├── assigned_to: nullable staff User
├── resolution_note
├── resolved_at
└── created_at
```

Initial reasons:

```text
HARASSMENT
THREAT
HATE_OR_DEHUMANIZATION
SPAM
IMPERSONATION
PRIVACY
COORDINATED_ABUSE
OTHER
```

Statuses:

```text
OPEN
IN_REVIEW
RESOLVED_ACTIONED
RESOLVED_NO_ACTION
DUPLICATE
```

**Acceptance criteria**

* Exactly one content target is required.
* A report is private to the reporter and staff.
* Duplicate reports may be grouped without losing individual records.
* Reports do not automatically remove content.
* Staff can record a resolution in Django Admin.

---

## Phase 1 Migrations

```text
interactions/
├── 0001_reply.py
├── 0002_thank_you.py
├── 0003_notification.py
└── 0004_boundaries_and_reports.py
```

### Required constraints and indexes

* Reply index on `(post, created_at)`.
* Reply index on `(author, created_at)`.
* Unique thank-you constraints per target.
* Check constraint requiring exactly one thank-you target.
* Unique mute relationship.
* Unique block relationship.
* Unique hidden-post relationship.
* Report index on `(status, created_at)`.
* Check constraint requiring exactly one report target.

**Acceptance criteria**

* Migrations succeed with existing Phase 0 data.
* Invalid cross-target rows are rejected by the database.
* Existing posts remain visible and usable.

---

## Phase 1 Services and Selectors

### Services

```text
interactions.services.create_reply()
interactions.services.update_reply()
interactions.services.delete_reply()
interactions.services.toggle_thank_you()
interactions.services.hide_post()
interactions.services.unhide_post()
interactions.services.mute_user()
interactions.services.unmute_user()
interactions.services.block_user()
interactions.services.unblock_user()
interactions.services.submit_report()
interactions.services.mark_notification_read()
```

### Selectors

```text
interactions.selectors.get_post_replies()
interactions.selectors.get_user_notifications()
interactions.selectors.get_unread_notification_count()
interactions.selectors.get_hidden_posts()
interactions.selectors.apply_user_boundaries_to_feed()
```

**Acceptance criteria**

* Block rules are enforced within services, not only templates.
* Feed boundary filtering is implemented once and reused.
* Notification creation occurs transactionally with the triggering action.

---

## Phase 1 Views and Routes

```text
/posts/<uuid:post_id>/replies/create/
/replies/<uuid:reply_id>/edit/
/replies/<uuid:reply_id>/delete/

/posts/<uuid:post_id>/thank/
/replies/<uuid:reply_id>/thank/

/notifications/
/notifications/<int:id>/read/
/notifications/read-all/

/posts/<uuid:post_id>/hide/
/settings/hidden-posts/
/profiles/<handle>/mute/
/profiles/<handle>/block/

/posts/<uuid:post_id>/report/
/replies/<uuid:reply_id>/report/
```

**Acceptance criteria**

* All state changes require POST.
* Blocked users receive a neutral authorization response.
* Reports can be submitted without exposing prior reporters.
* Notification counts update through an HTMX fragment.
* Anonymous users cannot reply, thank, mute, block, hide, or report.

---

## Phase 1 Templates

```text
interactions/
├── reply_form.html
├── reply_item.html
├── reply_list.html
├── thank_you_button.html
├── notification_list.html
├── notification_item.html
├── report_form.html
├── mute_confirm.html
├── block_confirm.html
└── hidden_posts.html
```

### Interface requirements

* Thank-you is visually distinct from a generic like.
* Reporting is not presented as a dislike action.
* Block and mute explain their different effects.
* Deleted replies use neutral text such as “Reply removed.”
* Report forms show concise definitions of each reason.
* The interface does not reveal who muted, blocked, or negatively evaluated another user.

---

## Phase 1 Tests

### Reply tests

* Create top-level reply.
* Create one nested reply.
* Reject deeper nesting.
* Reject cross-post parent.
* Edit own reply.
* Reject editing another user’s reply.
* Delete reply with and without descendants.
* Reject reply when blocked.

### Thank-you tests

* Thank a post.
* Thank a reply.
* Reject self-thank.
* Prevent duplicates.
* Remove thank-you.
* Notification created.
* Deleted content cannot be thanked.

### Boundary tests

* Hidden post excluded for one user only.
* Muted user excluded from feed.
* Muted user is not notified.
* Blocked user cannot reply.
* Blocked user cannot thank.
* Unblock restores interaction.
* Boundary controls survive pagination.

### Report tests

* Report post.
* Report reply.
* Reject empty or invalid target.
* Reporter cannot access staff notes.
* Staff can change report status.
* Report submission does not automatically hide content globally.

### Notification tests

* Correct notification recipient.
* No self-notification.
* Mark one read.
* Mark all read.
* Cross-user read attempt rejected.
* Notification link resolves correctly.

### Integration scenario

1. User A creates a post.
2. User B replies.
3. User A receives a notification.
4. User A thanks the reply.
5. User B receives a notification.
6. User A mutes User B.
7. User B’s later posts no longer appear in User A’s feed.
8. User A blocks User B.
9. User B can no longer interact with User A’s content.

---

## Phase 1 Release Acceptance Criteria

Phase 1 is complete when:

* Users can hold threaded conversations with one nesting level.
* Users can express gratitude without a generic like system.
* Notifications are functional and private.
* Users can hide individual posts.
* Users can mute or block other users.
* Reports reach a staff review queue.
* Personal controls do not automatically punish the affected user.
* Block rules are enforced in services and views.
* No public dislike count or universal reputation score exists.

---

# Phase 2 — Prosocial Actions and Commitments

## Phase objective

Allow users to move from ordinary discussion into concrete, trackable actions while keeping commitments private by default.

---

## Phase 2 Models

### P2-001: Add post kind

Add a `kind` field to `Post`.

Suggested choices:

```text
GENERAL
HELP_REQUEST
HELP_OFFER
ENCOURAGEMENT_REQUEST
LOCAL_ACTION
VOLUNTEER_OPPORTUNITY
```

Default existing posts to:

```text
GENERAL
```

**Acceptance criteria**

* Existing posts remain valid.
* Users can filter the feed by post kind.
* A post kind does not imply that an action was completed.

---

### P2-002: Action opportunity model

**Application:** `prosocial_actions`

```text
ActionOpportunity
├── public_id: UUID
├── post: one-to-one Post
├── creator: User
├── status
├── location_label
├── starts_at
├── ends_at
├── capacity
├── verification_mode
├── completion_instructions
├── created_at
└── updated_at
```

Status values:

```text
OPEN
FULL
COMPLETED
CANCELLED
EXPIRED
```

Verification modes:

```text
SELF_REPORTED
CREATOR_CONFIRMED
RECIPIENT_CONFIRMED
NO_VERIFICATION
```

**Rules**

* Precise addresses should not be publicly required.
* End time cannot precede start time.
* Capacity must be positive when supplied.
* Cancelled or expired actions cannot accept new commitments.

**Acceptance criteria**

* A qualifying post can have one action opportunity.
* Ordinary posts do not require an action opportunity.
* Invalid scheduling and capacity data is rejected.
* The creator can cancel but not silently erase an action with commitments.

---

### P2-003: Commitment model

```text
Commitment
├── public_id: UUID
├── action: ActionOpportunity
├── participant: User
├── status
├── scheduled_for
├── reminder_at
├── is_public: default False
├── private_note
├── committed_at
├── completed_at
├── withdrawn_at
└── updated_at
```

Status values:

```text
SAVED
COMMITTED
COMPLETION_SUBMITTED
VERIFIED
REJECTED
WITHDRAWN
EXPIRED
```

**Rules**

* Commitments are private by default.
* A user can have only one active commitment per action.
* Private notes are visible only to the participant.
* State transitions must occur through services.
* Completing an action should not automatically publish a celebratory post.

**Acceptance criteria**

* A user can save an action without committing.
* A user can commit immediately or schedule participation.
* A user can withdraw before completion.
* A user cannot commit after cancellation or expiration.
* Private commitments are not listed publicly.

---

### P2-004: Completion submission model

```text
CompletionSubmission
├── commitment: one-to-one Commitment
├── participant_note
├── submitted_at
├── reviewed_by
├── review_status
├── reviewer_note
└── reviewed_at
```

Review statuses:

```text
PENDING
VERIFIED
REJECTED
NOT_REQUIRED
```

**Acceptance criteria**

* A participant can submit completion once.
* Creator-confirmed actions enter `PENDING`.
* Self-reported actions can become `NOT_REQUIRED` or completed according to policy.
* Only authorized reviewers can verify completion.
* Rejection includes a participant-visible reason.

---

### P2-005: Action invitation model

```text
ActionInvitation
├── public_id: UUID
├── action
├── inviter
├── invitee
├── status
├── message
├── created_at
└── responded_at
```

Status values:

```text
PENDING
ACCEPTED
DECLINED
CANCELLED
EXPIRED
```

Initial scope:

* Registered-user invitations only.
* No email-address invitations in the first implementation.

**Acceptance criteria**

* A user can invite one or more existing users.
* Duplicate pending invitations are prevented.
* Blocked users cannot invite one another.
* Accepting an invitation can create a commitment transactionally.
* Declining an invitation does not notify unrelated users.

---

### P2-006: Action acknowledgement model

```text
ActionAcknowledgement
├── commitment
├── sender
├── recipient
├── message
└── created_at
```

**Rules**

* Used after submitted or verified completion.
* Optional.
* Private by default.
* Not displayed as a public reputation score.

**Acceptance criteria**

* A creator or recipient can acknowledge a completed action.
* Duplicate acknowledgement from the same sender is prevented.
* The participant receives a notification.
* Acknowledgements do not alter verification status.

---

## Phase 2 Migrations

```text
posts/
└── 0002_add_post_kind.py

prosocial_actions/
├── 0001_action_opportunity.py
├── 0002_commitment.py
├── 0003_completion_submission.py
└── 0004_invitation_and_acknowledgement.py
```

### Required constraints and indexes

* Index on `Post(kind, created_at)`.
* Unique one-to-one relation between post and action opportunity.
* Index on `ActionOpportunity(status, starts_at)`.
* Index on `Commitment(participant, status)`.
* Partial or service-enforced uniqueness for active commitment.
* Unique completion submission per commitment.
* Unique pending invitation per inviter, invitee, and action.
* Unique acknowledgement per sender and commitment.

**Acceptance criteria**

* Existing general posts are migrated safely.
* The migration does not require action records for old posts.
* Invalid action times are rejected at validation and, where practical, database level.
* Rollback is documented before production deployment.

---

## Phase 2 Forms

### Action opportunity form

Fields vary by post kind:

* Action type.
* Description through associated post body.
* General location label.
* Start and end.
* Capacity.
* Verification mode.
* Completion instructions.

### Commitment form

* Commit now or schedule.
* Scheduled date and time.
* Reminder preference.
* Private note.
* Optional public participation toggle, default off.

### Completion form

* Completion note.
* Optional evidence attachment deferred unless clearly required.

### Invitation form

* Invitee.
* Short message.

**Acceptance criteria**

* Irrelevant fields are hidden or rejected based on action type.
* Commitments default to private.
* Reminder time cannot occur after scheduled participation.
* A user cannot invite themselves.
* Block relationships are enforced during validation and service execution.

---

## Phase 2 Services and Selectors

### Services

```text
prosocial_actions.services.create_action_post()
prosocial_actions.services.update_action()
prosocial_actions.services.cancel_action()
prosocial_actions.services.save_action()
prosocial_actions.services.commit_to_action()
prosocial_actions.services.withdraw_commitment()
prosocial_actions.services.submit_completion()
prosocial_actions.services.verify_completion()
prosocial_actions.services.reject_completion()
prosocial_actions.services.invite_user()
prosocial_actions.services.accept_invitation()
prosocial_actions.services.decline_invitation()
prosocial_actions.services.send_acknowledgement()
prosocial_actions.services.generate_due_reminders()
```

### Selectors

```text
prosocial_actions.selectors.get_open_actions()
prosocial_actions.selectors.get_action_detail()
prosocial_actions.selectors.get_user_commitments()
prosocial_actions.selectors.get_pending_verifications()
prosocial_actions.selectors.get_pending_invitations()
prosocial_actions.selectors.get_due_reminders()
```

### State-transition requirement

Commitment transitions should be explicit.

Example:

```text
SAVED -> COMMITTED
SAVED -> WITHDRAWN
COMMITTED -> COMPLETION_SUBMITTED
COMMITTED -> WITHDRAWN
COMPLETION_SUBMITTED -> VERIFIED
COMPLETION_SUBMITTED -> REJECTED
```

Invalid transitions must raise a domain-specific exception.

---

## Phase 2 Views and Routes

```text
/actions/
/actions/create/
/actions/<uuid:public_id>/
/actions/<uuid:public_id>/edit/
/actions/<uuid:public_id>/cancel/

/actions/<uuid:public_id>/save/
/actions/<uuid:public_id>/commit/
/actions/<uuid:public_id>/withdraw/
/actions/<uuid:public_id>/complete/

/commitments/
/commitments/<uuid:public_id>/

/commitments/<uuid:public_id>/verify/
/commitments/<uuid:public_id>/reject/
/commitments/<uuid:public_id>/acknowledge/

/actions/<uuid:public_id>/invite/
/invitations/
/invitations/<uuid:public_id>/accept/
/invitations/<uuid:public_id>/decline/
```

**Acceptance criteria**

* Action creation is available only to authenticated users.
* Only the creator can edit or cancel an action.
* Participants cannot verify their own creator-confirmed completion.
* Commitment privacy is enforced in every view.
* Invitation acceptance is transactional.
* State-changing actions reject GET requests.

---

## Phase 2 Templates

```text
prosocial_actions/
├── action_list.html
├── action_card.html
├── action_detail.html
├── action_form.html
├── action_cancel_confirm.html
├── commitment_form.html
├── commitment_list.html
├── commitment_detail.html
├── completion_form.html
├── verification_queue.html
├── verification_detail.html
├── invitation_form.html
├── invitation_list.html
└── acknowledgement_form.html
```

### Interface requirements

* Clearly distinguish:

  * Saving.
  * Committing.
  * Completing.
  * Verification.
* Do not describe a saved action as completed.
* Display privacy state near commitment controls.
* Allow reminders to be declined.
* Avoid guilt-based copy.
* Avoid public streaks, rankings, or virtue badges.
* Explain who will verify an action before commitment.

---

## Phase 2 Reminder Implementation

### Initial approach

Do not add a full distributed task queue yet.

Implement:

```text
python manage.py send_due_commitment_reminders
```

Run it through the deployment scheduler at a reasonable interval.

The command should:

1. Select due reminders.
2. Create an in-app notification.
3. Mark the reminder as dispatched.
4. Avoid duplicate delivery.
5. Record an activity event.

A background worker can replace this later without changing the domain model.

**Acceptance criteria**

* Running the command twice does not send duplicate reminders.
* Withdrawn or cancelled commitments do not receive reminders.
* Reminder text does not use guilt or urgency unless the underlying action is genuinely time-sensitive.
* Users can disable future reminders.

---

## Phase 2 Tests

### Action opportunity tests

* Create each supported action type.
* Reject invalid schedule.
* Reject zero or negative capacity.
* Cancel action.
* Expire action.
* Prevent commitments to closed action.
* Preserve action history after cancellation.

### Commitment tests

* Save action.
* Commit immediately.
* Schedule commitment.
* Default privacy is private.
* Reject duplicate active commitment.
* Withdraw commitment.
* Reject invalid status transition.
* Capacity changes when commitment is created or withdrawn.
* Race-condition test for final capacity slot.

### Completion tests

* Submit completion.
* Prevent duplicate submission.
* Self-reported flow.
* Creator-confirmed flow.
* Verify completion.
* Reject completion with reason.
* Unauthorized verification rejected.

### Invitation tests

* Send invitation.
* Reject self-invitation.
* Reject blocked-user invitation.
* Prevent duplicate pending invitation.
* Accept invitation and create commitment.
* Decline invitation.
* Cancel invitation.
* Reject acceptance after action closes.

### Reminder tests

* Due reminder selected.
* Future reminder ignored.
* Duplicate run is idempotent.
* Withdrawn commitment ignored.
* Notification generated correctly.
* User preference disables reminder.

### Privacy tests

* Private commitment absent from public action page.
* Public commitment shown only when deliberately enabled.
* Private notes visible only to participant.
* Verification notes visible only to authorized parties.
* Invitations visible only to inviter and invitee.

### Integration scenario

1. User A creates a help-request action.
2. User B saves it privately.
3. User B schedules a commitment and reminder.
4. Reminder notification is generated.
5. User B submits completion.
6. User A verifies completion.
7. User A sends a private acknowledgement.
8. User B receives the acknowledgement notification.
9. No public reputation score is changed or displayed.

---

## Phase 2 Release Acceptance Criteria

Phase 2 is complete when:

* Users can publish structured requests, offers, and opportunities.
* Users can save or commit to an action.
* Commitments are private by default.
* Users can schedule actions and optional reminders.
* Completion can be submitted and, when required, verified.
* Users can invite another registered user.
* Blocks and privacy controls apply to invitations and actions.
* The application distinguishes interest, commitment, completion, and verification.
* Acknowledgement exists without public status competition.
* Real completed actions can now be measured separately from posts and reactions.

---

# Recommended Ticket Order

## Phase 0

```text
P0-001 Project skeleton
P0-002 Tooling and CI
P0-003 Common timestamp model
P0-004 Custom user
P0-005 Profile
P0-006 Post
P0-007 Activity events
P0-008 Registration
P0-009 Profile editing
P0-010 Post and upload validation
P0-011 HTMX post creation
P0-012 HTMX deletion
Production deployment and security pass
```

## Phase 1

```text
P1-001 Replies
P1-002 Thank-you
P1-003 Notifications
P1-004 Hidden posts
P1-005 Mutes
P1-006 Blocks
P1-007 Reports
Feed integration
Admin moderation queue
Phase 1 security and integration pass
```

## Phase 2

```text
P2-001 Post kinds
P2-002 Action opportunities
P2-003 Commitments
P2-004 Completion submissions
P2-005 Invitations
P2-006 Acknowledgements
Reminder command
Action filters and dashboards
Phase 2 privacy and concurrency pass
```

---

# Explicitly Deferred Beyond Phase 2

The following should not be added during this backlog:

* Multidimensional reply ratings.
* Trust-edge calculations.
* Trust-informed feed ranking.
* LLM moderation.
* Public reputation.
* Public leaderboards.
* Donations or payment processing.
* External volunteer-service integrations.
* Multiple post attachments.
* Video.
* Direct messaging.
* Graph databases.
* Redis unless required for measured load or distributed rate limiting.
* Celery or another task queue unless scheduler-based reminders become insufficient.
* Mobile applications or a public API.
