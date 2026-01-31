#!/bin/bash

echo "🔄 更新 Terminal Skills..."
echo ""

# 拉取最新變更
git pull origin main

# 重新執行安裝
./install.sh
