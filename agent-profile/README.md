# Portable profile

共用政策位於 [AGENTS.md](AGENTS.md)，安裝器依原生載入路徑套用：

| 工具 | 指令 | 設定 | Skills |
|---|---|---|---|
| Codex Desktop／CLI | `~/.codex/AGENTS.md` | `~/.codex/config.toml` | `~/.agents/skills` |
| Pi | `~/.pi/agent/AGENTS.md` | `~/.pi/agent/settings.json`、`models.json` | `~/.pi/agent/skills` |
| Oh My Pi | `~/.omp/agent/AGENTS.md` | `~/.omp/agent/config.yml`、`models.yml` | `~/.omp/agent/skills` |
| DeepSeek Harness Desktop | `~/.dsh/AGENTS.md` | `~/.dsh/settings.yaml` | `~/.dsh/skills` |
| Hermes Desktop（助手） | `~/.hermes/SOUL.md` | `~/.hermes/config.yaml` | `~/.hermes/skills` |

以上為預設 home；Windows 的 `~` 指 Windows 使用者目錄，WSL 指 Linux home。自訂 home、遠端 backend 或 named profile 需要套用至實際讀取位置。

本人的 Pi／OMP 在 WSL Ubuntu，Codex 在 Windows 與 WSL 分別管理。Windows Hermes Desktop 的實際 home 為 `%LOCALAPPDATA%/hermes`；安裝器不會自動偵測此位置，也不可用 `--home` 指向單一 backend 目錄。手動套用時，先備份該目錄的 `SOUL.md`、`config.yaml` 與同名 skills，再合併本套件內容，保留登入與原有身份。

DeepSeek 的設定 adapter 對應已檢查的 `@deepseek-ai/dsh`：`agent-default-model` 與 `llm-pi-ai.providers` namespace。保留現有 profile 的 plugin 組合，不複製整個套件或 cache。若 Desktop 使用不同 backend，先確認其 `DSH_HOME` 與 plugin schema。

Hermes 的 [SOUL.md](hermes/SOUL.md) 僅提供新安裝的預設身份；共用政策統一來自 [AGENTS.md](AGENTS.md)，安裝器保留原有身份，僅更新標記內的政策。手動套用也使用此單一政策來源。Codex Desktop 與偶爾使用的 CLI 共用相同使用者設定；Desktop 的既有 task 或 CLI 參數仍可能覆寫模型選擇。

安裝與啟動方法見 [BOOTSTRAP.md](../BOOTSTRAP.md)。
