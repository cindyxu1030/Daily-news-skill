<p align="right"><a href="README.md">English</a> | <strong>中文</strong></p>

# news-brief

一个为 [Claude Code](https://claude.com/claude-code) 打造的个性化每日**综合简报**技能。第一次运行时，它会先采访 / 研究你，写下一份持久的**读者画像**（agent 对「它在服务谁」的记忆）。之后每天，它从 **可信 RSS 源、Hacker News 与 Hugging Face API、你追踪的 YouTube 创作者、以及按域名定向的网页搜索** 跨*你的*视角抓取候选，按「时效 / 新鲜度 / 相关性 / 热度 / 跨领域共振 / 个人相关」给每条打分，对过去 7 天去重，挑出覆盖 ≥3 个视角的 5–8 条，并通过 **飞书私信、邮件或本地文件**送达。

📖 **新手？先看[手把手教程](TUTORIAL.zh-CN.md)（[English](TUTORIAL.md)）。**
👀 **想先看产出长什么样：[中文示例](examples/sample-brief.zh-CN.md) · [English sample](examples/sample-brief.md) · [真实飞书私信截图](examples/)。**

---

## 这个适合你吗？

**适合：** 会用 Claude Code、愿意敲几行终端命令、想要一份贴着自己领域的简报——一个先学会你、再照着挑的 agent。

**不适合：** 只想一键收 AI 新闻、不碰终端、期待零配置的人。（飞书是可选的——也能用邮件或本地文件——但 Claude Code 必须有。）

> **输出语言：** 技能的指令是英文写的，但简报会用你在画像里设定的语言输出（`Output language: 中文` → 全中文简报）。

---

## 快速开始

```bash
# 1. 克隆到你的 Claude Code 技能目录
git clone https://github.com/cindyxu1030/Daily-news-skill.git ~/.claude/skills/news-brief

# 2. 在 Claude Code 里跑一次——它会给你做引导（建画像 + 配置）
#    /news-brief

# 3. 先本地预览——写到 ~/Documents/NewsBrief/，什么都不发
NEWSBRIEF_DRY_RUN=1 ~/.claude/skills/news-brief/scripts/run_brief.sh

# 4. 自检配置
~/.claude/skills/news-brief/scripts/doctor.sh
```

引导会帮你生成 `~/.config/news-brief/{profile.md, sources.json, settings.json}`。想手动初始化，就复制示例（注意用完整路径，不必待在 repo 目录里）：

```bash
mkdir -p ~/.config/news-brief
cp ~/.claude/skills/news-brief/config/sources.example.json   ~/.config/news-brief/sources.json
cp ~/.claude/skills/news-brief/config/settings.example.json  ~/.config/news-brief/settings.json
cp ~/.claude/skills/news-brief/config/profile.example.md     ~/.config/news-brief/profile.md
```

然后选送达渠道、设定时——完整流程见**[教程](TUTORIAL.zh-CN.md)**。

---

## 信源

三层，一起打分——高信号，不是 SEO 榜单页：

- **确定性 feeds** —— `scripts/fetch_feeds.py` 抓真·RSS（AI 实验室、MIT Tech Review、BBC/NYT/Guardian/Al Jazeera/Diplomat、市场），加 Hacker News 与 Hugging Face 论文 API，每条都带真实发布时间戳。宽口径世界新闻 feed 支持 `filter_keywords` + `max_items`，让视角聚焦。
- **YouTube 创作者** —— 抓你追踪创作者的频道 RSS。**不需要 API key**（频道 RSS 自带播放量，爆款视频会被打 `outlier` 标记）。想要更稳的播放数据，加一个**免费** `YOUTUBE_API_KEY`——$0，每天 1 万配额。见[教程](TUTORIAL.zh-CN.md#加可信信源--youtube可选推荐)。
- **网页搜索** —— 按域名定向（用 `sources.json` 里的 `allowed_domains`），补全广度和 feed 之外的内容。

全部配在 `~/.config/news-brief/sources.json`（`feeds`、`lenses`）。feed 这一步失败也没关系——简报会退回到纯网页搜索，绝不卡住。

---

## 送达

在 `~/.config/news-brief/settings.json` 里设 `delivery`：

- **`file`**（默认）—— 存到 `~/Documents/NewsBrief/`，零配置，最适合测试。
- **`email`** —— 走 `scripts/send_email.py`（SMTP 凭据放 `~/.config/news-brief/.env`）。
- **`lark`** —— 飞书机器人私信。门槛最高：先按 **[cindyxu1030/lark-agents-bridge](https://github.com/cindyxu1030/lark-agents-bridge)** 搭好桥（装 `lark-cli`、建机器人 + 权限、完成授权），再填你的 `open_id`。完整流程见**[教程 → 飞书配置](TUTORIAL.zh-CN.md)**。

建议先用 `file` 跑通，确认输出顺眼，再切换。

---

## 个性化

一切都由 `~/.config/news-brief/profile.md` 和 `sources.json` 驱动——基本不用动 `SKILL.md` 本身：

- **读者画像** —— 你是谁、目标、会为什么去行动、输出语言。引导时生成，随时可改。
- **视角 + 信源** —— 你的话题和信任的媒体（`sources.json` → `lenses`）。
- **Feeds + YouTube** —— RSS/API 源地址和你的 YouTube `channel_id`（`sources.json` → `feeds`）。见[教程](TUTORIAL.zh-CN.md#加可信信源--youtube可选推荐)。
- **个人相关信号** —— 让一条新闻「算是为你」的模式（在 `profile.md` 里）。

完整格式见 `config/profile.example.md`。

---

## 它不做什么

- 不带人设语气、不生成脚本、不产出社媒文案。是综合阅读器，不是内容流水线。
- 没有一键魔法——需要配置（见「这个适合你吗」）。
- 不制造虚假紧迫感。淡日 → 少发几条，绝不凑数。

---

## 文件说明

- `SKILL.md` —— 技能定义、引导、运行流程
- `scripts/run_brief.sh` —— 定时入口（`NEWSBRIEF_MODEL` 可配模型、`NEWSBRIEF_DRY_RUN=1` 本地预览、带重试/退避）
- `scripts/fetch_feeds.py` —— 确定性 RSS/API/YouTube 抓取（`feeds` 注册表）；YouTube 不需 key，可选 `YOUTUBE_API_KEY` 解锁 outlier 排序。见[教程](TUTORIAL.zh-CN.md#加可信信源--youtube可选推荐)
- `scripts/doctor.sh` —— 自检配置（claude、python3、lark-cli、配置、占位符）
- `scripts/send_email.py` —— 可选的 SMTP 送达
- `config/*.example.*` —— `profile.md`、`sources.json`、`settings.json` 的模板
- `examples/` —— 简报示例（英文 + 中文）
- `TUTORIAL.md` / `TUTORIAL.zh-CN.md` —— 手把手搭建教程

运行状态在 `~/.config/news-brief/`；归档在 `~/Documents/NewsBrief/`。

> **关于「保证」：** 去重、缓存过期、打分日志都是 agent 每次运行时自己维护的（prompt 驱动），不是数据库强制的。尽力而为——对个人简报够用，但不是确定性软件。

---

## 许可

MIT —— 见 `LICENSE`。
