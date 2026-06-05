# news-brief

A personalized daily **synthesis brief** skill for [Claude Code](https://claude.com/claude-code). Searches the last 24 hours across 5 configurable lenses, scores each story on recency / novelty / relevance / trending heat / cross-category resonance / personal-relevance signal, dedupes against the past week, picks 5–8 stories spanning ≥3 lenses, and **delivers the digest as a Lark DM** (bot → you). Built as a personal reader and synthesis primer — not a content pipeline.

**Default lenses** (edit to your own interests): AI Core · AI × Marketing · Tech Macro · Geopolitics & Econ · Culture & Creator Economy

Runs on demand (`/news-brief`) or on a daily schedule.

---

## Install

1. Clone into your Claude Code skills directory:
   ```bash
   git clone https://github.com/cindyxu1030/Daily-news-skill.git ~/.claude/skills/news-brief
   ```
2. Authenticate the Lark bridge — delivery goes through [`lark-cli`](https://github.com/) as a bot DM. **No email / SMTP / app password needed.**
   ```bash
   lark-cli auth status        # confirm logged in
   # if not: lark-cli auth login   (needs scope im:message.send_as_bot)
   ```
3. Seed your config:
   ```bash
   mkdir -p ~/.config/news-brief
   cp config/sources.example.json ~/.config/news-brief/sources.json
   # then edit sources.json with your lenses + trusted outlets
   ```
4. (Optional) Schedule a daily run via macOS LaunchAgent or cron — see **Schedule** below.

Trigger manually inside Claude Code: `/news-brief` or "run news brief".

---

## Personalize

This skill is meant to be forked and made your own. Edit in `SKILL.md`:

### 1. Reader profile

`SKILL.md` top — rewrite the **Reader profile (EDIT ME)** line to describe yourself: role, field, what you want the brief to help you do. This biases selection. The more specific, the better the picks.

### 2. Lenses + sources

`SKILL.md` Step 2 — edit the 5-lens table to your interests (e.g., Climate, Biotech, Sports, Local Politics). Mirror the same lenses in `~/.config/news-brief/sources.json` with the domains/publications you trust.

If you change the number of lenses, also update Step 4's variety rule (`span ≥3 lenses`).

### 3. Personal-relevance signal

`SKILL.md` Step 3 — the **Personal-Relevance Signal** axis ships with a solo-founder/creator pattern list. Replace it with the patterns that matter for *your* profile.

### 4. Lark recipient

`SKILL.md` Step 6 — replace `<YOUR_LARK_OPEN_ID>` with your own open_id (find it via `lark-cli contact` or your Lark admin).

### 5. Story count + format + archive

`SKILL.md` Step 4 (count + selection rules), Step 5 (brief template), Step 8 (archive path, default `~/Documents/NewsBrief/YYYY-MM-DD.md`).

---

## Schedule (optional)

Run daily via a macOS LaunchAgent. Create `~/Library/LaunchAgents/com.example.newsbrief.plist` (rename the label to your own reverse-DNS id) pointing at `scripts/run_brief.sh`, set `StartCalendarInterval` to your preferred time, then:

```bash
launchctl load ~/Library/LaunchAgents/com.example.newsbrief.plist
```

On Linux, a cron entry calling `scripts/run_brief.sh` works the same way.

---

## What it does NOT do

- No persona voice, no script generation, no social-media output. Pure synthesis digest.
- No email. Delivery is Lark DM only.
- No fabricated urgency. Slow news day → ships 5 stories with a "slow cycle" note instead of padding.
- No re-surfacing — strict 7-day dedup against `~/.config/news-brief/seen.json`.

---

## Files

- `SKILL.md` — skill definition + run flow
- `scripts/run_brief.sh` — scheduler entrypoint (invokes `claude -p "Run news brief"`, with retry/backoff)
- `config/sources.example.json` — template lens/source registry; copy to `~/.config/news-brief/sources.json`

State lives in `~/.config/news-brief/` (sources, seen-cache, category history, scoring log). Archive in `~/Documents/NewsBrief/`.

---

## License

MIT — see `LICENSE`.
