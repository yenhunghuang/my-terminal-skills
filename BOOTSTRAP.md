# 在新電腦重建個人 agent 環境

Coding 工具限定 Pi、Oh My Pi、Codex Desktop（主力，CLI 偶爾）、DeepSeek Harness Desktop；Hermes Desktop 用作助手。設定安裝支援 macOS、Linux、原生 Windows 與 WSL。Desktop 程式的可用平台依你安裝的版本；設定測試通過不代表每個 GUI 已在每個平台驗證。

## 準備程式

先準備 Git、[uv](https://docs.astral.sh/uv/getting-started/installation/)，再安裝會使用的程式。安裝器不會自動安裝或升級 agent。

- Codex：優先使用 Desktop；需要 terminal 時另外安裝 CLI。
- Pi、Oh My Pi：安裝原生 CLI，確認 `pi`、`omp` 在 PATH。
- DeepSeek Harness Desktop：使用你的 Desktop 發行版及配套 backend；本套件對應 `.dsh` 設定格式，不替換 profile 的 plugin bundles。
- Hermes Desktop：使用你的 Desktop 發行版與其實際 `.hermes` backend home。

## 初始化與安裝

macOS／Linux／WSL：

```sh
git clone https://github.com/yenhunghuang/my-terminal-skills.git
cd my-terminal-skills
./scripts/install.sh init
./scripts/install.sh install --agents codex,pi,omp,dsh,hermes
./scripts/install.sh install --agents codex,pi,omp,dsh,hermes --apply
export PATH="$HOME/.local/bin:$PATH"
```

Windows PowerShell：

```powershell
git clone https://github.com/yenhunghuang/my-terminal-skills.git
Set-Location my-terminal-skills
.\scripts\install.ps1 init
.\scripts\install.ps1 install --agents codex,pi,omp,dsh,hermes
.\scripts\install.ps1 install --agents codex,pi,omp,dsh,hermes --apply
$env:Path = "$HOME\.local\bin;$env:Path"
```

若 PowerShell policy 不允許 `.ps1`，使用 `uv run --locked python scripts/profile/manage.py init` 等效入口，不需修改全域 policy。`install` 預覽，`--apply` 寫入並備份。`--agents` 可以縮短，省略則套用五個工具。

`init` 建立 `~/.config/terminal-agents/machine.json`。`--home` 指整個帳戶 home，不是單一 agent 的 home。安裝器使用[預設路徑](agent-profile/README.md)；自訂 `CODEX_HOME`、`HERMES_HOME`、`DSH_HOME`、Pi/OMP home 或 named profiles 請依表格手動套用到實際目錄。

Windows Desktop 使用 Windows home；WSL terminal 使用 Linux home，兩邊分別安裝與登入。若 Desktop 接到 WSL／遠端 backend，政策與模型設定要放在 backend 實際讀取的位置。不要把 Windows 執行檔路徑直接當成 WSL 路徑。

## 模型與本機設定

編輯本機 `machine.json`：

- `custom_gateway.enabled`：啟用時為 Pi、OMP、DeepSeek Harness、Hermes 配置 OpenAI Chat Completions gateway；關閉時保留既有路由。
- `base_url`、`key_env`：實際 HTTPS API base URL 與金鑰環境變數名稱。只有 loopback 可使用 HTTP。填名稱，不填金鑰值。
- `models`、`default_model`：使用 gateway 接受的精確 ID。範本提供來源機曾使用的 GLM-5.3 Flash 與 DeepSeek V4 Flash ID；Pro 等其他 ID 由你的 gateway 確認後加入。
- `contextWindow`、`maxTokens`：有可靠 metadata 才填；缺省時 adapter 可能使用自己的預設。
- `thinkingLevelMap`：僅填已確認的模型 thinking 等級與 wire 值。DeepSeek adapter 將非 null 條目轉為 `reasoningEfforts`；未提供時保留其 catalog／provider 行為，不推測支援程度。
- `overrides`：以 `codex`、`pi`、`omp`、`dsh`、`hermes` 為 key 的原生 settings 片段，可設定已安裝的 MCP、介面或模型偏好。
- `desktop_commands`：以 `codex`、`dsh`、`hermes` 為 key 的啟動參數陣列，第一項為實際 executable，後面為各別參數。macOS 的標準 Codex.app／Hermes.app 可自動找到；其他位置與平台需填入。Windows 使用 `.exe`，不使用 `.cmd`／`.bat` 作為 Desktop entry。

例如將 `desktop_commands.hermes` 設為 `["C:\\Apps\\Hermes\\Hermes.exe"]`，但必須換成該機器真正存在的路徑。若你的 DeepSeek Desktop 由特定啟動器開啟，使用該啟動器的 executable 與參數；本套件不把 `dsh web` 自動當成你的 Desktop。

既有目標機的其他設定、登入與身份會保留。同名 skill 由本套件管理並先備份。POSIX 使用 symlink，Windows 使用副本；父目錄為 symlink 時會指出衝突。先關閉會寫入同一份設定的 app，再套用更新。

## 登入與金鑰

Codex 在新電腦登入原生帳號；其他工具依選用 provider 完成登入。Desktop 可使用自己的金鑰管理介面，金鑰名稱須對應 settings 中的引用。

POSIX 的 launcher 可使用隱藏輸入保存金鑰：

```sh
agent-run secret TERMINAL_AGENTS_GATEWAY_KEY
```

儲存在本機 `~/.config/terminal-agents/secrets.json`，權限 0600；或由密碼管理器提供環境變數。Windows 原生 launcher 使用 process environment，例如：

```powershell
$Credential = Get-Credential -UserName gateway -Message 'API key 請輸入 Password 欄位'
$env:TERMINAL_AGENTS_GATEWAY_KEY = $Credential.GetNetworkCredential().Password
Remove-Variable Credential
```

`agent-run` 只把變數交給新啟動的程序。已在執行的 Desktop 不會因此取得新變數；先完全退出再啟動。從圖示直接開啟時，本套件不會注入 secrets.json，請使用 app 原生憑證或該程序環境。Hermes 若另有獨立／遠端 backend，金鑰需在 backend 設定。

## 平常使用、更新與還原

```sh
agent-run codex                 # Codex Desktop
agent-run codex-cli             # 偶爾使用 CLI，共用 Codex 設定
agent-run pi
agent-run omp
agent-run dsh                   # 已配置的 DeepSeek Harness Desktop entry
agent-run hermes                # Hermes Desktop 助手
./scripts/install.sh doctor
agent-run probe custom
./scripts/update.sh --apply
./scripts/install.sh restore --manifest /path/printed/by/install/manifest.json
```

PowerShell 對應 `install.ps1`／`update.ps1`。額外參數會傳給所選程式；原生命令也讀取已安裝設定。

`doctor` 檢查設定漂移，以及 Pi/OMP 的 CLI 或 Desktop 啟動 entry；不要求 Codex Desktop 使用者另裝 CLI。未配置 Desktop entry 或檔案漂移會回傳非零，這不等於程式不存在。`probe custom` 僅查詢 gateway 的模型 catalog，不宣稱推論、串流或工具呼叫已通過。

備份位於 `~/.local/state/terminal-agents/<install-id>/`。還原若發現安裝後的手動編輯會停止；多次更新依反向順序還原。舊版本曾裝入的範圍外設定不會自動刪除，避免損失你另行維護的內容；本版不再新增或管理它們。

## 給另一個 agent 的指令

> 閱讀 BOOTSTRAP.md，安裝我選用的五個工具 profile。Codex 以 Desktop 為主，Hermes 是助手。沿用既有登入，確認 Windows／WSL 與 backend 的設定位置。完成 init、install、doctor；只有缺少實際連線資料時才詢問。不要上傳 machine.json、secrets.json 或備份。
