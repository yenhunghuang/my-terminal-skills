# 精簡 CLI agent profile

以模型能力與任務需求決定流程，保留必要的使用者偏好和操作限制。模型偏好：GPT-5.6 Luna/Sol、GPT-6 Astra、自接 GLM-5.3 Flash、DeepSeek V4 Flash/Pro。這些名稱描述偏好，並不建立 provider、API key 或切換實際模型。

## 內容

- [AGENTS.md](AGENTS.md)：共用全域原則；子代理預設繼承主模型。
- [skills/](skills/)：4 個個人 skills，包含必要 references、腳本與原有授權檔。
- [claude/commands/sc/](claude/commands/sc/)：17 個精簡快捷指令，保留 `/sc:*` 名稱。
- [hermes/SOUL.md](hermes/SOUL.md)：Hermes 身份描述與相同全域偏好。

## 可攜式設定與安裝

[settings/](settings/) 包含八個 CLI 的原生設定片段；[machine.example.json](machine.example.json) 提供每台機器的 gateway 參數格式。安裝、Windows／WSL、登入、金鑰、驗證和還原請依 [BOOTSTRAP.md](../BOOTSTRAP.md)。

## 放置位置

先備份目標檔案；有既有個人規則時合併內容。以下路徑均以預設使用者 profile 為例，自訂 home 或 named profile 應改用其實際路徑。

| 工具 | 共用 AGENTS.md 的全域入口 |
|---|---|
| Codex | `~/.codex/AGENTS.md`，或 `$CODEX_HOME/AGENTS.md` |
| Claude Code | `~/.claude/CLAUDE.md` |
| Copilot CLI | `~/.copilot/copilot-instructions.md` |
| Gemini CLI | `~/.gemini/GEMINI.md` |
| OpenCode | `~/.config/opencode/AGENTS.md` |
| Pi | `~/.pi/agent/AGENTS.md` |
| Oh My Pi | `~/.omp/agent/AGENTS.md` |

將共用原則放入各工具的原生入口；可以複製，也可以用指向同一穩定位置的符號連結。不要只留下普通 Markdown 連結並假設所有 CLI 都會自動展開。

Hermes 使用 `hermes/SOUL.md` 的內容合併到 `~/.hermes/SOUL.md`；保留自己已有的身份描述。它是獨立內容副本，更新共用原則時需同步。

Skills 可放入 Codex 的 `~/.agents/skills/<name>/` 或 Claude 的 `~/.claude/skills/<name>/`。本機 Codex 既有 skills 也可繼續維護於 `~/.codex/skills/`，再以符號連結暴露到支援的 discovery 目錄。只安裝需要的 skills，避免相同名称的不同副本。

Claude 快捷指令放入 `~/.claude/commands/sc/`。替換舊 SuperClaude 時，把舊 `CLAUDE.md` 的八份 framework imports 移除；不必把舊 persona、wave、固定品質關卡再搬回入口。

重新啟動 CLI session 以載入全域指令。實際執行檔、支援模型及帳號權限應以本機 CLI 為準。

## 模型設定

Markdown 只提供行為偏好。需調整實際模型時，使用各工具的 model 設定；保留 gateway 原本的完整 model ID、provider 和 token limits。

- Copilot 支援的 `subagents.agents.<name>.model` 可設為 `inherit`；使用前確認已安裝版本的 `copilot help config`。
- CLIProxy wrapper 的 fast/subagent 預設應取自主模型；保留明確的環境變數 override。
- Luna、Flash 不代表應該排除或降級；它們也是此 profile 指定的模型選項。

## 來源與打包差異

本目錄保存個人精簡版，不是官方 CLI 系統 prompt。PDF skill 保留原有 [Apache-2.0 授權檔](skills/pdf/LICENSE.txt)，其工作流程文字已精簡。UI skill 沿用 ui-ux-pro-max 的識別名稱，改為模型直接做設計判斷；匯出時省略原安裝中無法執行的 `scripts` / `data` 路徑占位檔，並調整說明。

此 profile 包含可攜式 settings 與 provider 產生邏輯；不包含 OAuth、API keys、私人 gateway 位址、session、歷史紀錄、舊電腦的絕對路徑或備份。
