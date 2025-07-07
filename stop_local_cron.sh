#!/bin/bash

# 停止本地定时任务脚本

echo "停止本地定时任务..."

# 创建临时cron文件
TEMP_CRON=$(mktemp)

# 获取当前用户的cron任务
crontab -l > "$TEMP_CRON" 2>/dev/null || true

# 检查是否存在相关任务
if grep -q "update_cache_local.py" "$TEMP_CRON"; then
    echo "找到相关定时任务，正在删除..."
    
    # 删除包含update_cache_local.py的行
    grep -v "update_cache_local.py" "$TEMP_CRON" > "${TEMP_CRON}.new"
    mv "${TEMP_CRON}.new" "$TEMP_CRON"
    
    # 安装新的cron任务
    crontab "$TEMP_CRON"
    
    echo "✅ 定时任务已停止！"
else
    echo "ℹ️ 没有找到相关的定时任务"
fi

# 清理临时文件
rm "$TEMP_CRON"

echo ""
echo "当前剩余的cron任务："
crontab -l 2>/dev/null || echo "没有定时任务" 