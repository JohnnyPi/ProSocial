# Common Good — Application Summary

*A concise overview of the Prosocial Platform: what it is, why it exists, how it works, and how each part of the system is designed to cultivate prosocial behavior.*

**Last updated:** July 2026 · **Implementation:** Phases 0–12 (Functional Trust)

---

## What This Application Is

**Common Good** is a prosocial social network — a Django web application built to reward helpfulness, cooperation, and genuine community contribution rather than raw popularity or time-on-site. Where conventional social media optimizes for engagement (often at the cost of division and shallow interaction), Common Good deliberately cultivates empathy, mutual support, and altruism.

The platform is branded internally as the **Prosocial Platform** and implemented as a modular monolith: accounts, profiles, posts, and a paginated feed form the social core; specialized apps layer on interactions, knowledge preservation, coordinated action, trust, gamification, AI-assisted reflection, moderation, and discovery. The interface uses server-rendered templates with HTMX for responsive, low-friction interactions.

---

## Intended Purpose

### The problem it addresses

Mainstream social networks tend to amplify what spreads fastest — outrage, novelty, and performative conflict — while burying slow, thoughtful help. Good answers disappear in the feed. Harmful posts go up without pause. Influence follows follower counts, not demonstrated care. Common Good exists to invert those incentives.

### The north star

**Growth in prosocial skill — not daily active time — is the metric of success.** The platform asks whether people are becoming *better* community members, not merely more addicted ones. Every design choice — feed weighting, reaction types, badge logic, notification copy, even the “you’re caught up” feed endpoint — is judged against that mission.

### Who it serves

- People who want to give back to an online community in meaningful ways
- Learners seeking curated, durable knowledge from peers
- Professionals who want to mentor without formal program overhead
- Communities organized around causes, hobbies, or emotional support
- Anyone burned out by extractive, dopamine-optimized social media

---

## How It Means to Achieve That Purpose

Common Good does not rely on a single feature or algorithm. It uses a **coherent stack of reinforcing mechanisms**, each aligned with one of seven core principles:

| Principle | What it means in practice |
|-----------|---------------------------|
| **Prosocial over popularity** | Deeply helpful replies outweigh hundreds of shallow likes. Discovery ranks by clipping and constructive signals, not raw engagement. |
| **Visibility as responsibility** | Prominence is earned through sustained prosocial behavior and quality trust scores — not tenure or follower count alone. |
| **Gentle friction before harm** | A soft reflection prompt may appear before hostile posts or replies. Users can edit, post anyway, or cancel — never a silent block. |
| **Earn your privacy upgrades** | Higher-trust capabilities (context notes, moderation tools, official role claims) unlock through demonstrated constructive participation. |
| **Knowledge outlasts conversation** | Clipping, collections, and vault turn ephemeral threads into reusable knowledge artifacts. |
| **Growth is the metric** | XP, trust, and badges reward skill development and verified help — not addiction loops or infinite scroll. |
| **AI as coach, not cop** | Automated suggestions encourage and explain; humans make every binding moderation decision. |

### The trust architecture (internal, not a public score)

Influence is governed by **multi-dimensional trust**, deliberately separated so popularity alone cannot buy power:

- **Engagement Trust Score (ETS)** — quality of participation: constructive replies, prosocial reactions received, reflection consistency, moderation behavior, crisis-support contributions.
- **Popularity Trust Score (PTS)** — social validation filtered for authenticity: followers, content clipped into others’ collections, peer endorsements.
- **Contribution Score** — composite (65% ETS + 35% PTS) used internally for role eligibility and privileges. **ETS must clear thresholds first**; a popular user with poor conduct is coached, not promoted.
- **Domain reputation** — separate channels (support, clarity, knowledge, civility, concern) fed by typed prosocial reactions, so expertise in gardening does not automatically grant authority in politics or crisis support.

**Functional Trust** (Phase 12) adds layered account assurance, earned privileges, community context notes with cross-perspective validation, transparent moderation with appeals, and anti-gaming safeguards — all **without** exposing a single public social-credit number. Users see scoped badges and reaction category totals; exact scores remain private unless opted in.

### The behavioral loop

At a high level, the platform creates a virtuous cycle:

1. **Contribute** — post, reply, offer help, join actions, clip valuable content.
2. **Signal quality** — peers respond with prosocial reactions (Helpful, Kind, Clarified, etc.) rather than generic likes.
3. **Earn trust & privileges** — domain reputation and composite scores unlock practical abilities (tagging, context notes, triage flags).
4. **Take responsibility** — trusted members add corrective context, moderate, and model constructive norms.
5. **Preserve knowledge** — good work is clipped, collected, and surfaced in discovery — rewarding authors and benefiting future readers.
6. **Reflect & improve** — pre-send prompts and a private reflection journal turn one-off acts into habits.

Gamification (XP, streaks, badges) and Helper Style onboarding personalize this loop without replacing intrinsic motivation with empty points-chasing.

---

## Areas of Functionality and Their Prosocial Role

The application is organized into focused modules. Below, each area is described by **what it does** and **how it contributes to prosocial behavior**.

