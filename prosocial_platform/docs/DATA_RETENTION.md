# Data Retention Policy

## User account deletion

When a user account is deleted (via admin action or future self-service):

1. **Profile** — Removed with the user (CASCADE).
2. **Posts** — Soft-deleted (`deleted_at` set); content retained for moderation audit.
3. **Replies** — Soft-deleted; retained for thread integrity where descendants exist.
4. **Activity events** — Retained with `actor` set to NULL.
5. **Notifications, thank-yous, boundaries** — Removed with the user (CASCADE).
6. **Content reports** — Retained; reporter reference set to NULL if reporter deleted.
7. **Commitments and actions** — Retained for audit; participant/creator references set to NULL where applicable.

Sequential database IDs are never exposed in public URLs; only `public_id` UUIDs are used.
