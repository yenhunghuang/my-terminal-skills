# My Terminal Skills

在其他電腦重建個人的 CLI coding agent 工作環境：共用指令、4 個 skills、17 個 Claude 快捷指令、八個 CLI 的 settings，以及自接模型路由。

**新電腦請從 [BOOTSTRAP.md](BOOTSTRAP.md) 開始。** 支援 macOS／Linux／WSL 與 Windows PowerShell；可只安裝選定工具的 profile。

```sh
git clone https://github.com/yenhunghuang/my-terminal-skills.git
cd my-terminal-skills
./scripts/install.sh init
# 在 ~/.config/terminal-agents/machine.json 填入這台機器的 gateway 設定
./scripts/install.sh install --apply
./scripts/install.sh doctor
```

Windows 使用 `scripts/install.ps1` 執行相同子命令。這些命令安裝設定；各 CLI binary 和帳號登入依 [bootstrap 說明](BOOTSTRAP.md)準備。

## 包含內容

- [agent-profile/AGENTS.md](agent-profile/AGENTS.md)：最小共用工作原則。
- [agent-profile/settings/](agent-profile/settings/)：Codex、Claude、Copilot、Gemini、OpenCode、Pi、Oh My Pi、Hermes 設定片段。
- [agent-profile/skills/](agent-profile/skills/)：instruction refactor、CLIProxy、PDF、UI/UX。
- [Claude 快捷指令](agent-profile/claude/commands/sc/)與 [Hermes 身份範本](agent-profile/hermes/SOUL.md)。
- 安裝、預覽、備份、還原、doctor；`agent-run` 與 Claude／Copilot 的 CLIProxy wrapper。
- macOS／Linux／Windows 的隔離測試 workflow；測試不使用真實憑證或付費推論。

模型偏好為 GPT-5.6 Luna/Sol、GPT-6 Astra、自接 GLM-5.3 Flash、DeepSeek V4 Flash/Pro。子代理預設繼承主模型。各 CLI 仍有不同內建行為；Gemini 保留原生模型。自接模型的完整 ID、可用性和 token limits 由你的 gateway 決定。

金鑰、OAuth、私人 gateway URL、本機 MCP 路徑與聊天紀錄不進 Git。設定安裝會保留無關欄位；首次連線仍須在新電腦登入或提供金鑰。

## 開發驗證

```sh
uv run --locked python -m unittest discover -s tests -v
```

## 舊版收藏

`claude-skills/`、`copilot-customizations/` 和 `docs/USAGE.md` 保留舊版收藏；新版安裝器僅管理 `agent-profile/`，不會自動安裝舊版內容。

來源：[awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)、[awesome-copilot](https://github.com/github/awesome-copilot)、[ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)。