### 1. Accounts & Profiles — Identity with integrity

**What it does:** Registration, authentication, password management, and public profiles (bio, avatar, handle). Users can add **scoped role badges** (self-asserted claims with explicit verification method) and manage boundaries (mute, block).

**Prosocial contribution:** Profiles are *living identities* meant to showcase how someone helps, not just who they follow. Scoped endorsements verify specific claims (“affiliated with X organization”) without forcing full real-name exposure. Boundaries give individuals control over their experience without requiring moderator intervention for every conflict.

---

### 2. Home Feed & Posting — Conversation without infinite trap

**What it does:** A paginated dashboard feed with “All” and “Following” modes, optional kind filters (help requests, offers, local actions), and a post composer supporting text and images for **general discussion posts** (action kinds such as help requests are created through the Actions module). Posts can be viewed, edited (with civility prompts), and soft-deleted. The feed ends with a natural “you’re caught up” message rather than endless scroll.

**Prosocial contribution:** The feed is the town square — but it is weighted toward constructive content and designed to respect attention. Kind-specific filters surface *actionable* posts (requests for help, local initiatives) alongside general discussion, making it easy to find opportunities to contribute rather than only consume.

---

### 3. Interactions — Replies, gratitude, reactions, and context

**What it does:** Threaded replies (one level of nesting), a **prosocial reaction system** (Helpful, Kind, Clarified, Supportive, Good faith, Needs context, Thanks — including gratitude via the Thanks reaction), **community context notes** (corrective/clarifying annotations that appear only after cross-perspective support), hide/mute/block, content reporting, and notifications.

**Prosocial contribution:** This is the primary replacement for the “like economy.” Reactions encode *what kind* of good someone did — practical help, emotional warmth, clarity, gratitude — feeding domain-specific reputation instead of one popularity number.

---

### 4. Knowledge — Clips, Vault & Collections

**What it does:** Users clip whole posts or highlighted passages into a personal **Vault**, organize material into **Collections** (private, public, or guild-scoped), browse **Tags**, and search by keyword. The **Knowledge hub** aggregates followed-thread activity, collections, and links to vault and progress tools. Clipping someone else’s content awards XP to the original author.

**Prosocial contribution:** Implements the principle that **knowledge outlasts conversation**. A thoughtful reply that would vanish in a conventional feed becomes a citable artifact. Discovery surfaces “most clipped” content, so durable value — not viral outrage — earns visibility. This rewards authors who write for reuse and gives learners a curated path through community wisdom.

---

### 5. Prosocial Actions — Goodwill made concrete

**What it does:** A full lifecycle for help requests, help offers, encouragement requests, local actions, and volunteer opportunities: create, browse, save, commit, complete, verify, invite, and acknowledge. Commitments track status; creators verify fulfillment; invitations and reminders keep participants accountable.

**Prosocial contribution:** This is the platform’s clearest differentiator from “discussion only” networks. Intent to help becomes tracked commitment. Verification builds **trust through verified action**, not self-reported virtue. The right rail surfaces open opportunities near you and your active commitments — lowering the gap between seeing a need and doing something about it.

---

### 6. Following, Guilds & Messaging — Community structure

**What it does:** Follow users (feed filter) and threads (Knowledge hub tracking). **Guilds** are community groups around shared causes or interests with their own feeds and membership. **Messaging** provides private 1:1 conversations with unread badges.

**Prosocial contribution:** Following lets inspiring helpers and important threads reach people without requiring mutual “friend” connections — amplifying positive role models. Guilds create bounded communities where norms and missions align (local action, knowledge sharing, support). Direct messaging enables coordination for help offers, mentorship, and sensitive support that does not belong in public threads.

---

### 7. Discovery — Valuable content, not viral noise

**What it does:** Surfaces community content elevated by clipping counts and (when populated) positive sentiment signals. Includes a ripple-effect view of help given and received.

**Prosocial contribution:** Discovery answers “what’s worth my attention?” with **community-curated quality** rather than engagement bait. Most-clipped ranking is a collective vote for lasting usefulness. The design explicitly avoids a “trending outrage” feed.

---

### 8. Trust & Helper Style — Earned influence

**What it does:** One-time **Helper Style** onboarding (Empathizer, Sage, Builder, Guide, Connector) personalizes challenges. Private trust settings show ETS, PTS, contribution score, and domain reputation. **Earned privileges** (`can_tag_posts`, `can_submit_context_notes`, `can_flag_high_priority`) unlock from reputation thresholds and are enforced in the composer and reporting flows. **Assurance profiles** gate high-risk capabilities (payments, official roles) through progressive verification. Anti-gaming down-weights coordinated rating from tight trust clusters.

**Prosocial contribution:** Separates *quality* from *popularity* so loud or controversial users cannot buy influence. Domain-specific reputation ensures authority matches demonstrated skill in that area. Privileges reward constructive participation with **practical abilities**, not vanity badges — tagging, note review, and small-group moderation are responsibilities earned through trust.

---

### 9. Gamification — Motivation without addiction

