---
name: news-brief
description: A personalized daily synthesis brief. Use when the user types /news-brief, /brief, /NewsBrief, "run news brief", "run the news brief", or asks for "today's news", "morning news", "daily brief", "news digest", "AI news", or similar. Surfaces what's hot, groundbreaking, and compounding for the reader's specific interests. Searches the last 24 hours across 5 configurable lenses (default: AI Core, AI × Marketing, Tech Macro, Geopolitics & Econ, Culture & Creator Economy), scores on recency + novelty + relevance + trending heat + cross-category resonance + a personal-relevance signal, deduplicates against last 7 days, selects 5–8 stories spanning ≥3 lenses, and sends a synthesis brief via Lark DM (bot). Selection biased toward what compounds; tone factual. Can also run automatically on a daily schedule via a LaunchAgent (macOS) or cron.
---

# News Brief — Solopreneur Synthesis Brief

Purpose: Surface industry signal that compounds for **you**. The brief should help you stay current in your field, spot opportunities, and fuel cross-domain synthesis. **Selection biased toward what compounds; tone factual.**

> **⚙️ Customize this — start here.** This skill ships with a default reader profile (a solo founder / creator working in AI & tech) so it runs out of the box. Rewrite the line below to describe *yourself* — role, field, what you're trying to learn, what you'd act on. Then edit the lenses (Step 2) and the personal-relevance signal (Step 3) to match. The more specific your profile, the better the picks.
>
> **Reader profile (EDIT ME):** `<one or two sentences: who you are, your field, what you want this brief to help you do>`

---

## Run flow

### Step 1 — Load caches

Read these files (create empty if missing):

- `~/.config/news-brief/sources.json` — lens registry (sources + search guidance). See `config/sources.example.json` in this repo for the structure.
- `~/.config/news-brief/seen.json` — rolling **7-day** dedup cache; array of `{url, headline_hash, date}`
- `~/.config/news-brief/category_history.json` — rolling **14-day** log; array of `{date, lenses_used: [], story_count: N}`
- `~/.config/news-brief/scoring_log.jsonl` — rolling **30-day** per-story scoring log (debug aid)

### Step 2 — Search each lens (WebSearch, last 24hr)

Run 2–3 targeted WebSearch queries per lens. Use `sources.json` to shape search terms. **Stories can carry MULTIPLE lenses — tag accordingly.** The 5 default lenses (replace with your own interests):

| Lens | Scope |
|---|---|
| **AI Core** | Model releases, lab news, research, frontier-lab moves (OpenAI, Anthropic, Google DeepMind, Meta AI, DeepSeek, MiniMax, Kimi/Moonshot, ByteDance, research papers) |
| **AI × Marketing** | Adtech/martech updates, agency AI moves, marketing-platform updates, AI-creative tooling, ad-industry transformation (Marketing Brew, AdWeek, AdAge, Adobe, Salesforce, HubSpot, Search Engine Journal) |
| **Tech Macro** | Big tech earnings, chips, IPOs, VC moves, **AI services / consulting firms**, platform policy (Stratechery, The Information, TechCrunch, The Verge, Bloomberg tech) |
| **Geopolitics & Econ** | Wars, oil, rates, US-China decoupling, AI regulation (Reuters, FT, Bloomberg, WSJ, Semafor, Axios) |
| **Culture & Creator Economy** | Algorithm shifts, creator pay, viral moments, creator tools, platform policy (Platformer, Garbage Day, Link in Bio, Hung Up, Verge creator coverage) |

**Add 2 dedicated trending-heat searches** (cross-lens):
- "Hacker News front page AI today" / "trending HN AI startup"
- "X tech founder trending today" / "viral AI thread"

### Step 3 — Score each candidate

Each story scored on these axes. **Sum scores; do not average.** Highest totals win.

| Axis | Range | Notes |
|---|---|---|
| **Recency (×2)** | 0–10 | last 6hr = 10 · 6–24hr = 8 · 24–48hr = 5 · >48hr = reject |
| **Novelty** | 0–10 | exact match in seen.json = 0 · same topic new angle = 4–6 · fresh = 8–10 |
| **Relevance** | 0–10 | stands on its own as worth knowing. No angle-forcing. |
| **Trending Heat** | 0–10 | viral on X/HN/Reddit/PH OR cited across ≥3 authoritative outlets in 24hr = 8–10 · moderate buzz = 4–6 · niche = 0–3 |
| **Cross-Category Resonance (CCR)** | 0–5 | ≥2 lenses = +3 · ≥3 lenses = +5. **Gated by novelty ≥7.** Otherwise CCR = 0. |
| **Personal-Relevance Signal** | 0–5 | matches patterns specific to your reader profile — edit these to fit. Example (solo founder / creator): indie/solo raises, AI agency or services-firm moves, AI replacing traditional services, creator tooling, no-code/solo workflows, freelancer market shifts |

**Hard rules:**
- Drop anything in `seen.json` unless real new development (new model, new data, new milestone).
- CCR override: stories with CCR ≥3 + novelty ≥8 cannot be dropped by lens-cap penalty.

