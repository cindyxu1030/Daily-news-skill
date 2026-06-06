<p align="right"><strong>English</strong> | <a href="README.zh-CN.md">中文</a></p>

# news-brief

A personalized daily **synthesis brief** — an agentic skill built for [Claude Code](https://claude.com/claude-code) and portable to other LLM agents (see [Runtime & models](#runtime--models)). On first run it interviews/researches you and writes a persistent **reader profile** (the agent's memory of who it serves). Then, each day, it pulls candidates from **trusted RSS feeds, the Hacker News & Hugging Face APIs, your tracked YouTube creators, and domain-steered web search** across *your* lenses, scores each story on recency / novelty / relevance / trending heat / cross-category resonance / personal-relevance, dedupes against the past week, picks 5–8 stories spanning ≥3 lenses, and delivers a synthesis brief via **Lark DM, email, or a local file**.

📖 **New here? Read the [step-by-step tutorial](TUTORIAL.md) ([中文](TUTORIAL.zh-CN.md)).**
👀 **See what it produces: [sample brief](examples/sample-brief.md) · [中文示例](examples/sample-brief.zh-CN.md) · [real Lark DM screenshot](examples/).**

---

## Is this for you?

**Good fit:** you use an agentic LLM CLI (Claude Code is the reference; Codex or any agent with web-search + shell + file tools works too), are OK with a few terminal commands, and want a brief tuned to your field — an agent that learns you once and curates accordingly.

**Not a fit:** you just want a one-click AI-news feed, won't touch a terminal, or expect zero setup. (Lark is optional — email or a local file work too — but you do need an agentic LLM CLI; see [Runtime & models](#runtime--models).)

> **Output language:** the skill's instructions are in English, but the brief is written in whatever language you set in your profile (`Output language: 中文` → a fully Chinese brief).

---

## Runtime & models

**Not locked to Claude Code, and not locked to one model.**

- **Model** — any. Claude (Opus / Sonnet / Haiku) by default; DeepSeek, MiniMax, Zhipu/GLM, GPT, etc. work too, set via your agent's model config or `NEWSBRIEF_MODEL`. The run-flow doesn't care which model writes the brief.
- **Runtime** — the 9-step flow in `SKILL.md` is plain instructions. Any agentic CLI with **web search + shell + file** tools can execute it (Codex, etc.). Only the *packaging* is Claude-Code-specific and easily swapped:
  - skill auto-discovery + the `/news-brief` trigger → on another agent, paste/point it at `SKILL.md`;
  - `scripts/run_brief.sh`'s `claude …` line → replace with your agent's CLI invocation.
- **Runtime-agnostic already** — `scripts/fetch_feeds.py` (feeds + YouTube) and `scripts/send_email.py` are plain Python; they run the same under any agent.

Claude Code is the path of least resistance (slash command + scheduling work out of the box); everything else is a small adaptation, not a rewrite.

---

## Quickstart

**1. Clone** into your Claude Code skills directory:

```bash
git clone https://github.com/cindyxu1030/Daily-news-skill.git ~/.claude/skills/news-brief
```

**2. Onboard** — in Claude Code, run `/news-brief` once. It interviews you and writes your profile + config. **Do this before step 3** — the dry run needs your profile, and will refuse to run without it.

**3. Preview + check** — once onboarded, run a local dry run (writes to `~/Documents/NewsBrief/`, sends nothing) and the setup checker:

```bash
NEWSBRIEF_DRY_RUN=1 ~/.claude/skills/news-brief/scripts/run_brief.sh
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

## Sources

Three layers, scored together — high signal, not SEO listicles:

- **Deterministic feeds** — `scripts/fetch_feeds.py` pulls real RSS (AI labs, MIT Tech Review, BBC/NYT/Guardian/Al Jazeera/Diplomat, markets) plus the Hacker News & Hugging Face daily-papers APIs, each with a verified publish timestamp. Broad world feeds take `filter_keywords` + `max_items` so a lens stays on-topic.
- **YouTube creators** — per-channel RSS for the creators you track. **Works with no API key** (channel RSS carries view counts, so overperforming videos get an `outlier` flag). Add a **free** `YOUTUBE_API_KEY` for more reliable view data — $0, 10k quota/day. See the [tutorial](TUTORIAL.md#add-trusted-feeds--youtube-optional-recommended).
- **Web search** — domain-steered (`allowed_domains` from your `sources.json`) for breadth and anything outside your feed list.

All configured in `~/.config/news-brief/sources.json` (`feeds`, `lenses`). If the feed pass fails, the brief falls back to web search only — never blocks.

---

## Delivery

Set `delivery` in `~/.config/news-brief/settings.json`:

- **`file`** (default) — saved to `~/Documents/NewsBrief/`. Zero config. Best for testing.
- **`email`** — via `scripts/send_email.py` (SMTP creds in `~/.config/news-brief/.env`).
- **`lark`** — Lark/飞书 bot DM. Highest friction: set up the bridge first via **[cindyxu1030/lark-agents-bridge](https://github.com/cindyxu1030/lark-agents-bridge)** (installs `lark-cli`, creates the bot + scopes, authenticates), then add your `open_id`. Full walkthrough in the **[tutorial → Lark setup](TUTORIAL.md#step-4--choose-how-its-delivered)**.

Start with `file`, confirm the output looks right, then switch.

---

## Personalize

Everything is driven by `~/.config/news-brief/profile.md` and `sources.json` — you rarely edit `SKILL.md` itself:

- **Reader profile** — who you are, goals, what you'd act on, output language. Built by onboarding; edit anytime.
- **Lenses + sources** — your topics and the outlets you trust (`sources.json` → `lenses`).
- **Feeds + YouTube** — RSS/API feed URLs and your YouTube `channel_id`s (`sources.json` → `feeds`). See the [tutorial](TUTORIAL.md#add-trusted-feeds--youtube-optional-recommended).
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
- `scripts/fetch_feeds.py` — deterministic RSS/API/YouTube ingestion (the `feeds` registry); keyless YouTube, optional `YOUTUBE_API_KEY` for outlier ranking. See the [tutorial](TUTORIAL.md#add-trusted-feeds--youtube-optional-recommended)
- `scripts/doctor.sh` — checks your setup (claude, python3, lark-cli, config, placeholders)
- `scripts/send_email.py` — optional SMTP delivery
- `config/*.example.*` — templates for `profile.md`, `sources.json`, `settings.json`
- `examples/` — sample briefs (EN + 中文)
- `TUTORIAL.md` / `TUTORIAL.zh-CN.md` — step-by-step build guide

State lives under `~/.config/news-brief/`; archives under `~/Documents/NewsBrief/`.

> **Note on guarantees:** dedup, cache expiry, and the scoring log are maintained by the agent each run (prompt-driven), not enforced by a database. Best-effort — good for a personal brief, not deterministic software.

---

## License

MIT — see `LICENSE`.
