#!/bin/bash

# 启动带翻译功能的Streamlit应用 (Archer版本)
echo "🚀 启动Delta Net树结构可视化应用 - Archer版本 (带翻译功能)"

# 设置豆包API密钥（如果未设置）
if [ -z "$ARK_API_KEY" ]; then
    echo "🔑 设置豆包API密钥..."
    export ARK_API_KEY="7955573a-a3dd-4c9f-93bf-5bb24fdba252"
fi

# 检查并安装依赖
echo "📦 检查依赖..."
pip install -r requirements.txt

# 启动Streamlit应用
echo "🌐 启动Streamlit应用..."
streamlit run streamlit_app.py --server.port=8502 --server.address=0.0.0.0

echo "✅ 应用已启动！"
echo "🌐 请访问 http://localhost:8502 查看可视化界面"
echo "💡 点击节点将自动翻译成中文！" 