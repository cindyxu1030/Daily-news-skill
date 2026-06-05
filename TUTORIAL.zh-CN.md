<p align="right"><a href="TUTORIAL.md">English</a> | <strong>中文</strong></p>

# 手把手：搭一个属于你自己的新闻简报 agent

从 clone 到一份「认识你」的每日个性化简报。

---

## 这个适合你吗？

**适合：** 会用 [Claude Code](https://claude.com/claude-code)、愿意敲几行终端命令、想要一份贴着*你的领域*的简报（而不是千篇一律的信息流）。回报：一个 agent 先研究你一次，记住，然后照着你的口味挑。

**不适合：** 只想点一下就收到 AI 新闻、不想碰终端、不用飞书的人。（不用飞书也行——可以改用**邮件**或**本地文件**，见第 4 步——但你确实需要 Claude Code。）

**前置条件：** 装好 Claude Code；一个终端；*可选* 飞书账号 + `lark-cli`（如果你想用飞书推送）。

---

## 第 1 步 — 克隆

```bash
git clone https://github.com/cindyxu1030/Daily-news-skill.git ~/.claude/skills/news-brief
```

## 第 2 步 — 让 agent 认识你（onboarding）

在 Claude Code 里运行：

```
/news-brief
```

第一次没有画像，技能会先给你**做引导**：它会问你愿不愿意提供一段简介 / 一个链接 / 一份笔记（research），再问你几个问题（interview）——你的领域、想每天追的 4–6 个话题、信任谁、会为什么去行动、用哪个渠道送达、用什么语言输出。

然后它把三个文件写到 `~/.config/news-brief/`：
- `profile.md` —— agent 对你的记忆（每次都读）
- `sources.json` —— 你的话题 + 信任的信源
- `settings.json` —— 送达渠道 + 收件人 + 输出语言

检查一下，随时可改。格式见 `config/profile.example.md`。

> **提示：** 想要中文简报？在 `profile.md` 里把「Output language」设成 `中文`（或在 `settings.json` 里设 `output_language`）。整份简报都会用该语言写——即使技能本身的指令是英文的。

## 第 3 步 — 先在本地跑通（dry run）

先别急着配送达，先在自己机器上看输出。要么把 `settings.json` 的 `delivery` 设成 `"file"`，要么：

```bash
NEWSBRIEF_DRY_RUN=1 ~/.claude/skills/news-brief/scripts/run_brief.sh
```

简报会落到 `~/Documents/NewsBrief/YYYY-MM-DD.md`。读一读，调 `profile.md` / `sources.json`，直到挑出来的东西顺眼，再重跑。

随时自检：

```bash
~/.claude/skills/news-brief/scripts/doctor.sh
```

它会告诉你装了什么、配了什么、有没有还没替换的占位符。

## 第 4 步 — 选送达方式

在 `~/.config/news-brief/settings.json` 里设 `delivery`。

### 方式 A — 本地文件（零配置）
`delivery: "file"`。简报只存到 `~/Documents/NewsBrief/`。最简单，什么都不用装。

### 方式 B — 邮件
`delivery: "email"`，填 `email_to`。把 SMTP 凭据放进 `~/.config/news-brief/.env`：

```
NEWSBRIEF_SMTP_USER=you@gmail.com
NEWSBRIEF_SMTP_PASS=你的16位应用专用密码
NEWSBRIEF_SMTP_HOST=smtp.gmail.com
NEWSBRIEF_SMTP_PORT=465
```

Gmail 需要**应用专用密码**（不是账号密码）：myaccount.google.com → 安全 → 两步验证 → 应用专用密码。测试：

```bash
python3 ~/.claude/skills/news-brief/scripts/send_email.py \
  --to you@gmail.com --subject "test" --body-file ~/Documents/NewsBrief/$(date +%F).md
```

### 方式 C — 飞书私信（Lark）

这是门槛最高的一条路，只在你确实用飞书时才折腾。

1. **安装 `lark-cli`** —— 飞书命令行桥。<!-- TODO: 替换成 lark-cli 的官方安装链接/来源 --> 按它自己的文档安装，并确保 `lark-cli` 在你的 `PATH` 里。
2. **配置应用** —— `lark-cli config init`，填入你的飞书应用凭据（在飞书开放平台拿 app id / secret）。
3. **登录授权** —— `lark-cli auth login`。机器人需要权限 **`im:message.send_as_bot`**。
4. **拿到你的 open_id** —— 简报是私信*你*。查自己的 `open_id`：
   ```bash
   lark-cli contact   # 查自己，复制 ou_... 那串 id
   ```
   填进 `settings.json` 的 `lark_open_id`，并把 `delivery` 设成 `"lark"`。
5. **常见报错：**
   - `lark-cli: command not found` → 没装 / 不在 PATH。
   - auth / token 过期 → 重新 `lark-cli auth login`。
   - 发送时 permission denied → 机器人缺 `im:message.send_as_bot`，去开放平台加权限再重新授权。
   - 跑 `./scripts/doctor.sh` 查授权状态、以及是否还留着没替换的 `<YOUR_LARK_OPEN_ID>`。

## 第 5 步 — 设成每天定时

### macOS（LaunchAgent）
新建 `~/Library/LaunchAgents/com.example.newsbrief.plist`（标签改成你自己的反向域名），`ProgramArguments` 指向 `~/.claude/skills/news-brief/scripts/run_brief.sh`，用 `StartCalendarInterval` 设时间。然后：

```bash
launchctl load ~/Library/LaunchAgents/com.example.newsbrief.plist
```

### Linux（cron）
```
0 8 * * *  $HOME/.claude/skills/news-brief/scripts/run_brief.sh
```

用 `NEWSBRIEF_MODEL` 选模型（默认 `sonnet`；想要更深的综合可以 `NEWSBRIEF_MODEL=opus`）。

## 第 6 步 — 持续调优

- 关注点变了就改 `profile.md`，下一份简报立刻跟上。
- 看 `~/.config/news-brief/scoring_log.jsonl`，理解某条*为什么*被选/被丢，再调你的视角和个人相关模式。

---

## 隐私

- **WebSearch** 走的是公开网络搜索。
- onboarding 时你交给 agent 的东西（简介、链接、笔记文件）只用来建画像：链接会被抓取，本地文件在本地读。agent 只读你给的，不会越过你的链接去乱挖。
- `profile.md`、你的配置、缓存、归档全部**留在本地**：`~/.config/news-brief/` 和 `~/Documents/NewsBrief/`。
- 送达只发到*你自己*的渠道（你的飞书、你的邮箱、你的硬盘）。

## 关于「保证」

去重、缓存过期、打分日志都是 agent 每次运行时自己维护的（prompt 驱动），不是数据库强制的。对个人简报来说足够好，但不是确定性软件。想要硬保证，就自己写脚本来管这些缓存文件。
