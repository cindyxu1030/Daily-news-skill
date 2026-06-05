<p align="right"><strong>English</strong> | <a href="README.zh-CN.md">中文</a></p>

# news-brief

A personalized daily **synthesis brief** skill for [Claude Code](https://claude.com/claude-code). On first run it interviews/researches you and writes a persistent **reader profile** (the agent's memory of who it serves). Then, each day, it searches the last 24 hours across *your* lenses, scores each story on recency / novelty / relevance / trending heat / cross-category resonance / personal-relevance, dedupes against the past week, picks 5–8 stories spanning ≥3 lenses, and delivers a synthesis brief via **Lark DM, email, or a local file**.

📖 **New here? Read the [step-by-step tutorial](TUTORIAL.md) ([中文](TUTORIAL.zh-CN.md)).**
👀 **See what it produces: [sample brief](examples/sample-brief.md) · [中文示例](examples/sample-brief.zh-CN.md) · [real Lark DM screenshot](examples/).**

---

## Is this for you?

**Good fit:** you use Claude Code, are OK with a few terminal commands, and want a brief tuned to your field — an agent that learns you once and curates accordingly.

**Not a fit:** you just want a one-click AI-news feed, won't touch a terminal, or expect zero setup. (Lark is optional — email or a local file work too — but Claude Code is required.)

> **Output language:** the skill's instructions are in English, but the brief is written in whatever language you set in your profile (`Output language: 中文` → a fully Chinese brief).

---

## Quickstart

```bash
# 1. Clone into your Claude Code skills directory
git clone https://github.com/cindyxu1030/Daily-news-skill.git ~/.claude/skills/news-brief

# 2. In Claude Code, run it once — it onboards you (builds your profile + config)
#    /news-brief

# 3. Preview locally first — writes to ~/Documents/NewsBrief/, sends nothing
NEWSBRIEF_DRY_RUN=1 ~/.claude/skills/news-brief/scripts/run_brief.sh

# 4. Check your setup
~/.claude/skills/news-brief/scripts/doctor.sh
```

Onboarding seeds `~/.config/news-brief/{profile.md, sources.json, settings.json}` for you. To seed them manually instead, copy the examples (note the full path — you don't need to be inside the repo):

```bash
mkdir -p ~/.config/news-brief
cp ~/.claude/skills/news-brief/config/sources.example.json   ~/.config/news-brief/sources.json
cp ~/.claude/skills/news-brief/config/settings.example.json  ~/.config/news-brief/settings.json
cp ~/.claude/skills/news-brief/config/profile.example.md     ~/.config/news-brief/profile.md
```

Then pick a delivery channel and schedule it — full walkthrough in the **[tutorial](TUTORIAL.md)**.

---

## Delivery

Set `delivery` in `~/.config/news-brief/settings.json`:

- **`file`** (default) — saved to `~/Documents/NewsBrief/`. Zero config. Best for testing.
- **`email`** — via `scripts/send_email.py` (SMTP creds in `~/.config/news-brief/.env`).
- **`lark`** — Lark/飞书 bot DM. Highest friction: set up the bridge first via **[cindyxu1030/lark-agents-bridge](https://github.com/cindyxu1030/lark-agents-bridge)** (installs `lark-cli`, creates the bot + scopes, authenticates), then add your `open_id`. Full walkthrough in the **[tutorial → Lark setup](TUTORIAL.md)**.

Start with `file`, confirm the output looks right, then switch.

---

## Personalize

Everything is driven by `~/.config/news-brief/profile.md` and `sources.json` — you rarely edit `SKILL.md` itself:

- **Reader profile** — who you are, goals, what you'd act on, output language. Built by onboarding; edit anytime.
- **Lenses + sources** — your topics and the outlets you trust (`sources.json`).
- **Personal-relevance signal** — the patterns that make a story "for you" (in `profile.md`).

See `config/profile.example.md` for the full shape.

---

## What it does NOT do

- No persona voice, no script generation, no social output. A synthesis reader, not a content pipeline.
- No one-click magic — it needs setup (see "Is this for you?").
- No fabricated urgency. Slow day → fewer stories, no padding.

---

## Files

- `SKILL.md` — skill definition, onboarding, and run flow
- `scripts/run_brief.sh` — scheduler entrypoint (configurable model via `NEWSBRIEF_MODEL`, `NEWSBRIEF_DRY_RUN=1` for local preview, retry/backoff)
- `scripts/doctor.sh` — checks your setup (claude, lark-cli, config, placeholders)
- `scripts/send_email.py` — optional SMTP delivery
- `config/*.example.*` — templates for `profile.md`, `sources.json`, `settings.json`
- `examples/` — sample briefs (EN + 中文)
- `TUTORIAL.md` / `TUTORIAL.zh-CN.md` — step-by-step build guide

State lives under `~/.config/news-brief/`; archives under `~/Documents/NewsBrief/`.

> **Note on guarantees:** dedup, cache expiry, and the scoring log are maintained by the agent each run (prompt-driven), not enforced by a database. Best-effort — good for a personal brief, not deterministic software.

---

## License

MIT — see `LICENSE`.
