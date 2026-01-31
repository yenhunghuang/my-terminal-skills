# 📖 使用指南

## Claude Skills 詳細說明

### 1. File Organizer
智慧檔案整理系統，自動分類和組織檔案。

**使用範例:**
```bash
claude
> 幫我整理 ~/Downloads 資料夾
> 找出 ~/Documents 中的重複檔案
> 為我的專案資料夾建議更好的結構
```

**功能:**
- 按副檔名自動分類
- 尋找重複檔案
- 建議資料夾結構
- 批量重新命名

---

### 2. UI/UX Pro Max ⭐
專業 UI/UX 設計助手，支援多種前端框架。

**使用範例:**
```bash
claude
> 設計一個現代化的 SaaS 登入頁面
> 建立一個響應式的 pricing section
> 生成一個帶動畫的 hero section
> 設計一個電商產品卡片
```

**支援技術:**
- React + Tailwind CSS
- HTML5 + CSS3
- 響應式設計
- 動畫效果

**最佳實踐:**
- 使用語意化 HTML
- 遵循 accessibility 標準
- 優化效能
- 現代化設計風格

---

### 3. Changelog Generator
從 Git commits 自動生成用戶友好的 changelog。

**使用範例:**
```bash
claude
> 為過去 30 天的 commits 生成 changelog
> 從 v1.0.0 到 v2.0.0 的變更記錄
> 生成本月的發布說明
```

**輸出格式:**
```markdown
# Changelog

## [2.0.0] - 2026-01-31

### Added
- 新增使用者認證功能
- 新增深色模式支援

### Changed
- 改進 API 回應速度

### Fixed
- 修復登入頁面錯誤
```

---

### 4. Document Skills
文件處理工具集，支援多種格式。

**支援格式:**
- PDF - 解析、合併、註釋
- Word (DOCX) - 編輯、格式化
- Excel (XLSX) - 資料處理
- PowerPoint (PPTX) - 簡報編輯

**使用範例:**
```bash
claude
> 從這個 PDF 提取文字
> 合併這些 Word 文件
> 分析這個 Excel 檔案的數據
```

---

## GitHub Copilot Customizations 詳細說明

### 1. Conventional Commit
遵循 Conventional Commits 規範的 commit 訊息。

**格式:**
```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Type 類型:**
- `feat`: 新功能
- `fix`: Bug 修復
- `docs`: 文件更新
- `style`: 程式碼格式（不影響功能）
- `refactor`: 重構
- `test`: 測試相關
- `chore`: 建置或工具變更

**範例:**
```bash
# VS Code 中
/conventional-commit

# 輸出:
feat(auth): add OAuth2 login support

Implemented OAuth2 authentication flow with Google and GitHub providers.
Added user session management and token refresh logic.

Closes #123
```

---

### 2. Git Flow Branch Creator
自動化 Git Flow 分支管理。

**分支類型:**
- `feature/` - 新功能開發
- `bugfix/` - Bug 修復
- `hotfix/` - 緊急修復
- `release/` - 發布準備

**使用範例:**
```bash
# VS Code 中
/git-flow-branch-creator

# 輸入:
Type: feature
Name: user-authentication

# 自動執行:
git checkout -b feature/user-authentication
```

---

### 3. GitHub Actions Expert
GitHub Actions CI/CD 專家代理。

**功能:**
- 建立工作流程
- 優化 CI/CD pipeline
- 故障排除
- 安全性檢查

**使用範例:**
```bash
# 建立 Node.js CI workflow
@github-actions-expert 建立一個 Node.js CI workflow

# 優化現有 workflow
@github-actions-expert 優化這個 workflow 的執行時間
```

---

### 4. CI/CD Best Practices
GitHub Actions CI/CD 最佳實踐指南。

**包含內容:**
- 自動化測試策略
- 部署流程優化
- 安全性最佳實踐
- 效能優化技巧
- 監控和日誌

**範例 Workflow:**
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: npm test
      
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: ./deploy.sh
```

---

## 組合使用範例

### 場景 1: 建立新功能
```bash
# 1. 建立分支
/git-flow-branch-creator
Type: feature
Name: user-dashboard

# 2. 開發功能（使用 UI/UX Pro Max）
claude
> 設計一個使用者儀表板

# 3. Commit 變更
/conventional-commit
feat(dashboard): add user dashboard with analytics

# 4. 生成 Changelog
claude
> 為這次功能更新生成 changelog
```

### 場景 2: 整理專案
```bash
# 1. 整理檔案
claude
> 整理專案目錄，移除無用檔案

# 2. 更新文件
claude
> 使用 document-skills 更新 README

# 3. 建立 CI/CD
@github-actions-expert 建立測試和部署 workflow
```

---

## 快捷鍵和技巧

### Claude Code
```bash
# 快速啟動
alias c='claude'

# 常用提示詞別名
alias organize='claude -p "幫我整理當前目錄"'
alias design='claude -p "設計一個 UI 組件"'
```

### VS Code
- `Cmd/Ctrl + I`: 開啟 Copilot Chat
- `/` + Tab: 自動完成 slash 命令
- `Cmd/Ctrl + Shift + P`: 命令面板

---

## 故障排除

### Claude Skills 沒有載入
```bash
# 檢查安裝路徑
ls -la ~/.config/claude-code/skills/

# 重新安裝
cd ~/my-terminal-skills
./scripts/install.sh
```

### Copilot Customizations 無效
```bash
# 檢查安裝
ls -la ~/.github/copilot/

# 重啟 VS Code
# 檢查 Copilot 是否已登入
```

---

## 更多資源

- [Claude Documentation](https://docs.anthropic.com/)
- [GitHub Copilot Docs](https://docs.github.com/copilot)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
