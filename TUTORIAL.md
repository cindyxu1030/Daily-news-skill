<p align="right"><strong>English</strong> | <a href="TUTORIAL.zh-CN.md">中文</a></p>

# Build your own news brief agent — step by step

This walks you from clone → a personalized daily brief that knows who you are.

---

## Is this for you?

**Good fit if you:** use [Claude Code](https://claude.com/claude-code), are OK running a few terminal commands, and want a daily brief tuned to *your* field — not a generic feed. The reward: an agent that researches you once, remembers it, and curates accordingly.

**Not a fit if you:** just want to click a button and get AI news, don't want to touch a terminal, or don't use Lark. (You can still use **email** or a **local file** instead of Lark — see Step 4 — but you do need Claude Code.)

**Prerequisites:** Claude Code installed; a terminal; *optionally* a Lark account + `lark-cli` if you want Lark delivery.

---

## Step 1 — Clone

```bash
git clone https://github.com/cindyxu1030/Daily-news-skill.git ~/.claude/skills/news-brief
```

## Step 2 — Let the agent learn who you are (onboarding)

In Claude Code, run:

```
/news-brief
```

The first time, there's no profile yet, so the skill **onboards you**: it offers to read a bio / link / notes you provide (research), then asks a handful of questions (interview) — your field, the 4–6 topics you want to track, who you trust, what you'd act on, delivery channel, and output language.

It then writes three files to `~/.config/news-brief/`:
- `profile.md` — the agent's memory of you (read every run)
- `sources.json` — your topics + trusted outlets
- `settings.json` — delivery channel + recipient + output language

Review them; edit anytime. See `config/profile.example.md` for the shape.

> **Tip:** want the brief in Chinese? Set `Output language: 中文` in `profile.md` (the single source for language and tone). The whole brief is then written in that language — even though this skill's instructions are in English.

## Step 3 — Run it locally first (dry run)

Don't wire up delivery yet. See the output on your own machine first. Either keep `settings.json` `delivery: "file"`, or:

```bash
NEWSBRIEF_DRY_RUN=1 ~/.claude/skills/news-brief/scripts/run_brief.sh
```

The brief lands in `~/Documents/NewsBrief/YYYY-MM-DD.md`. Read it. Tune `profile.md` / `sources.json` until the picks feel right. Re-run.

Check your setup anytime:

```bash
~/.claude/skills/news-brief/scripts/doctor.sh
```

It reports what's installed, what's configured, and any unreplaced placeholders.

## Step 4 — Choose how it's delivered

Set `delivery` in `~/.config/news-brief/settings.json`.

### Option A — Local file (zero config)
`delivery: "file"`. The brief is just saved to `~/Documents/NewsBrief/`. Simplest; nothing to install.

### Option B — Email
`delivery: "email"`, set `email_to`. Put SMTP credentials in `~/.config/news-brief/.env`:

```
NEWSBRIEF_SMTP_USER=you@gmail.com
NEWSBRIEF_SMTP_PASS=your-16-char-app-password
NEWSBRIEF_SMTP_HOST=smtp.gmail.com
NEWSBRIEF_SMTP_PORT=465
```

For Gmail you need an **App Password** (not your account password): myaccount.google.com → Security → 2-Step Verification → App passwords. Test:

```bash
python3 ~/.claude/skills/news-brief/scripts/send_email.py \
  --to you@gmail.com --subject "test" --body-file ~/Documents/NewsBrief/$(date +%F).md
```

### Option C — Lark DM (飞书)

This is the highest-friction path. Do it only if you actually use Lark.

1. **Set up the Lark bridge** — follow **[cindyxu1030/lark-agents-bridge](https://github.com/cindyxu1030/lark-agents-bridge)**. It installs `lark-cli` (`npm install -g @larksuite/cli`), walks you through creating the Lark app + bot, enabling the right scopes, and authenticating (`lark-cli config init` → `lark-cli auth login`). Finish that until `lark-cli auth status` succeeds, then come back here.
2. **Get your open_id** — the brief DMs *you*. Print your `open_id`:
   ```bash
   lark-cli contact +get-user --jq '.data.user.open_id'   # prints your ou_... id
   ```
   Put it in `settings.json` as `lark_open_id`, and set `delivery: "lark"`.
3. **Common errors:**
   - `lark-cli: command not found` → bridge not installed / not on PATH (revisit the bridge setup).
   - auth / token expired → re-run `lark-cli auth login`.
   - permission denied on send → the bot is missing a send scope; check the scope list in [lark-agents-bridge](https://github.com/cindyxu1030/lark-agents-bridge), add it in the developer console, and re-auth.
   - run `~/.claude/skills/news-brief/scripts/doctor.sh` to check auth + a still-unreplaced `<YOUR_LARK_OPEN_ID>`.

## Step 5 — Schedule it daily

### macOS (LaunchAgent)
Create `~/Library/LaunchAgents/com.example.newsbrief.plist` (use your own reverse-DNS label), pointing `ProgramArguments` at `~/.claude/skills/news-brief/scripts/run_brief.sh`, with a `StartCalendarInterval` for your time. Then:

```bash
launchctl load ~/Library/LaunchAgents/com.example.newsbrief.plist
```

### Linux (cron)
```
0 8 * * *  $HOME/.claude/skills/news-brief/scripts/run_brief.sh
```

Pick the model with `NEWSBRIEF_MODEL` (default `sonnet`; e.g. `NEWSBRIEF_MODEL=opus` for deeper synthesis).

## Add trusted feeds + YouTube (optional, recommended)

Plain web search returns mostly SEO listicles. `scripts/fetch_feeds.py` fixes that: it reads the `feeds` block in `sources.json` and pulls real RSS feeds, the Hacker News + Hugging Face APIs, and YouTube channels into the candidate pool — with verified publish timestamps. It runs automatically at the start of Step 2; you just edit the registry.

**Edit `~/.config/news-brief/sources.json` → `feeds`:**
- `rss` — add `{ "lens": "...", "source": "...", "url": "https://.../feed.xml" }`. For broad world feeds add `"filter_keywords": [...]` + `"max_items": 12` so they stay on-topic.
- `api` — Hacker News + Hugging Face papers are pre-wired.
- `youtube_channels` — add `{ "lens": "...", "source": "Creator Name", "channel_id": "UC..." }`.

**Find a YouTube `channel_id`:** open the channel page → View Source → search for `"channelId":"UC…"` (or `"externalId":"UC…"`). It always starts with `UC`. Paste it in.

**YouTube works with NO API key** — channel RSS already includes view counts, so overperforming videos still get flagged. For more reliable view data, add a **free** key:
1. console.cloud.google.com → new project → APIs & Services → enable **YouTube Data API v3**.
2. Credentials → Create API key.
3. Put `YOUTUBE_API_KEY=your-key` in `~/.config/news-brief/.env` (gitignored).
Cost: **$0** — 10,000 quota units/day free; a daily brief uses ~1–3.

**Test it:** `python3 ~/.claude/skills/news-brief/scripts/fetch_feeds.py` then look at `/tmp/newsbrief_candidates.json` — confirm a healthy `counts.total` and that `failed_feeds` lists only paywalled ones (Bloomberg/WSJ/FT are flaky by design).

## Step 6 — Tune over time

- Edit `profile.md` whenever your focus shifts — the next brief picks it up.
- Inspect `~/.config/news-brief/scoring_log.jsonl` to see *why* a story was picked or dropped, and adjust your lenses / personal-relevance patterns.

---

## Privacy

- **WebSearch** queries are public web searches.
- Anything you hand the agent during onboarding (a bio, a link, a notes file) is read to build your profile. A URL is fetched; a local file is read locally. The agent only reads what you give it — it doesn't go hunting beyond your links.
- `profile.md`, your config, caches, and archives all stay **local** under `~/.config/news-brief/` and `~/Documents/NewsBrief/`.
- Delivery sends the brief to *your* channel (your Lark, your email, your disk).

## Note on guarantees

Dedup, cache expiry, and the scoring log are maintained by the agent each run (prompt-driven), not enforced by a database. They're best-effort and good enough for a personal brief — not deterministic software. If you want hard guarantees, wrap the cache files with your own script.
