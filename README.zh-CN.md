<p align="right"><a href="README.md">English</a> | <strong>中文</strong></p>

# news-brief

一个为 [Claude Code](https://claude.com/claude-code) 打造的个性化每日**综合简报**技能。它会检索过去 24 小时、跨 5 个可配置视角（lens）的新闻，按照「时效性 / 新鲜度 / 相关性 / 热度 / 跨领域共振 / 个人相关信号」给每条打分，对过去 7 天去重，最终挑出覆盖 ≥3 个视角的 5–8 条，并通过 **Lark（飞书）机器人私信**把简报发给你。定位是个人阅读与思维原料，而非内容生产流水线。

**默认视角**（可改成你自己的关注点）：AI Core · AI × Marketing · Tech Macro · Geopolitics & Econ · Culture & Creator Economy

支持手动触发（`/news-brief`），也可以设成每天定时跑。

---

## 安装

1. 克隆到你的 Claude Code 技能目录：
   ```bash
   git clone https://github.com/cindyxu1030/Daily-news-skill.git ~/.claude/skills/news-brief
   ```
2. 配置 Lark 通道——简报通过 [`lark-cli`](https://github.com/) 以机器人私信发送，**不需要邮箱 / SMTP / 应用专用密码**：
   ```bash
   lark-cli auth status        # 确认已登录
   # 若未登录：lark-cli auth login（需要权限 im:message.send_as_bot）
   ```
3. 初始化配置：
   ```bash
   mkdir -p ~/.config/news-brief
   cp config/sources.example.json ~/.config/news-brief/sources.json
   # 然后编辑 sources.json，填入你的视角和信任的信源
   ```
4.（可选）用 macOS LaunchAgent 或 cron 设置每日定时——见下方**定时运行**。

在 Claude Code 里手动触发：`/news-brief` 或「run news brief」。

---

## 个性化

这个技能就是用来 fork 后改成你自己的。在 `SKILL.md` 里修改：

### 1. 读者画像

`SKILL.md` 顶部——把 **Reader profile (EDIT ME)** 那一行改成描述你自己：身份、领域、希望这份简报帮你做什么。这会直接影响选题。写得越具体，挑得越准。

### 2. 视角与信源

`SKILL.md` 第 2 步——把 5 个视角的表格改成你的关注点（比如气候、生物科技、体育、本地政治）。同时在 `~/.config/news-brief/sources.json` 里用同样的视角，填上你信任的媒体/域名。

如果你增减了视角数量，记得同步改第 4 步的多样性规则（`span ≥3 lenses`）。

### 3. 个人相关信号

`SKILL.md` 第 3 步——**Personal-Relevance Signal** 这一项默认给的是「独立开发者/创作者」的模式清单。换成对*你的画像*真正重要的模式。

### 4. Lark 收件人

`SKILL.md` 第 6 步——把 `<YOUR_LARK_OPEN_ID>` 换成你自己的 open_id（可用 `lark-cli contact` 或问你的 Lark 管理员获取）。

### 5. 条数 / 格式 / 归档

`SKILL.md` 第 4 步（条数与挑选规则）、第 5 步（简报模板）、第 8 步（归档路径，默认 `~/Documents/NewsBrief/YYYY-MM-DD.md`）。

---

## 定时运行（可选）

用 macOS LaunchAgent 每天自动跑。新建 `~/Library/LaunchAgents/com.example.newsbrief.plist`（把标签改成你自己的反向域名 id），指向 `scripts/run_brief.sh`，把 `StartCalendarInterval` 设成你想要的时间，然后：

```bash
launchctl load ~/Library/LaunchAgents/com.example.newsbrief.plist
```

在 Linux 上，用 cron 调用 `scripts/run_brief.sh` 是一样的效果。

---

## 它不做什么

- 不带人设语气、不生成脚本、不产出社媒文案。纯粹是综合简报。
- 不发邮件。只通过 Lark 私信送达。
- 不制造虚假紧迫感。新闻淡日 → 只发 5 条并标注「slow cycle」，绝不凑数。
- 不重复推送——严格对 `~/.config/news-brief/seen.json` 做 7 天去重。

---

## 文件说明

- `SKILL.md` — 技能定义 + 运行流程
- `scripts/run_brief.sh` — 定时入口（调用 `claude -p "Run news brief"`，带重试 / 退避）
- `config/sources.example.json` — 视角/信源模板；复制到 `~/.config/news-brief/sources.json`

运行状态存放在 `~/.config/news-brief/`（信源、去重缓存、视角历史、打分日志）。归档在 `~/Documents/NewsBrief/`。

---

## 许可

MIT —— 见 `LICENSE`。
