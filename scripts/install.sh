#!/bin/bash

echo "🚀 開始安裝 Terminal Skills..."
echo ""

# 顏色定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. 安裝 Claude Skills
echo "${BLUE}📦 安裝 Claude Code Skills...${NC}"
CLAUDE_DIR="$HOME/.config/claude-code/skills"
mkdir -p "$CLAUDE_DIR"

cp -r ../claude-skills/* "$CLAUDE_DIR/" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "${GREEN}✓ Claude Skills 已安裝到: $CLAUDE_DIR${NC}"
    ls "$CLAUDE_DIR"
else
    echo "⚠️  Claude Skills 安裝失敗"
fi

echo ""

# 2. 安裝 GitHub Copilot Customizations
echo "${BLUE}📦 安裝 GitHub Copilot Customizations...${NC}"
COPILOT_DIR="$HOME/.github/copilot"
mkdir -p "$COPILOT_DIR"

cp -r ../copilot-customizations/* "$COPILOT_DIR/" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "${GREEN}✓ Copilot Customizations 已安裝到: $COPILOT_DIR${NC}"
    ls "$COPILOT_DIR"
else
    echo "⚠️  Copilot Customizations 安裝失敗"
fi

echo ""
echo "${GREEN}✅ 安裝完成！${NC}"
echo ""
echo "使用方法:"
echo "  Claude Code: 執行 'claude' 命令"
echo "  GitHub Copilot: 在 VS Code 中使用或執行 'gh copilot'"
echo ""
echo "請重啟終端或執行: source ~/.zshrc"
