# Personal Agent Profile

在不同電腦重建個人 agent 工作環境，以精簡指令與原生能力為主。

| 用途 | 工具 | 安裝器名稱 |
|---|---|---|
| Coding | Pi | `pi` |
| Coding | Oh My Pi | `omp` |
| Coding（主力） | Codex Desktop；偶爾使用 CLI | `codex` |
| Coding | DeepSeek Harness Desktop | `dsh` |
| 助手 | Hermes Desktop | `hermes` |

目前只維護這五個工具。包含共用 AGENTS.md、原生設定片段、Hermes 身份、3 個 skills（指令精簡、PDF、UI/UX），以及可預覽、備份、還原的跨平台安裝器。

**新電腦從 [BOOTSTRAP.md](BOOTSTRAP.md) 開始。** 設定安裝支援 macOS、Linux、Windows PowerShell 與 WSL；Desktop 程式依該版本提供的平台安裝，Windows 與 WSL 分別管理設定。

```sh
git clone https://github.com/yenhunghuang/my-terminal-skills.git
cd my-terminal-skills
./scripts/install.sh init
./scripts/install.sh install --apply
```

Windows 使用 `scripts/install.ps1` 的相同子命令。套件安裝設定，不代替程式安裝或帳號登入。Desktop 與 CLI 的啟動方式見 [BOOTSTRAP.md](BOOTSTRAP.md)。

模型偏好：GPT-5.6 Luna/Sol、GPT-6 Astra、自接 GLM-5.3 Flash、DeepSeek V4 Flash/Pro。保留實際 provider 與 model ID；子代理預設繼承主模型，按任務選用規劃、委派與驗證，不強加固定流程。

私人 gateway URL、金鑰、OAuth、聊天紀錄與機器專屬路徑留在本機。不同 agent 的原生工具與系統指令仍會影響行為。

開發驗證：`uv run --locked python -m unittest discover -s tests -v`。CI 在 macOS、Linux、Windows 執行隔離測試，不使用真實憑證或模型推論。
