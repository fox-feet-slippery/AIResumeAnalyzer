#!/bin/bash

# 后端服务部署脚本

echo "🚀 部署后端服务到阿里云函数计算..."

# 检查Serverless Devs工具
if ! command -v s &> /dev/null; then
    echo "⚠️ 未检测到Serverless Devs工具，请先安装："
    echo "npm install @serverless-devs/s -g"
    exit 1
fi

# 检查环境变量
if [ -z "$DASHSCOPE_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️ 警告：未设置AI API密钥，请在部署前配置："
    echo "export DASHSCOPE_API_KEY=your_key"
    echo "或"
    echo "export OPENAI_API_KEY=your_key"
fi

# 部署
echo "📦 开始部署..."
s deploy

echo "✅ 部署完成！"
