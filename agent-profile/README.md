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

DeepSeek 的設定 adapter 對應已檢查的 `@deepseek-ai/dsh`：`agent-default-model` 與 `llm-pi-ai.providers` namespace。保留現有 profile 的 plugin 組合，不複製整個套件或 cache。若 Desktop 使用不同 backend，先確認其 `DSH_HOME` 與 plugin schema。

Hermes 保留原有 SOUL 身份，僅更新共用政策區塊。Codex Desktop 與偶爾使用的 CLI 共用相同使用者設定；Desktop 的既有 task 或 CLI 參數仍可能覆寫模型選擇。

安裝與啟動方法見 [BOOTSTRAP.md](../BOOTSTRAP.md)。
