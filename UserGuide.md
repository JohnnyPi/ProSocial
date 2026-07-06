# Common Good — User Guide

*A complete guide to the Prosocial Platform as it exists today. Each section states the **intent** of a feature, how to use it, and whether it is fully working, partially implemented, or not yet available.*

**Last reviewed:** July 2026 · **App version:** Phases 0–11 scaffold (mixed maturity)

---

## Table of Contents

1. [What Is Common Good?](#1-what-is-common-good)
2. [Getting Started](#2-getting-started)
3. [Navigation & Layout](#3-navigation--layout)
4. [Home Feed & Posting](#4-home-feed--posting)
5. [Profiles](#5-profiles)
6. [Interactions — Replies, Gratitude & Boundaries](#6-interactions--replies-gratitude--boundaries)
7. [Knowledge — Clips, Vault & Collections](#7-knowledge--clips-vault--collections)
8. [Prosocial Actions](#8-prosocial-actions)
9. [Following People & Threads](#9-following-people--threads)
10. [Guilds](#10-guilds)
11. [Messaging](#11-messaging)
12. [Discovery](#12-discovery)
13. [Trust & Helper Style](#13-trust--helper-style)
14. [Gamification — XP, Streaks & Badges](#14-gamification--xp-streaks--badges)
15. [AI Coach — Reflection & Pre-Send Prompts](#15-ai-coach--reflection--pre-send-prompts)
16. [Engagement — Challenges & Rest Mode](#16-engagement--challenges--rest-mode)
17. [Moderation & Safety](#17-moderation--safety)
18. [Advanced — Donations, Skills & Data Export](#18-advanced--donations-skills--data-export)
19. [Account Settings & Privacy](#19-account-settings--privacy)
20. [Feature Status Summary](#20-feature-status-summary)
21. [Known Gaps & Redundancies](#21-known-gaps--redundancies)

---

## 1. What Is Common Good?

**Intent:** Common Good is a prosocial social network designed to reward *helpfulness, cooperation, and genuine community contribution* — not raw popularity or screen time. The north-star metric is whether people become better community members, not how long they stay logged in.

**Core ideas that shape every feature:**

| Principle | What it means for you |
|-----------|----------------------|
| **Prosocial over popularity** | A post with three deeply helpful replies matters more than one with hundreds of shallow likes. |
| **Knowledge outlasts conversation** | Good contributions are meant to be clipped, collected, and reused — not lost in the feed. |
| **Gentle friction before harm** | You may see a soft reflection prompt before posting something flagged as negative — never a silent block. |
| **Growth is the metric** | XP, trust scores, and badges reward prosocial skill development, not addiction. |
| **AI as coach, not cop** | Automated suggestions encourage and explain; humans make every binding moderation decision. |

---

## 2. Getting Started

### Registration

**Intent:** Create a secure account and a public profile in one step so you can immediately participate in the community.

| Step | Detail |
|------|--------|
| **Route** | `/accounts/register/` |
| **Status** | ✅ Fully implemented |
| **What you do** | Choose a username, email, and password; accept terms; submit. |
| **What happens** | Account and profile are created; you are logged in automatically. |

### Sign In & Sign Out

**Intent:** Standard secure authentication with rate limiting to prevent brute-force attacks.

| Action | Route | Status |
|--------|-------|--------|
| Sign in | `/accounts/login/` | ✅ Fully implemented |
| Sign out | POST to `/accounts/logout/` | ✅ Fully implemented (button in left sidebar footer) |

### Password Management

**Intent:** Let you recover or change credentials without admin help.

| Action | Route | Status |
|--------|-------|--------|
| Change password | `/accounts/password-change/` | ✅ Fully implemented |
| Reset password (email flow) | `/accounts/password-reset/` | ✅ Fully implemented |

> **Not available:** Multi-factor authentication (MFA) is not implemented.

### Test Accounts (Development)

For local testing, five seeded accounts share the password `TestPass123!`. See `prosocial_platform/README.md` for handles (`test_river`, `test_morgan`, etc.).

---

## 3. Navigation & Layout

When signed in, the interface uses a three-column **app shell**:

```
┌─────────────────┬──────────────────────────┬─────────────────┐
│  Left sidebar   │      Main content        │   Right rail    │
│  (primary nav)  │      (feed, pages)       │   (context)     │
└─────────────────┴──────────────────────────┴─────────────────┘
```

### Left Sidebar (Primary Navigation)

**Intent:** Persistent access to every major area of the platform.

| Link | Route | Purpose |
|------|-------|---------|
| **Home** | `/dashboard/` | Your main feed and post composer |
| **Knowledge** | `/dashboard/knowledge/` | Knowledge hub — collections, followed threads, links to vault |
| **Guilds** | `/guilds/` | Community groups around causes or interests |
| **Messages** | `/messages/` | Private 1:1 conversations (badge shows unread count) |
| **Discover** | `/discovery/` | Find highly clipped and sentiment-boosted content |
| **Actions** | `/actions/` | Help requests, offers, local actions, volunteer opportunities |
| **Notifications** | `/notifications/` | Replies, thank-yous, invitations, and system alerts |
| **Profile** | `/profiles/<your-handle>/` | Your public profile page |

Footer links: **Edit profile** · **Log out**

### Right Rail (Context Panel)

**Intent:** Surface actionable community context — open help near you, pending invitations, your active commitments, and trust signals.

| Panel | Status | What it shows |
|-------|--------|---------------|
| **You** | ⚠️ Partial | Your avatar, name, handle — plus a **hardcoded** "◐ New here" badge (not tied to real trust data) |
| **Your circles** | ❌ Placeholder | Copy says *"Circles are coming soon"*; chips link to feed filters (Requests, Offers, Local) |
| **Invitations** | ✅ Working | Pending action invitations (when any exist) |
| **Open near you** | ✅ Working | Open action opportunities |
| **Your commitments** | ✅ Working | Your active commitments with status |
| **Trust** | ⚠️ Placeholder | Copy says vouches *"will show plainly here"*; shows a **hardcoded** "✔ Verified helper" badge |

> **Gap:** The right rail does **not** link to your Vault, Collections, or saved clips — even though clipping works. Saved content is only reachable via Knowledge → Vault or by direct URL.

### Guest Navigation

Visitors who are not signed in see a simplified top bar with **Sign in** and **Join** links.

> **Redundancy:** An older top navigation component (`navigation.html`) still exists in the codebase but is **not used** by the current layout. The app shell (`shell_left.html`) is the active navigation.

---

## 4. Home Feed & Posting

### Dashboard Feed

**Intent:** A personalized, paginated stream of community posts — weighted toward constructive content, with a natural stopping point ("you're caught up") rather than infinite scroll.

| Feature | Status | Detail |
|---------|--------|--------|
| Paginated feed | ✅ | Posts load page by page |
| Feed mode: **All** | ✅ | Every visible post |
| Feed mode: **Following** | ✅ | Posts from people you follow + your guilds |
| Kind filters | ⚠️ Partial | Chips for General, Requests, Offers, Local — **not** Encouragement or Volunteer |
| "Caught up" endpoint | ✅ | Shown when you've seen all posts |

**Route:** `/dashboard/` · Filter with `?feed=following` or `?kind=HELP_REQUEST`

### Creating a Post

**Intent:** Share text and optional images with the community. A pre-send reflection prompt may appear if your draft contains negative keywords.

| Method | Route | Status |
|--------|-------|--------|
| **Dashboard composer** (primary) | POST to `/dashboard/` | ✅ Modal on Home; HTMX prepends new post to feed |
| **Standalone create page** | `/posts/create/` | ✅ Works but **not linked** from sidebar nav |

**Fields available when posting:**

| Field | In UI? | Notes |
|-------|--------|-------|
| Body (text) | ✅ | Required |
| Image | ✅ | Processed and validated on upload |
| Image alt text | ✅ | Accessibility |
| Post kind | ❌ | Model supports HELP_REQUEST, HELP_OFFER, etc. — only set via Actions app or test data |
| Thread type | ❌ | Model only (Discussion, Help Request, Knowledge Share, etc.) |
| Title | ❌ | Model only |
| Guild | ❌ | Model only |

> **Redundancy:** Two post-creation entry points exist (dashboard modal and `/posts/create/`). Only the dashboard modal is linked in the UI.

### Viewing, Editing & Deleting Posts

| Action | Route | Status |
|--------|-------|--------|
| View post | `/posts/<uuid>/` | ✅ Public (no login required) |
| Edit own post | `/posts/<uuid>/edit/` | ✅ Owner only |
| Delete own post | `/posts/<uuid>/delete/` | ✅ Soft delete; owner only |

### Post Detail Page Actions

From a post's detail page you can:

- **Reply** — add a threaded comment
- **Grateful** — thank the author (toggle)
- **Clip to vault** — save the whole post
- **Clip selection** — save highlighted text
- **Follow thread** — get updates in Knowledge hub
- **Hide** — remove from your feed
- **Report** — flag for moderator review (if not the author)

---

## 5. Profiles

### Public Profile

**Intent:** A living identity that showcases who you are and how you contribute — meant eventually to display Helper Style, XP, badges, and impact.

| Feature | Status | Detail |
|---------|--------|--------|
| View any profile | ✅ | `/profiles/<handle>/` |
| Display name, handle, bio, avatar | ✅ | |
| Mute / Block buttons | ✅ | On other users' profiles |
| Trust scores on profile | ❌ | Not displayed publicly |
| Helper Style badge | ❌ | Not displayed after onboarding |
| XP / badges / level | ❌ | Not on profile page |
| Profile visibility (public/guild/private) | ❌ | All profiles are always public |

### Edit Your Profile

**Intent:** Keep your public identity current.

| Field | Editable? |
|-------|-----------|
| Handle | ✅ |
| Display name | ✅ |
| Biography | ✅ |
| Profile image | ✅ |

**Route:** `/profiles/edit/` (sidebar footer link)

---

## 6. Interactions — Replies, Gratitude & Boundaries

### Replies

**Intent:** Threaded discussion with one level of nesting — constructive conversation without deep reply chains.

| Action | Route | Status |
|--------|-------|--------|
| Create reply | `/posts/<uuid>/replies/create/` | ✅ |
| Edit own reply | `/replies/<uuid>/edit/` | ✅ |
| Delete own reply | `/replies/<uuid>/delete/` | ✅ Soft delete |
| View replies | On post detail page | ✅ Nested one level |

Replies also trigger the **pre-send reflection prompt** (same as posts).

### Gratitude (Thank-Yous)

**Intent:** Express appreciation for helpful posts and replies — a prosocial alternative to generic "likes."

| Target | Route | Status | UI |
|--------|-------|--------|-----|
| Thank a **post** | `/posts/<uuid>/thank/` | ✅ | Toggle button with count on post detail |
| Thank a **reply** | `/replies/<uuid>/thank/` | ⚠️ Partial | Button exists but initial count/state is wrong until after first click |

> **Redundancy / not implemented:** A separate **ProsocialReaction** system (Constructive, Supportive, Insightful) exists in the database but has **no UI, routes, or services**. Users only see "Grateful" (thank-you), not the three reaction kinds.

### Boundaries — Hide, Mute, Block

**Intent:** Give you control over what and whom you see — without requiring moderator intervention.

| Action | Route | Status | How to access |
|--------|-------|--------|---------------|
| **Hide post** | `/posts/<uuid>/hide/` | ✅ | Button on post detail |
| **View hidden posts** | `/settings/hidden-posts/` | ✅ | **No nav link** — direct URL only |
| **Restore hidden post** | From hidden posts page | ✅ | |
| **Mute user** | `/profiles/<handle>/mute/` | ✅ | Button on their profile |
| **Unmute user** | `/profiles/<handle>/unmute/` | ✅ Backend | **No UI link** on profile |
| **Block user** | `/profiles/<handle>/block/` | ✅ | Button on their profile |
| **Unblock user** | `/profiles/<handle>/unblock/` | ✅ Backend | **No UI link** on profile |

Blocking prevents feed visibility and interactions. Muting hides their content from your feed.

### Reporting Content

**Intent:** Flag posts or replies for human moderator review — the AI flags but humans decide.

| Action | Route | Status |
|--------|-------|--------|
| Report post | `/posts/<uuid>/report/` | ✅ |
| Report reply | `/replies/<uuid>/report/` | ✅ |

Both show a form with category and explanation. Reports enter the moderation queue.

### Notifications

**Intent:** Keep you informed of community activity without guilt-based re-engagement.

| Action | Route | Status |
|--------|-------|--------|
| View notifications | `/notifications/` | ✅ |
| Mark one read | POST `/notifications/<id>/read/` | ✅ |
| Mark all read | POST `/notifications/read-all/` | ✅ |
| Unread badge | Left sidebar | ✅ |

**Notification kinds created in practice:** replies, thank-yous, action invitations, crisis reviews (moderators), commitment reminders.

**Not surfaced well:** Many notification kinds are defined (user followed, post followed, message received, XP earned, guild invite) but the list template shows only a text label — **no deep links** to the related content.

---

## 7. Knowledge — Clips, Vault & Collections

This is one of the platform's core differentiators: turning ephemeral conversation into lasting, reusable knowledge.

### Clipping (Saving Content)

**Intent:** Save a whole post, a specific passage, or (eventually) a whole thread into your personal Vault — with automatic source attribution and a small XP bonus for the original author when someone else clips their work.

| Clip type | Status | How |
|-----------|--------|-----|
| **Whole post** | ✅ | "Clip to vault" button on post detail → saves to Vault |
| **Text selection** | ✅ | Highlight text on post detail → "Clip selection" → saves quoted passage |
| **Whole reply** | ❌ Model only | No button or route |
| **Whole thread** | ❌ Model only | No button or route |
| **Private note on clip** | ❌ Model only | `private_note` displays in vault if set, but **no UI to add one** |

**After clipping a whole post:** you are redirected back to the post.
**After clipping a selection:** you are redirected to the Vault.

### Vault (Your Personal Library)

**Intent:** Browse everything you've clipped — your personal knowledge base.

| Feature | Route | Status |
|---------|-------|--------|
| Vault list | `/knowledge/vault/` | ✅ Paginated; shows quoted text, source link, private note if any |
| Link from Knowledge hub | `/dashboard/knowledge/` → Vault | ✅ |
| Link from sidebar | — | ❌ Sidebar "Knowledge" goes to hub, not vault directly |
| Link from right rail | — | ❌ Not present |
| Recent clips on Knowledge hub | — | ⚠️ **Data is fetched but not displayed** in the template |

> **This is the gap you noticed:** Clipping **does save** to the database and **is viewable** at `/knowledge/vault/`, but it does **not** appear in the right sidebar or as a "Recent clips" panel on the Knowledge hub (even though the backend loads `vault_recent` — the template simply doesn't render it).

### Collections

**Intent:** Organize clips, posts, and (eventually) external links into structured, shareable knowledge containers.

| Action | Route | Status |
|--------|-------|--------|
| List collections | `/knowledge/collections/` | ✅ |
| Create collection | `/knowledge/collections/new/` | ✅ Title, description, visibility (Private/Public/Guild) |
| View collection | `/knowledge/collections/<uuid>/` | ✅ Shows items |
| Edit collection | — | ❌ Not implemented |
| Delete collection | — | ❌ Not implemented |
| Add clip to collection | `/knowledge/collections/<uuid>/add-clip/<clip_id>/` | ⚠️ Backend only — **no UI to pick a clip** |
| Add post to collection | `/knowledge/collections/<uuid>/add-post/<post_id>/` | ⚠️ Backend only — **no UI** |
| Guild visibility enforcement | — | ❌ Guild collections behave like private for non-owners |

> **Redundancy:** Two ways to "save" a post exist:
> 1. **Clip** → `Clip` model → appears in **Vault** (has UI buttons)
> 2. **Add post to collection** → `CollectionItem` (backend endpoint only, no buttons)

### Tags

**Intent:** Categorize posts for browsing and discovery.

| Action | Route | Status |
|--------|-------|--------|
| Browse all tags | `/knowledge/tags/` | ✅ Shows tags with post counts |
| View tag detail | `/knowledge/tags/<slug>/` | ✅ Lists tagged posts |
| Assign tags to a post | — | ❌ Service exists but **no user UI** — tags only via admin/test data |

### Search

**Intent:** Find posts and tags by keyword.

| Route | Status | Nav link? |
|-------|--------|-----------|
| `/knowledge/search/` | ✅ Searches post body/title and tag names | ❌ No — direct URL only |

### Knowledge Hub

**Intent:** Your personal knowledge dashboard — activity from people you follow, your collections, followed threads, and links to vault/tags/helper style.

**Route:** `/dashboard/knowledge/`

| Panel | Status | What it shows |
|-------|--------|---------------|
| Quick links | ✅ | Vault, Collections, Tags, Helper style |
| Activity from people you follow | ✅ | Recent **posts** (not clips) from followed users |
| My collections | ✅ | Up to 5 collection titles |
| Followed threads | ✅ | Posts you've followed |
| Recent vault clips | ❌ | **Backend loads data; template does not render it** |
| Active challenges | ⚠️ Placeholder | *"Coming soon to this panel"* with link to challenges page |
| Streak tracker | ✅ | Link to gamification progress page |

---

## 8. Prosocial Actions

**Intent:** Turn goodwill into concrete action — help requests, offers, local initiatives, and volunteer shifts with a full commitment and verification lifecycle.

This is one of the most complete feature areas in the platform.

### Action Opportunities

| Kind | Status | Created via |
|------|--------|-------------|
| Help request | ✅ | `/actions/create/` |
| Help offer | ✅ | `/actions/create/` |
| Encouragement request | ✅ | `/actions/create/` |
| Local action | ✅ | `/actions/create/` |
| Volunteer opportunity | ✅ | `/actions/create/` |

| Action | Route | Status |
|--------|-------|--------|
| Browse all actions | `/actions/` | ✅ |
| Create action | `/actions/create/` | ✅ |
| View action detail | `/actions/<uuid>/` | ✅ |
| Save action | POST on detail page | ✅ |
| Commit to action | `/actions/<uuid>/commit/` | ✅ |

### Commitments

**Intent:** Track your promise to help — with status progression and optional verification.

| Status flow | Detail |
|-------------|--------|
| Committed → In progress → Completed | ✅ |
| Withdraw | ✅ |

| Action | Route | Status |
|--------|-------|--------|
| List your commitments | `/actions/commitments/` | ✅ Also shown in right rail |
| View commitment | `/actions/commitments/<uuid>/` | ✅ |
| Complete commitment | `/actions/commitments/<uuid>/complete/` | ✅ |
| Acknowledge someone's help | `/actions/commitments/<uuid>/acknowledge/` | ⚠️ Backend works; **no link** on commitment detail page |

### Verification

**Intent:** Action creators confirm that commitments were fulfilled — building trust through verified help.

| Action | Route | Status |
|--------|-------|--------|
| Verification queue (creator) | `/actions/verification/` | ✅ Pending items with verify/reject |
| Review verification | `/actions/verification/<uuid>/` | ✅ |

### Invitations

**Intent:** Invite specific people to join an action opportunity.

| Action | Route | Status |
|--------|-------|--------|
| Send invitation | From action detail | ✅ |
| View invitations | `/actions/invitations/` | ✅ Accept/decline |
| Right rail panel | — | ✅ Shows pending invitations |

### Reminders

**Intent:** Nudge you about upcoming commitment deadlines.

| Feature | Status |
|---------|--------|
| In-app notifications | ✅ Created by management command |
| Email reminders | ❌ Not implemented |

---

## 9. Following People & Threads

**Intent:** Curate whose content you see and which threads you want to track — without requiring mutual "friend" connections.

### Follow Users

| Action | Route | Status | UI |
|--------|-------|--------|-----|
| Follow / unfollow user | `/follows/follow/user/<handle>/` | ✅ Backend toggle | ❌ **No follow button** on profile pages |
| Followed users' posts in feed | `/dashboard/?feed=following` | ✅ | Feed filter chip |
| Followed users' posts in Knowledge hub | `/dashboard/knowledge/` | ✅ | Activity panel |

### Follow Threads (Posts)

| Action | Route | Status | UI |
|--------|-------|--------|-----|
| Follow / unfollow thread | `/follows/follow/post/<uuid>/` | ✅ | ✅ Button on post detail |
| Followed threads list | `/dashboard/knowledge/` | ✅ | "Followed threads" panel |

### Followers / Following Lists

| Feature | Status |
|---------|--------|
| View who follows you | ❌ No page |
| View who you follow | ❌ No page |
| Data in export | ✅ Included in data export JSON |

---

## 10. Guilds

**Intent:** Community groups around shared causes, interests, or Helper Styles — with collective identity and internal feeds.

| Action | Route | Status |
|--------|-------|--------|
| List guilds | `/guilds/` | ✅ |
| Create guild | `/guilds/new/` | ✅ Creator becomes leader |
| View guild | `/guilds/<slug>/` | ✅ Name, description, guild feed |
| Join guild | `/guilds/<slug>/join/` | ✅ |
| Leave guild | `/guilds/<slug>/leave/` | ✅ Leader transfer or guild deletion |
| Manage member roles | — | ❌ Leader/Member exist in backend; no UI to change roles |
| Guild XP / collective progress | — | ❌ Not implemented |
| Guild missions | — | ❌ Model exists; admin only |
| Guild-shared collections | — | ❌ Visibility flag exists but not enforced |

---

## 11. Messaging

**Intent:** Private 1:1 channels for coordinating help, offering support, and building relationships.

| Action | Route | Status |
|--------|-------|--------|
| Conversation list | `/messages/` | ✅ Minimal — shows "Conversation" or empty state |
| View / send messages | `/messages/<uuid>/` | ✅ Marks messages read on open |
| Start conversation | `/messages/start/<handle>/` | ✅ Creates ordered pair; blocked if either user blocked the other |
| Unread badge | Left sidebar | ✅ |

| Feature | Status |
|---------|--------|
| 1:1 messaging | ✅ |
| Group chats | ❌ Model supports exactly two participants |
| Voice / video | ❌ Not implemented |

---

## 12. Discovery

**Intent:** Surface the community's most valuable content — elevated by clipping and positive sentiment, not raw engagement.

| Feature | Route | Status | Detail |
|---------|-------|--------|--------|
| Discovery home | `/discovery/` | ⚠️ Partial | |
| Most clipped posts | On discovery home | ✅ | Real clip-count ranking |
| Sentiment-boosted posts | On discovery home | ⚠️ | Query works but usually **empty** — sentiment snapshots are not created on post/reply |
| Ripple effect | `/discovery/ripple/` | ⚠️ Display only | Shows "You helped" / "You were helped by" — data must be admin-seeded |
| Community spotlights | — | ❌ | Loaded in view but **not rendered** in template |
| Prosocial ranked feed | — | ❌ | Selector exists; no URL or UI |
| Trending | — | ❌ | Does not exist |
| Semantic search | — | ❌ | Basic keyword search is in Knowledge app |

---

## 13. Trust & Helper Style

**Intent:** Multi-dimensional trust that separates *quality of participation* (ETS) from *social validation* (PTS) — so popularity alone can never buy influence.

### Helper Style Onboarding

**Intent:** A short preference signal (not a personality test) that personalizes challenges and XP opportunities.

| Style | Focus |
|-------|-------|
| Empathizer | Emotional support, active listening |
| Sage | Knowledge sharing, tutorials |
| Builder | Collaborative projects |
| Guide | Mentorship, onboarding |
| Connector | Bridging people, introductions |

| Action | Route | Status |
|--------|-------|--------|
| Choose helper style | `/trust/onboarding/` | ✅ One-time onboarding form |
| Change helper style | — | ❌ No re-selection UI after onboarding |
| Display on profile | — | ❌ Not shown anywhere after onboarding |

### Trust Scores

**Intent:** A composite Contribution Score (65% ETS + 35% PTS) that drives role eligibility and feed visibility — shown only when you opt in.

| Feature | Route | Status |
|---------|-------|--------|
| View your scores (private) | `/trust/settings/` | ✅ Shows exact ETS, PTS, contribution, range label |
| Control score visibility | `/trust/settings/` | ⚠️ Setting saved but **never enforced** on any public surface |
| Scores on public profile | — | ❌ Not displayed |
| Right rail trust badges | — | ❌ **Hardcoded** static badges, not real data |

### Peer Ratings

**Intent:** Let community members rate the helpfulness, empathy, and constructiveness of posts and replies.

| Action | Route | Status |
|--------|-------|--------|
| Rate a post | `/trust/rate/post/<uuid>/` | ❌ Backend only — **no rating UI** on post detail |
| Rate a reply | `/trust/rate/reply/<uuid>/` | ❌ Backend only — **no rating UI** on replies |
| Negative rating dimensions | — | ❌ Model supports them; form excludes them |

### Trust Events

Scores are recalculated from trust events. In practice, only **peer ratings** and **clips by others** create events. Thank-yous, commitment verifications, and moderation actions do **not** yet generate trust events despite being defined.

**Management command:** `python manage.py recalculate_trust_scores` recalculates all users.

---

## 14. Gamification — XP, Streaks & Badges

**Intent:** Make prosocial behavior feel good in the moment and visible over time — without manufacturing addiction.

### What Earns XP Today

| Action | XP Source | Status |
|--------|-----------|--------|
| Someone clips your content | KNOWLEDGE_SHARED | ✅ Automatic |
| Write a reflection journal entry | REFLECTION | ✅ Automatic |
| Complete a daily challenge | DAILY_CHALLENGE | ✅ Honor-system click |
| Direct support, commitments, welcoming, guild missions, etc. | Various | ❌ Defined in model but **not wired** to real actions |

### Progress Page

**Intent:** Your private view of level, XP, streak, multiplier, badges, and recent transactions.

| Feature | Route | Status |
|---------|-------|--------|
| View progress | `/gamification/progress/` | ✅ |
| Nav link | — | ❌ Only linked from Knowledge hub "Streak tracker" |

**What the page shows:** Level, total XP, streak days, multiplier, earned badges, last 20 XP transactions.

### Badges & Achievements

| Feature | Status |
|---------|--------|
| Badges (auto-awarded at XP thresholds) | ⚠️ Works if `BadgeDefinition` rows exist in admin |
| Achievements | ❌ Model exists; `record_achievement()` never called |
| Skill trees | ❌ Not implemented |
| Level titles (Helper Initiate → Legendary Steward) | ❌ Levels calculated but titles not displayed |
| XP celebration animations | ❌ Not implemented |

### Streaks & Multipliers

| Feature | Status |
|---------|--------|
| Streak tracking | ✅ Days counted in progress page |
| Multiplier display | ✅ Shown on progress page |
| Grace rest day | ❌ Not implemented |

---

## 15. AI Coach — Reflection & Pre-Send Prompts

**Intent:** An AI layer that encourages, suggests, and celebrates — never enforces. (Principle: Coach, Not Cop.)

> **Important:** There is **no live LLM integration**. All "AI" features use keyword matching (`model_version: "keyword-v1"`).

### Pre-Send Reflection Prompt

**Intent:** Gentle friction before potentially harmful posts — preserves your agency while inviting reflection.

| Feature | Status | What you see |
|---------|--------|--------------|
| Post composer check | ✅ | If negative keywords detected: *"Before you post — does this say what you mean?"* |
| Reply form check | ✅ | Same prompt on reply forms |
| Dismissible | ✅ | Prompt appears inline; you can still post |

**Route:** `/ai/pre-send-check/` (HTMX partial, not a standalone page)

### Reflection Journal

**Intent:** A private space for short entries after significant events — reflection turns prosocial behavior into habit.

| Action | Route | Status |
|--------|-------|--------|
| List entries | `/ai/journal/` | ✅ |
| Create entry | `/ai/journal/new/` | ✅ |
| AI response | — | ⚠️ **Static hardcoded text**, not LLM-generated |
| Nav link | — | ❌ No sidebar link — direct URL only |
| XP reward | ✅ | Awards REFLECTION XP on create |

### Not Available

| Feature | Status |
|---------|--------|
| Sentiment analysis on posts/replies | ❌ `score_content()` exists but is never called on create |
| Thread summaries | ❌ Service exists; never called |
| Behavioral forecasting | ❌ Not implemented |
| Personalized challenges from AI | ❌ Not implemented |
| Ripple effect visualization | ❌ Display-only page exists; no auto-creation |
| AI interventions log | ❌ Model exists; never used |

---

## 16. Engagement — Challenges & Rest Mode

**Intent:** Short- and medium-term goals that sustain prosocial habits — with built-in burnout protection.

### Challenges

| Action | Route | Status |
|--------|-------|--------|
| View challenges | `/engagement/challenges/` | ✅ |
| Complete challenge | `/engagement/challenges/<id>/complete/` | ✅ Honor-system (click "Complete") |
| Challenge verification | — | ❌ No action verification |
| Completion status in list | — | ❌ Not shown in template |
| Helper-style filtering | — | ❌ Model field exists; never used |

> Challenges must be created by administrators. The Knowledge hub says *"Active challenges — coming soon to this panel."*

### Rest Mode

**Intent:** Pause streaks, mute notifications, and reduce pressure when you need a break.

| Action | Route | Status |
|--------|-------|--------|
| Toggle rest mode | `/engagement/rest-mode/` | ⚠️ Creates/ends session in database |
| Effect on notifications | — | ❌ `mute_notifications` field never read |
| Effect on streaks | — | ❌ No pause behavior |
| UI indicator | — | ❌ No visible "resting" state |

### Re-Engagement Messages

**Intent:** Warm, no-pressure invitations to return — never guilt or streak-shaming.

| Feature | Status |
|---------|--------|
| Re-engagement messages | ❌ Model exists; no cron, views, or emails |

---

## 17. Moderation & Safety

**Intent:** Human-reviewed content moderation with AI-assisted flagging, crisis-first protocols, and transparency.

### Reporting (User Side)

See [Reporting Content](#reporting-content) in Interactions.

### Crisis Protocol

**Intent:** Treat distress as a care situation, never an enforcement situation.

| Step | Status |
|------|--------|
| Keyword detection on post/reply create | ✅ |
| Crisis flag created | ✅ |
| Moderator notifications (up to 5) | ✅ |
| Crisis resources shown to poster | ❌ Flag set `resources_shown=True` but **no UI displays resources** |

### Moderator Tools

**Intent:** Human moderators review flagged content and make binding decisions.

| Action | Route | Status | Access |
|--------|-------|--------|--------|
| Moderation queue | `/moderation/queue/` | ✅ | MODERATOR, COMMUNITY_GUIDE, or COMMUNITY_LEADER role |
| Review item | `/moderation/review/<id>/` | ⚠️ Partial | Shows status dropdown + explanation — **does not show reported content** |
| Nav link | — | ❌ Must know URL |
| Crisis flag review | — | ❌ No UI |
| Transparency log | — | ❌ Written on review; admin only |
| Role assignment | — | ❌ Admin only; auto-assignment from trust scores |

### Platform Roles

Roles are earned through trust scores (ETS gates first, always). Auto-assignment runs on trust recalculation but roles are **not displayed** anywhere in the user-facing UI.

| Role | ETS threshold | Contribution threshold |
|------|--------------|----------------------|
| Member | > 40 | > 30 |
| Community Supporter | > 60 | > 50 |
| Mentor | > 75 | > 70 |
| Community Guide | > 80 | > 75 |
| Ambassador | > 85 | > 80 |
| Moderator | > 85 | > 80 |
| Community Leader | > 90 | > 90 |

---

## 18. Advanced — Donations, Skills & Data Export

### Donations

**Intent:** Embed philanthropy in the social experience — supporting verified causes without leaving the platform.

| Action | Route | Status |
|--------|-------|--------|
| Browse campaigns | `/advanced/donations/` | ⚠️ Only **verified** campaigns shown |
| Create campaign | `/advanced/donations/new/` | ✅ |
| Donate | `/advanced/donations/<uuid>/` | ⚠️ **Stub** — records donation as COMPLETED with calculated fee; **no payment processor** |
| Campaign verification | — | ❌ Admin only; new campaigns default to unverified (invisible in list) |

### Skill Sharing

**Intent:** Offer and discover skills — building community resilience through mutual aid.

| Action | Route | Status |
|--------|-------|--------|
| Browse offerings | `/advanced/skills/` | ✅ |
| Create offering | `/advanced/skills/new/` | ✅ |
| Workshops | — | ❌ Model exists; no routes or UI |
| Skill forums / mentorship matching | — | ❌ Not implemented |

### Data Export

**Intent:** Full data portability — export your profile, posts, clips, journal, XP, trust, messages, and more anytime.

| Action | Route | Status |
|--------|-------|--------|
| Export data | `/advanced/export/` | ✅ Immediate JSON download |
| Rate limited | ✅ | |
| Includes | Account, profile, posts, replies, clips, collections, journal, XP, trust, messages, commitments, follows, boundaries, notifications, donations, skills, guilds | |

---

## 19. Account Settings & Privacy

### Account Deletion

**Intent:** Leave the platform cleanly — with a grace period to change your mind.

| Action | Route | Status |
|--------|-------|--------|
| Request deletion | `/accounts/delete/` | ✅ Schedules deletion (not immediate) |
| Cancel deletion | `/accounts/delete/cancel/` | ✅ During grace period |
| Process deletions | Management command | ✅ `process_scheduled_deletions` |

Deletion soft-deletes posts and replies; related data cascades.

### Privacy Controls

| Feature | Design intent | Current status |
|---------|--------------|----------------|
| Profile visibility (public/guild/private) | User choice | ❌ All profiles public |
| Contribution score visibility | Hide exact / show range | ⚠️ Setting saved; not enforced publicly |
| Reflection journal | Always private | ✅ No sharing UI |
| Ripple effect display | User can disable | ❌ Not implemented |
| Anonymous posting (Support Circles) | Opt-in per thread | ❌ Not implemented |
| AI personalization opt-out | User control | ❌ Not implemented |
| Data export | Anytime | ✅ |
| Account deletion | Within grace period | ✅ |

---

## 20. Feature Status Summary

### ✅ Fully Working (End-to-End)

- Registration, login, logout, password change/reset
- Dashboard feed with pagination, following mode, kind filters
- Post create (text/image), view, edit, delete
- Replies (create, edit, delete, one-level nesting)
- Thank post (toggle with count)
- Hide post + hidden posts restore
- Mute/block from profile
- Report post/reply
- Notifications list + mark read + sidebar badge
- Clip whole post + clip text selection → vault
- Vault browse
- Collection create, list, detail
- Tag browse and detail (when tags exist)
- Knowledge search (by URL)
- Prosocial actions (full lifecycle: create, commit, complete, verify, invite)
- Guild create, join, leave, guild feed
- 1:1 messaging with unread badge
- Helper style onboarding
- Trust settings (private score view)
- Gamification progress page
- AI pre-send reflection prompts
- Reflection journal (with static AI response)
- Challenge list + honor-system completion
- Discovery home (most clipped)
- Data export (JSON)
- Account deletion with grace period

### ⚠️ Partially Implemented

| Feature | What works | What's missing |
|---------|-----------|----------------|
| **Clipping → surfacing** | Saves to DB; viewable at `/knowledge/vault/` | Not in right rail; not on Knowledge hub panel |
| **Post kinds** | Filterable on feed; set via Actions app | Not choosable in post composer |
| **Thank reply** | Toggle works on click | Wrong initial count/state in UI |
| **Collections** | Create, list, view | No edit/delete; no "add to collection" buttons |
| **Follow users** | Backend toggle; feed filter | No follow button on profiles; no followers list |
| **Trust scores** | Calculated; visible in settings | Not on profile; visibility setting ignored; right rail badges hardcoded |
| **Peer ratings** | Backend creates ratings + events | No rating UI anywhere |
| **Gamification XP** | Engine works; 3 triggers wired | Most XP sources unwired; badges need admin seeding |
| **AI coach** | Pre-send prompts; journal | Keyword-only (no LLM); sentiment not run on posts |
| **Rest mode** | Session created/ended | No effect on notifications or streaks |
| **Moderation review** | Queue + approve/remove | Review screen doesn't show reported content |
| **Donations** | Campaign create; stub donate | No payment processor; campaigns need admin verification |
| **Discovery** | Most clipped works | Sentiment-boosted empty; ripple/spotlights need seeding |
| **Crisis protocol** | Detection + moderator alert | No crisis resources shown to user |
| **Notifications** | List + mark read | No deep links to related content |

### ❌ Not Implemented (Model/Scaffold Only)

| Feature | Evidence |
|---------|----------|
| ProsocialReaction (Constructive/Supportive/Insightful) | Model + migration; zero UI |
| MFA | No code |
| Profile visibility controls | No model field |
| Group messaging | Two-participant model only |
| Guild XP / missions / role management UI | Models/admin only |
| Thread/reply clipping | Service validation only |
| Clip private notes UI | Model + form; no view |
| Tag assignment on posts | Service only |
| Collection edit/delete | No routes |
| Achievements | `record_achievement()` never called |
| Skill trees, level titles, XP animations | Not built |
| Re-engagement messages | Model only |
| Semantic search | Not built |
| Trending | Does not exist |
| Live collaboration rooms | Scaffolded for future |
| Workshops | Model only |
| Anonymous posting (Support Circles) | Not built |
| Ripple effect auto-creation | Display only |
| Thread summaries | Dead code |
| AI interventions | Model never used |
| Workshops | Model only |

---

## 21. Known Gaps & Redundancies

### Redundancies (Two Systems for One Purpose)

| Area | System A (Active) | System B (Dormant) | Recommendation |
|------|-------------------|--------------------|----|
| **Post creation** | Dashboard composer modal | `/posts/create/` standalone page | Consolidate to dashboard; remove or link standalone |
| **Reactions** | ThankYou ("Grateful") — full UI | ProsocialReaction (Constructive/Supportive/Insightful) — model only | Implement B or remove model |
| **Saving content** | Clip → Vault (has buttons) | Add post to collection (backend only) | Add collection UI or remove endpoint |
| **Navigation** | `shell_left.html` (active) | `navigation.html` (unused) | Remove dead template |
| **Trust display** | Real scores in `/trust/settings/` | Hardcoded badges in right rail | Wire rail to real data or remove badges |
| **Post kinds** | Dashboard feed filter | Actions app creation flow | Document that kinds come from Actions, not composer |

### Critical UX Gaps (Features That Work But Are Hard to Find)

| Feature | Works? | How to reach it | Should be in |
|---------|--------|-----------------|--------------|
| Vault (saved clips) | ✅ | Knowledge hub → Vault link, or `/knowledge/vault/` | Right rail + Knowledge hub "Recent clips" panel |
| Hidden posts | ✅ | `/settings/hidden-posts/` only | Settings or profile menu |
| Search | ✅ | `/knowledge/search/` only | Sidebar or Knowledge hub |
| Gamification progress | ✅ | Knowledge hub → Streak tracker | Sidebar or profile |
| Reflection journal | ✅ | `/ai/journal/` only | Sidebar or profile |
| Challenges | ✅ | `/engagement/challenges/` only | Knowledge hub (currently "coming soon") |
| Unmute / unblock | ✅ backend | No UI link after mute/block | Profile page when already muted/blocked |
| Follow user | ✅ backend | No button on profiles | Profile page |
| Peer ratings | ✅ backend | No UI at all | Post/reply detail pages |
| Acknowledge help | ✅ backend | No link on commitment detail | Commitment detail page |
| Moderation queue | ✅ | `/moderation/queue/` only | Moderator nav (when role assigned) |

### Data Fetched But Not Displayed

| View | Data loaded | Template renders it? |
|------|-------------|---------------------|
| Knowledge hub | `vault_recent` (5 clips) | ❌ No |
| Discovery home | `spotlights`, `ranked_page` | ❌ No |
| Thank reply button | `thank_count`, `thanked` | ❌ Wrong initial state |

---

## Quick Reference — All Routes

| Area | Route | Name |
|------|-------|------|
| Health | `/health/` | `health` |
| Register | `/accounts/register/` | `accounts:register` |
| Login | `/accounts/login/` | `accounts:login` |
| Home feed | `/dashboard/` | `dashboard:index` |
| Knowledge hub | `/dashboard/knowledge/` | `dashboard:knowledge` |
| Create post | `/posts/create/` | `posts:create` |
| Post detail | `/posts/<uuid>/` | `posts:detail` |
| Profile | `/profiles/<handle>/` | `profiles:detail` |
| Edit profile | `/profiles/edit/` | `profiles:edit` |
| Vault | `/knowledge/vault/` | `knowledge:vault` |
| Collections | `/knowledge/collections/` | `knowledge:collection_list` |
| Tags | `/knowledge/tags/` | `knowledge:tag_browse` |
| Search | `/knowledge/search/` | `knowledge:search` |
| Actions | `/actions/` | `prosocial_actions:action_list` |
| Commitments | `/actions/commitments/` | `prosocial_actions:commitment_list` |
| Invitations | `/actions/invitations/` | `prosocial_actions:invitations` |
| Guilds | `/guilds/` | `guilds:list` |
| Messages | `/messages/` | `messaging:list` |
| Discover | `/discovery/` | `discovery:home` |
| Notifications | `/notifications/` | `interactions:notifications` |
| Hidden posts | `/settings/hidden-posts/` | `interactions:hidden_posts` |
| Trust settings | `/trust/settings/` | `trust:settings` |
| Helper style | `/trust/onboarding/` | `trust:onboarding` |
| XP progress | `/gamification/progress/` | `gamification:progress` |
| Journal | `/ai/journal/` | `ai_coach:journal_list` |
| Challenges | `/engagement/challenges/` | `engagement:challenges` |
| Moderation queue | `/moderation/queue/` | `moderation:queue` |
| Donations | `/advanced/donations/` | `advanced:donation_list` |
| Skills | `/advanced/skills/` | `advanced:skill_list` |
| Data export | `/advanced/export/` | `advanced:data_export` |
| Delete account | `/accounts/delete/` | `accounts:account_delete` |

---

*This guide reflects the codebase as of July 2026. Features marked ❌ or ⚠️ may be completed in future phases — see `ProsocialNetworkDesign.md` for the full product vision.*
