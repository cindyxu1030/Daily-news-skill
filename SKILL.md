---
name: news-brief
description: A personalized daily synthesis brief. Use when the user types /news-brief, /brief, /NewsBrief, "run news brief", "set up news brief", "today's news", "morning news", "daily brief", "news digest", "AI news", or similar. On first run it interviews/researches the reader and writes a persistent profile (the agent's memory of who it serves). Then it searches the last 24 hours across the reader's configurable lenses, scores on recency + novelty + relevance + trending heat + cross-category resonance + a personal-relevance signal, deduplicates against last 7 days, selects 5–8 stories spanning ≥3 lenses, and delivers a synthesis brief via Lark DM, email, or a local markdown file. Selection biased toward what compounds; tone factual. Can run automatically on a daily schedule via LaunchAgent (macOS) or cron.
---

# News Brief — Personalized Synthesis Brief

Purpose: Surface industry signal that compounds for **its reader**. The brief helps the reader stay current in their field, spot opportunities, and fuel cross-domain synthesis. **Selection biased toward what compounds; tone factual.**

The reader is defined by `~/.config/news-brief/profile.md` — built once during onboarding and read on every run. It is the agent's long-term memory of who this brief serves.

---

## First run — build the reader profile (onboarding)

**Trigger this section when** `~/.config/news-brief/profile.md` is missing, OR the user says "set up news brief" / "redo my profile". After it completes, continue into the normal Run flow.

Goal: produce `profile.md`, `sources.json`, and `settings.json` for this reader. Use BOTH research and interview — research what the reader hands you, interview to fill the gaps.

### A. Research (use what the reader already has)

Ask once: *"To tune this to you — share anything that describes you: a short bio, a link to your X / LinkedIn / personal site, or a path to a notes file. Or skip and I'll just ask you a few questions."*

- If a URL is given → WebFetch it; extract role, field, recurring themes, the people/outlets they reference.
- If a local file path is given → read it.
- **Only read what the reader hands you.** Do not hunt beyond provided links. (See the privacy note in the tutorial.)

### B. Interview (ask only what research didn't already answer)

1. What do you do? (role / industry / what you're building)
2. What 4–6 topics do you want to track daily? → these become your **lenses**.
3. For each topic, which outlets or people do you trust most?
4. What decisions or actions should this brief feed — what would you actually *act on*?
5. Where do you discover news today? (so the brief mirrors your real sources)
6. Delivery channel: **Lark DM**, **email**, or **local file**? + the recipient (Lark `open_id` or email address).
7. Any tone preferences? (default: factual, no hype)
8. **Output language** for the brief? (e.g. English / 中文 / bilingual — default English)

### C. Synthesize + write (confirm before saving)

Draft, show the reader, adjust on feedback, then write:

1. `~/.config/news-brief/profile.md` — see the template in `config/profile.example.md`. Fill: who they are, goals, what they'd act on, their lenses (with a one-line "why it matters to me" each), their personal-relevance patterns, tone, and **output language**.
2. `~/.config/news-brief/sources.json` — seed from their lenses + trusted outlets, using the `config/sources.example.json` shape.
3. `~/.config/news-brief/settings.json` — using `config/settings.example.json` shape: `delivery` (lark|email|file) + recipient fields.

Confirm one line: *"Profile saved. Run `/news-brief` anytime, or I'll run it now."* Then continue to the Run flow.

---

## Run flow

### Step 1 — Load profile + caches

Read (create empty if missing):

- `~/.config/news-brief/profile.md` — **the reader.** If missing → run onboarding above first.
- `~/.config/news-brief/settings.json` — delivery channel + recipient + tone.
- `~/.config/news-brief/sources.json` — lens registry (sources + search guidance). See `config/sources.example.json`.
- `~/.config/news-brief/seen.json` — rolling **7-day** dedup cache; array of `{url, headline_hash, date}`
- `~/.config/news-brief/category_history.json` — rolling **14-day** log; array of `{date, lenses_used: [], story_count: N}`
- `~/.config/news-brief/scoring_log.jsonl` — rolling **30-day** per-story scoring log (debug aid)

### Step 2 — Search each lens (WebSearch, last 24hr)

Run 2–3 targeted WebSearch queries per lens defined in `sources.json` / `profile.md`. Use the listed domains to shape search terms. **Stories can carry MULTIPLE lenses — tag accordingly.**

**Add 2 dedicated trending-heat searches** (cross-lens), adapted to the reader's field:
- "Hacker News front page [reader's field] today" / "trending HN [field]"
- "X / trending [field] thread today"

### Step 3 — Score each candidate

Each story scored on these axes. **Sum scores; do not average.** Highest totals win.

| Axis | Range | Notes |
|---|---|---|
| **Recency (×2)** | 0–10 | last 6hr = 10 · 6–24hr = 8 · 24–48hr = 5 · >48hr = reject |
| **Novelty** | 0–10 | exact match in seen.json = 0 · same topic new angle = 4–6 · fresh = 8–10 |
| **Relevance** | 0–10 | stands on its own as worth knowing. No angle-forcing. |
| **Trending Heat** | 0–10 | viral on X/HN/Reddit/PH OR cited across ≥3 authoritative outlets in 24hr = 8–10 · moderate = 4–6 · niche = 0–3 |
| **Cross-Category Resonance (CCR)** | 0–5 | ≥2 lenses = +3 · ≥3 lenses = +5. **Gated by novelty ≥7.** Otherwise CCR = 0. |
| **Personal-Relevance Signal** | 0–5 | match against the patterns in `profile.md` → "Personal-relevance signal". The stronger the match to who this reader is and what they'd act on, the higher. |

**Hard rules:**
- Drop anything in `seen.json` unless real new development (new model, new data, new milestone).
- CCR override: stories with CCR ≥3 + novelty ≥8 cannot be dropped by lens-cap penalty.

### Step 4 — Select 5–8 stories

- **Span ≥3 lenses.** If top stories cluster in 1–2, demote duplicates and promote next-best from other lenses.
- **Soft penalty for over-used lens** — lens used 3 days running = −1 score. **Exception**: story with CCR ≥2 ignores the penalty.
- **Flex story count**: slow day (<5 stories scoring 25+) → 5, **no padding** · default → 6 · hot day (≥2 stories scoring 30+) → up to 8.
- **1 wildcard slot**: highest-novelty story regardless of lens.
- **Drop "Skipped today" filler.** Just deliver the picks.

### Step 5 — Format brief body

Write to `/tmp/newsbrief_body.txt`. Tone per `profile.md` (default factual; selection biased). **Write in the reader's output language from `profile.md`** (default English) — labels, summaries, and "why it matters" all follow that language.

```
N stories for today — lenses: [list].

━━━ [LENS NAME] ━━━
1. [Headline]
   [Source] · [URL] · [X] hours ago
   Summary: 2–3 sentences. What happened + why it happened.
   Why it matters: 1 sentence. The actual stakes — name the mechanism.
   Why it matters to you: 1 sentence. The angle for THIS reader, per profile.md. (OPTIONAL — only when genuine; skip when weak. Do NOT force.)

━━━ [NEXT LENS] ━━━
2. ...

━━━ WILDCARD ━━━
N. ...
```

**"Why it matters to you" rules:** optional per story; include only when the angle to this reader's goals/actions is real and specific. Not script-writing, not persona voice, not a CTA. Generic "good for people like you" → SKIP.

### Step 6 — Deliver (channel from `settings.json`)

**Dry run first:** if env `NEWSBRIEF_DRY_RUN=1` (or `settings.json` `delivery` = `file`), skip sending — write the archive only (Step 8) and report the path. Run this way until the output looks right, then switch on Lark/email.

Otherwise read `delivery` from `settings.json`. One of:

**`lark`** — DM from your app bot to the reader's open_id:
```bash
BODY="$(cat /tmp/newsbrief_body.txt)"
lark-cli im +messages-send --as bot --user-id "<open_id from settings.json>" --text "$BODY"
```
Chunking: if `wc -c < /tmp/newsbrief_body.txt` > **25000**, split on `━━━ ` boundaries into sequential messages, prefixing `(2/N)`, `(3/N)`, … If `lark-cli` exits non-zero: print body in conversation; run `lark-cli auth status` (needs scope `im:message.send_as_bot`).

**`email`** — send via the bundled sender (SMTP creds from env / `~/.config/news-brief/.env`):
```bash
python3 ~/.claude/skills/news-brief/scripts/send_email.py \
  --to "<email from settings.json>" \
  --subject "News Brief — $(date '+%Y-%m-%d')" \
  --body-file /tmp/newsbrief_body.txt
```
If it exits non-zero: print the body in conversation and point the reader to the email setup in `TUTORIAL.md`.

**`file`** — no send; the archive in Step 8 is the delivery. Tell the reader the path.

### Step 7 — Update caches + log

- Append today's stories to `seen.json` as `{url, headline_hash, date}`. Expire >7 days.
- Append today's entry to `category_history.json` as `{date, lenses_used: [...], story_count: N}`. Expire >14 days.
- Append per-story scoring entries to `scoring_log.jsonl`:
  ```json
  {"date": "YYYY-MM-DD", "headline": "...", "url": "...", "lenses": [...], "scores": {"recency": 10, "novelty": 9, "relevance": 9, "heat": 8, "ccr": 5, "signal": 4}, "total": 45, "selected": true, "reject_reason": null}
  ```
  Log BOTH selected and top-5 rejected per day. Expire >30 days. Use it to debug future misses.

### Step 8 — Archive

Save brief body as markdown to `~/Documents/NewsBrief/YYYY-MM-DD.md`. Overwrite if re-run same day.

### Step 9 — Confirm

```
News Brief delivered via [channel] — N stories, lenses: [list]. Archive: ~/Documents/NewsBrief/YYYY-MM-DD.md
```

---

## Standing rules

- **The reader is `profile.md`.** Bias selection toward who they are and what they'd act on. Re-read it every run.
- **Tone factual; selection biased.** No persona voice, no marketing voice.
- **No script generation, no CTAs.** Brief is fuel for synthesis, not output.
- **No fabricated urgency.** Slow news → ship 5 stories, no padding.
- **Dedup by storyline, not entity.** Same company, different events = both OK. Compare headline_hash + storyline.
- **Cite source + URL for every story.** Non-negotiable.
- **"Why it matters" must be specific** — name the mechanism (who's affected, how much, by when).
- **Today's date = today.** Use `currentDate` from system context. Don't include stories older than 48hr.

---

## Models

- Scheduled invocation (`run_brief.sh`): Sonnet 4.6 for cost efficiency.
- Interactive invocation: session's active model.
