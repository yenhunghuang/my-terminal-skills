# My Terminal Skills

個人 CLI coding agents 的共用指令、skills 與快捷指令。

## 最新：精簡 agent profile

[agent-profile/](agent-profile/) 收錄目前使用的精簡版：

- [共用 AGENTS.md](agent-profile/AGENTS.md)：以任務需要決定流程，減少固定步驟、persona orchestration 和重複驗證。
- [4 個 skills](agent-profile/skills/)：agent instruction refactor、CLIProxy coding agents、PDF、UI/UX。
- [17 個 Claude 快捷指令](agent-profile/claude/commands/sc/)：保留 `/sc:*` 名稱，以簡短任務描述取代舊 SuperClaude 流程。
- [Hermes SOUL.md](agent-profile/hermes/SOUL.md)：保留身份描述並套用相同工作偏好。

模型偏好為 GPT-5.6 Luna/Sol、GPT-6 Astra、自接 GLM-5.3 Flash、DeepSeek V4 Flash/Pro；子代理預設繼承主模型。模型連線及 provider 設定不包含在 repository 中。

請依 [profile 放置說明](agent-profile/README.md) 設定 Codex、Claude、Copilot、Gemini、OpenCode、Pi、Oh My Pi 或 Hermes。

```bash
git clone https://github.com/yenhunghuang/my-terminal-skills.git
cd my-terminal-skills
```

## 舊版收藏

`claude-skills/`、`copilot-customizations/`、`QUICKSTART.md`、`docs/USAGE.md` 與 `scripts/` 保留為舊版內容。舊安裝腳本不會安裝新版 `agent-profile/`，其路徑與 CLI 用法亦未在此次更新中驗證；新版請使用上述放置說明。

來源保留：

- [awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)
- [awesome-copilot](https://github.com/github/awesome-copilot)
- [ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