**What it does:** XP for actions like being clipped, journal entries, and challenge completion; levels, streaks, multipliers, and badges on a private progress page.

**Prosocial contribution:** Game mechanics pass one test: *Does this reward behavior we actually want?* Highest-value acts (crisis support, deep guidance, knowledge clipped repeatedly) are designed to earn the most XP. Streaks encourage consistency; rest mode (when fully wired) will protect against burnout. The system makes prosocial acts **feel good in the moment and visible over time** without optimizing for time-on-site.

---

### 10. AI Coach — Reflection, not enforcement

**What it does:** **Pre-send civility prompts** on posts and replies when keyword heuristics detect hostile language — user chooses Edit, Post anyway, or Cancel; outcomes are logged for moderation analytics. A private **reflection journal** with XP reward. (Current implementation uses keyword matching, not a live LLM.)

**Prosocial contribution:** Embodies **gentle friction before harm** and **AI as coach, not cop**. Prompts invite revision without blocking agency; if the user posts anyway, the event informs human moderators. The journal turns episodic kindness into reflective habit. Future sentiment analysis and summaries are scaffolded to support ranking and coaching — not automated punishment.

---

### 11. Engagement — Challenges & rest

**What it does:** Administrator-defined **challenges** with honor-system completion; **rest mode** sessions to pause pressure (partially implemented).

**Prosocial contribution:** Short-term goals sustain prosocial habits aligned with Helper Style. Rest mode acknowledges that sustainable helping requires breaks — streaks and notifications should yield to well-being, not shame users into constant activity.

---

### 12. Moderation & Safety — Human judgment, transparent process

**What it does:** User reporting, moderator queue, explainable **moderation actions** with notifications, **14-day appeals** that restore content and trust on approval, crisis keyword detection with moderator alerts, and moderation history showing earned privileges.

**Prosocial contribution:** Safety enables prosocial risk-taking — people share vulnerably when harm is addressed fairly. Crisis protocol treats distress as care, not enforcement. Transparent notices (“what rule, why, how to appeal”) make moderation contestable and auditable. Civility-prompt and report context ensure moderators see the full story. Roles (Member through Community Leader) auto-assign from trust scores with ETS gates first.

---

### 13. Advanced — Donations, skills & data portability

**What it does:** Donation campaigns (stub payment flow), skill offerings browse/create, and full **JSON data export** (profile, posts, clips, trust, messages, commitments, and more).

**Prosocial contribution:** Donations and skill-sharing extend help beyond the feed into philanthropy and mutual aid. Data export respects user autonomy — portability is a trust signal that the platform serves members, not captive audiences.

---

## How the Pieces Fit Together

```text
                    ┌─────────────────────────────────────┐
                    │     North star: prosocial growth    │
                    └─────────────────────────────────────┘
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        ▼                               ▼                               ▼
  Participate                    Signal quality                   Preserve & discover
  (posts, replies,               (prosocial reactions,            (clips, collections,
   actions, guilds)               context notes, gratitude)        discovery ranking)
        │                               │                               │
        └───────────────────────────────┼───────────────────────────────┘
                                        ▼
                         Trust & privileges (ETS-first, domain-specific)
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
            Earn capabilities    Reflect & improve     Safe community
            (tags, notes,        (pre-send prompts,    (moderation,
             moderation)          journal, challenges)   appeals, crisis)
```

No single module carries the mission alone. **Actions** turn intent into verified help. **Knowledge** makes help durable. **Interactions** replace shallow likes with meaningful signals. **Trust** ensures influence follows demonstrated care. **AI Coach** and **Moderation** protect agency while reducing harm. **Gamification** and **Engagement** sustain habit without addiction.

---

## Implementation Status (Brief)

The platform is production-shaped for local and staged deployment (PostgreSQL, Docker Compose, pytest, security-hardened settings). Phases 0–12 deliver a working social core plus Functional Trust features end-to-end: prosocial reactions, civility prompts, context notes, appeals, scoped badges, and anti-gaming hooks.

Some vision elements remain partial or scaffolded: live LLM integration, payment processing for donations, MFA enrollment UI, full XP wiring for all action types, sentiment-based discovery, group messaging, and several navigation links to features that work but are hard to find. The **User Guide** (`UserGuide.md`) documents feature-by-feature status; **Prosocial Network Design** (`ProsocialNetworkDesign.md`) and **Functional Trust** (`FunctionalTrust.md`) describe the full product vision and trust-network themes.

---

## Summary

Common Good is a deliberately designed alternative to extractive social media. Its purpose is to help people become better community members — more helpful, more knowledgeable, more connected to action — by aligning every major system with that goal. It achieves this through multi-dimensional trust, prosocial reaction semantics, knowledge preservation, coordinated action with verification, gentle pre-send friction, human-centered moderation, and gamification that rewards depth over addiction. Each functional area plays a distinct role in that whole; together they aim to make constructive behavior the path of least resistance and greatest reward.

---

*For operational detail and route reference, see `UserGuide.md`. For architecture and phased roadmap, see `prosocial_platform/README.md` and `ProsocialNetworkDesign.md`.*
