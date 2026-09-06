# 在新電腦重建 CLI coding agent 環境

這個 repository 保存可重現的指令、skills、快捷指令、介面偏好、模型選擇和 gateway 設定格式。支援 macOS、Linux、WSL，以及原生 Windows 的 PowerShell 入口。各 CLI 仍保有自己的內建工具和系統 prompt；相同設定不代表不同產品或模型會輸出相同結果。

## 1. 安裝需要的 CLI

先安裝 Git、[uv](https://docs.astral.sh/uv/getting-started/installation/)，以及要使用的 CLI。安裝器會鎖定自己的 Python 相依套件，但不會偷偷安裝或升級全部 CLI。只裝你會用到的工具即可。

| 工具 | 官方安裝入口／方式 |
|---|---|
| Codex | [官方 CLI](https://developers.openai.com/codex/cli/)；`npm install -g @openai/codex` |
| Claude Code | [原生安裝](https://code.claude.com/docs/en/setup)；macOS 可用 `brew install --cask claude-code` |
| Copilot | [官方安裝](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli)；`npm install -g @github/copilot` |
| Gemini | [官方安裝](https://geminicli.com/docs/get-started/installation/)；`npm install -g @google/gemini-cli` |
| Pi | [Pi](https://github.com/earendil-works/pi)；此 profile 的來源機使用 `@earendil-works/pi-coding-agent` |
| Oh My Pi | [官方 README](https://github.com/can1357/oh-my-pi) |
| OpenCode | [官方安裝](https://opencode.ai/docs/) |
| Hermes | [官方 README](https://github.com/NousResearch/hermes-agent)；不支援的原生 Windows 功能請在 WSL 執行 |

npm 安裝使用符合各 CLI 要求的 Node.js 版本；Copilot 文件要求 Node.js 22 以上。不同機器若需要嚴格重現版本，額外固定各 CLI 版本；不要將同名模型在不同 provider 的行為視為相同。

## 2. 初始化設定

macOS、Linux、WSL：

```sh
git clone https://github.com/yenhunghuang/my-terminal-skills.git
cd my-terminal-skills
./scripts/install.sh init
```

原生 Windows PowerShell：

```powershell
git clone https://github.com/yenhunghuang/my-terminal-skills.git
Set-Location my-terminal-skills
.\scripts\install.ps1 init
```

若組織 PowerShell policy 不允許執行 `.ps1`，不用修改全域 policy，可直接使用等效命令：

```powershell
uv run --locked python scripts/profile/manage.py init
```

這會建立使用者家目錄下的 `.config/terminal-agents/machine.json`。它不在 repository 裡。WSL 的 Linux home 和 Windows 的使用者 home 是兩套環境；在哪一邊使用 CLI，就在哪一邊安裝與登入。

## 3. 填入這台機器的連線資料

編輯 `~/.config/terminal-agents/machine.json`（Windows 為 `$HOME\.config\terminal-agents\machine.json`）：

- `custom_gateway.enabled`：啟用時，為 Pi、Oh My Pi、OpenCode、Hermes 設定相同的 OpenAI Chat Completions gateway。
- `custom_gateway.base_url`：你的 HTTPS API base URL，含 `/v1`（若 gateway 的 base path 不同，使用實際 path）。遠端 gateway 不是新電腦的 `localhost`。
- `custom_gateway.models`：填入 gateway 真正接受的 ID。範例提供 GLM-5.3 Flash、DeepSeek V4 Flash 的來源機 ID；DeepSeek V4 Pro 的精確 ID 需由 gateway 確認後加入，不猜 alias。
- `contextWindow`、`maxTokens`：可填在各 model 中，使用 gateway metadata 的數值。未填時 Pi／OMP／OpenCode 可能採用自己的預設，doctor 會提醒。
- `default_model`：必須是 models 內的其中一個 ID。
- `cliproxy`：供 Claude／Copilot 的專用 wrapper 使用。base URL 保持 loopback origin，例如 `http://127.0.0.1:8317`。遠端 CLIProxy 可先用 SSH port forwarding 建立本機 tunnel。
- `cliproxy.context_window_tokens`、`max_output_tokens`：使用選定 GPT 模型的實際 metadata；未填時 wrapper 會停止，不套用別款模型的 token limits。
- `overrides`：以 `codex`、`claude`、`copilot`、`gemini`、`opencode`、`pi`、`omp`、`hermes` 為 key，填原生 settings 格式的局部覆寫。可放這台機器已安裝的 MCP command、theme 或不同預設模型。不要把實際金鑰放進 overrides。

模板不會搬運舊電腦的 Pencil 執行檔路徑、VS Code 連線狀態、statusline script、shell alias、OAuth、聊天紀錄或 permission bypass 設定。需要的本機 integration 先安裝，再放到 overrides；既有目標機的其他設定會保留。

## 4. 安裝 profile

macOS、Linux、WSL：

```sh
./scripts/install.sh install --agents codex,claude,copilot,gemini,opencode,pi,omp,hermes
./scripts/install.sh install --agents codex,claude,copilot,gemini,opencode,pi,omp,hermes --apply
export PATH="$HOME/.local/bin:$PATH"
```

PowerShell：

```powershell
.\scripts\install.ps1 install --agents codex,claude,copilot,gemini,opencode,pi,omp,hermes
.\scripts\install.ps1 install --agents codex,claude,copilot,gemini,opencode,pi,omp,hermes --apply
$env:Path = "$HOME\.local\bin;$env:Path"
```

第一個命令預覽，第二個寫入並備份。只使用部分 CLI 時縮短 `--agents` 清單。安裝器不會啟動模型或把 API key 寫進參數。PATH 範例只影響目前 session；如要永久生效，可將這一個 PATH 變更放入自己的 shell profile。

安裝器使用各工具的預設使用者路徑。自訂 `CODEX_HOME`、`HERMES_HOME`、`PI_CODING_AGENT_DIR`、`COPILOT_HOME` 或 named profiles 不會自動重定位；在那種環境請先清楚選擇要安裝的 profile，依 [路徑表](agent-profile/README.md)手動套用，避免寫到錯誤位置。`--home` 指整個目標帳戶 home，不是單一 CLI 的 home。

指令在 managed block 內更新，保留其他個人內容。JSON/TOML/YAML 合併只覆寫 profile 管理的欄位；同名 skill 將由這份 profile 管理，原內容會備份。macOS/Linux 使用 skill 符號連結，Windows 使用檔案副本，不需要 symlink 管理員權限。對於已存在的「父目錄 symlink」，安裝器會指出衝突而不沿連結覆寫外部目錄。

## 5. 登入與金鑰

原生模式使用各 CLI 的正常登入流程：Codex 登入 ChatGPT、Copilot 登入 GitHub、Claude 登入 Anthropic、Gemini 登入 Google；Pi/OMP/OpenCode/Hermes 依你選用的 provider 完成登入。

macOS/Linux/WSL 的自接 gateway 金鑰可用隱藏輸入保存：

```sh
agent-run secret TERMINAL_AGENTS_GATEWAY_KEY
agent-run secret TERMINAL_AGENTS_CLIPROXY_KEY
```

只儲存在 `~/.config/terminal-agents/secrets.json`，權限 0600。也可使用密碼管理器提供的 process environment variable。

原生 Windows 不使用 POSIX 權限的 secrets.json。請從密碼管理器提供環境變數，或以 PowerShell 隱藏輸入建立當前 session 的變數，例如：

```powershell
$Credential = Get-Credential -UserName gateway -Message 'API key 請輸入 Password 欄位'
$env:TERMINAL_AGENTS_GATEWAY_KEY = $Credential.GetNetworkCredential().Password
Remove-Variable Credential
```

CLIProxy 的金鑰同樣設定到 `TERMINAL_AGENTS_CLIPROXY_KEY`。不要把值寫進 shell 歷史或 Git。

## 6. 平常怎麼使用

```sh
codex                         # 原生 ChatGPT/Codex 路由
copilot                       # 原生 GitHub 路由，預設 Sol
claude-via-cliproxy            # 本機 CLIProxy，預設 Sol，子代理繼承
copilot-via-cliproxy           # 本機 CLIProxy 的 Responses 路由
agent-run pi                  # 注入該 gateway 需要的環境變數後啟動
agent-run omp
agent-run opencode
agent-run hermes
agent-run gemini               # 保留 Gemini 原生模型與登入
```

每個 launcher 會原樣傳递額外 CLI 參數，例如 `agent-run pi -- --help`。原生 Windows `.cmd` launcher 會透過 Python 啟動 native executable 或已識別的 npm JavaScript entry，不用 `cmd /c` 拼接模型 prompt。Hermes/OMP 的 binary 發行支援依各專案而定，找不到支援的 entry 時會明確停止；可改在 WSL 執行。

直接執行 `pi` 等原生命令也會讀到已安裝 settings；若金鑰只存於本套件的 secrets.json，請用 `agent-run` 注入，或由密碼管理器輸出同名環境變數。

## 7. 驗證、更新、還原

```sh
./scripts/install.sh doctor --agents codex,claude,copilot,pi
agent-run probe custom
agent-run probe cliproxy
./scripts/update.sh --agents codex,claude,copilot,pi --apply
./scripts/install.sh restore --manifest /path/printed/by/install/manifest.json
```

PowerShell 使用 `install.ps1 doctor`、`update.ps1 --apply` 和 `install.ps1 restore --manifest ...`。

`doctor` 檢查程式是否在 PATH、設定與檔案是否漂移；缺 binary 或檔案差異時回傳非零。`probe` 只做具認證的 `/models` catalog 查詢，不做付費推論，也不將 catalog 可見誤當成串流、工具呼叫、子代理 routing 已驗證。首次登入後，請用一個無副作用的小任務確認想用的能力。

安裝器備份位於 `~/.local/state/terminal-agents/<install-id>/`。還原只還原該次改動；若之後又手動編輯過檔案，會停止保護那些改動。多次更新需依反向順序還原。備份可能含原本私人設定，請只留在本機。

## 給另一個 coding agent 的指令

> 閱讀此 repository 的 BOOTSTRAP.md。在目前電腦安裝我選用的 CLI profile，沿用既有登入與其他設定。先執行 init；請我補上缺少的 gateway URL、實際模型 ID 與必要 token metadata，金鑰使用私密輸入或環境變數。完成 install、doctor，回報缺少的 binary、登入或未驗證能力。不要上傳 machine.json、secrets.json 或 backups。
