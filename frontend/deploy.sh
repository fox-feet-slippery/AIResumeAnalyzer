#!/bin/bash

# 前端部署脚本

echo "🚀 部署前端到GitHub Pages..."

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "📥 安装依赖..."
    npm install
fi

# 构建生产版本
echo "🔨 构建生产版本..."
npm run build

# 部署到GitHub Pages
echo "📤 部署到GitHub Pages..."
npm run deploy

echo "✅ 前端部署完成！"
echo "🌐 访问地址：https://<your-github-username>.github.io/<repository-name>"
