#!/bin/bash
###
 # @Author: xiaohao
 # @Date: 2026-03-03 21:15:03
 # @LastEditors: xiaohao
 # @LastEditTime: 2026-03-03 21:15:06
 # @FilePath: \Sidereus笔试\deploy.sh
 # @Description: 
### 

# 智能简历分析系统部署脚本

echo "🚀 开始部署智能简历分析系统..."

# 部署后端到阿里云FC
echo "📦 部署后端到阿里云函数计算..."
cd backend

# 检查Serverless Devs工具
if ! command -v s &> /dev/null; then
    echo "⚠️ 未检测到Serverless Devs工具，请先安装："
    echo "npm install @serverless-devs/s -g"
    exit 1
fi

# 部署
s deploy

echo "✅ 后端部署完成！"

# 部署前端到GitHub Pages
echo "📦 部署前端到GitHub Pages..."
cd ../frontend

# 检查并安装依赖
if [ ! -d "node_modules" ]; then
    echo "📥 安装前端依赖..."
    npm install
fi

# 构建
npm run build

# 部署到GitHub Pages
npm run deploy

echo "✅ 前端部署完成！"

echo "🎉 部署完成！"
echo ""
echo "📋 部署信息："
echo "- 后端API：请在阿里云控制台查看函数计算服务的访问地址"
echo "- 前端页面：https://<your-github-username>.github.io/<repository-name>"
