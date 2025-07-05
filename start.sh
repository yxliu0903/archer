#!/bin/bash
cd /mnt/iem-nas/home/liuyixiu/AI_Archer_local/tree_visual

echo "正在清理端口..."

# 清理端口8000
echo "清理端口8010..."
fuser -k 8010/tcp 2>/dev/null || true
pkill -f "python.*serve.py" 2>/dev/null || true

# 清理端口8002
echo "清理端口8012..."
fuser -k 8012/tcp 2>/dev/null || true
pkill -f "python.*cache_server.py" 2>/dev/null || true

# 等待端口释放
sleep 10

echo "启动树形可视化服务器..."
echo "HTML服务器: http://localhost:8010"
echo "缓存服务器: http://localhost:80012"
echo "访问页面: http://localhost:80010/tree-visualization.html"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动服务器
python3 serve.py 