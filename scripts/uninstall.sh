#!/bin/bash

echo "🗑️  解除安裝 Terminal Skills..."
echo ""

read -p "確定要解除安裝嗎? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "取消解除安裝"
    exit 0
fi

# 移除 Claude Skills
rm -rf "$HOME/.config/claude-code/skills/file-organizer"
rm -rf "$HOME/.config/claude-code/skills/changelog-generator"
rm -rf "$HOME/.config/claude-code/skills/document-skills"
rm -rf "$HOME/.config/claude-code/skills/ui-ux-pro-max"

# 移除 Copilot Customizations
rm -f "$HOME/.github/copilot/conventional-commit.prompt.md"
rm -f "$HOME/.github/copilot/git-flow-branch-creator.prompt.md"
rm -f "$HOME/.github/copilot/github-actions-expert.agent.md"
rm -f "$HOME/.github/copilot/github-actions-ci-cd-best-practices.instructions.md"

echo "✅ 解除安裝完成"