### Step 4 — Select 5–8 stories

- **Span ≥3 lenses.** If top stories cluster in 1–2, demote duplicates and promote next-best from other lenses.
- **Soft penalty for over-used lens** — lens used 3 days running = −1 score. **Exception**: story with CCR ≥2 ignores the penalty.
- **Flex story count**:
  - Slow day (<5 stories scoring 25+) → 5 stories. **No padding.**
  - Default day → 6 stories.
  - Hot day (≥2 stories scoring 30+) → up to 8 stories.
- **1 wildcard slot**: highest-novelty story regardless of lens.
- **Drop "Skipped today" filler** — wasted real estate. Just deliver the picks.

### Step 5 — Format brief body

Write to `/tmp/newsbrief_body.txt`. Tone factual; selection biased.

```
N stories for today — lenses: [list].

━━━ [LENS NAME] ━━━
1. [Headline]
   [Source] · [URL] · [X] hours ago
   Summary: 2–3 sentences. What happened + why it happened.
   Why it matters: 1 sentence. The actual stakes — name the mechanism.
   Why it matters to you: 1 sentence. The angle for your reader profile. (OPTIONAL — only when angle is real; skip when weak. Do NOT force.)

2. [Headline]
   ...

━━━ [NEXT LENS] ━━━
3. [Headline]
   ...

━━━ WILDCARD ━━━
N. [Headline]
   ...
```

**"Why it matters to you" rules:**
- Optional per story — include only when angle is genuine and specific.
- Not script-writing. Not persona voice. Not a marketing CTA.
- Pure synthesis prime — name the implication for your reader profile in one sentence.
- If angle is a generic "this is good for people like me" without specifics → SKIP.

### Step 6 — Send via Lark DM (bot → you)

Send brief as a Lark DM from your app bot to your Lark `open_id`. Replace the placeholder below with your own open_id (find it via `lark-cli contact` or your Lark admin).

Single message (default — body usually 2–5 KB):

```bash
BODY="$(cat /tmp/newsbrief_body.txt)"
lark-cli im +messages-send \
  --as bot \
  --user-id <YOUR_LARK_OPEN_ID> \
  --text "$BODY"
```

**Chunking rule** — Lark text-message API hard-caps payload size. If `wc -c < /tmp/newsbrief_body.txt` returns > **25000**, split into multiple sends:

1. Lead message: header line + lens list.
2. Split body on `━━━ ` boundaries — each lens block becomes its own message. Prepend chunk index `(2/N)`, `(3/N)`, ... to each follow-up.
3. Send chunks sequentially with same `--as bot --user-id ...` command.

If `lark-cli` exits non-zero: print body in conversation; run `lark-cli auth status`. Missing scope hint: `im:message.send_as_bot`, plus reauth if token expired.

### Step 7 — Update caches + log

- Append today's stories to `seen.json` as `{url, headline_hash, date}`. Expire entries >7 days.
- Append today's entry to `category_history.json` as `{date, lenses_used: [...], story_count: N}`. Expire entries >14 days.
- Append per-story scoring entries to `~/.config/news-brief/scoring_log.jsonl`:
  ```json
  {"date": "YYYY-MM-DD", "headline": "...", "url": "...", "lenses": [...], "scores": {"recency": 10, "novelty": 9, "relevance": 9, "heat": 8, "ccr": 5, "signal": 4}, "total": 45, "selected": true, "reject_reason": null}
  ```
  Log BOTH selected and top-5 rejected stories per day. Expire entries >30 days. Use this to debug future misses.

### Step 8 — Archive

Save brief body as markdown to `~/Documents/NewsBrief/YYYY-MM-DD.md`. Overwrite if re-run same day.

### Step 9 — Confirm

One-line confirmation:

```
News Brief sent via Lark DM — N stories, lenses: [list]. Archive: ~/Documents/NewsBrief/YYYY-MM-DD.md
```

---

## Standing rules

- **Tone factual; selection biased toward your interests.** No persona voice, no marketing voice.
- **No script generation, no CTAs.** Brief is fuel for synthesis, not output.
- **No fabricated urgency.** Slow news → ship 5 stories, no padding.
- **Dedup by storyline, not entity.** Two stories about the same company on different events = both OK. Compare headline_hash + storyline, not entity overlap alone.
- **Cite source + URL for every story.** Non-negotiable.
- **"Why it matters" must be specific** — name the actual mechanism (who's affected, how much, by when).
- **"Why it matters to you" is optional and earned.** Skip when angle is weak. Don't force formulaic lines.
- **Cross-category bias is intentional.** Stories spanning multiple lenses are higher value than single-bucket stories. Score reflects that.
- **Today's date = today.** Use `currentDate` from system context. Don't include stories older than 48hr.

---

## Models

- Scheduled invocation (`run_brief.sh`): Sonnet 4.6 for cost efficiency.
- Interactive invocation: session's active model.
