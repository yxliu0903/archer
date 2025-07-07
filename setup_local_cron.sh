#!/bin/bash

# 设置本地定时任务脚本
# 每30分钟运行一次缓存更新

# 获取当前脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/update_cache_local.py"
LOG_FILE="$SCRIPT_DIR/cron_update.log"

echo "设置本地定时任务..."
echo "脚本目录: $SCRIPT_DIR"
echo "Python脚本: $PYTHON_SCRIPT"
echo "日志文件: $LOG_FILE"

# 检查Python脚本是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "错误: 找不到Python脚本 $PYTHON_SCRIPT"
    exit 1
fi

# 使脚本可执行
chmod +x "$PYTHON_SCRIPT"

# 创建临时cron文件
TEMP_CRON=$(mktemp)

# 获取当前用户的cron任务
crontab -l > "$TEMP_CRON" 2>/dev/null || true

# 检查是否已经存在相同的任务
if grep -q "update_cache_local.py" "$TEMP_CRON"; then
    echo "检测到已存在的定时任务，正在删除旧任务..."
    grep -v "update_cache_local.py" "$TEMP_CRON" > "${TEMP_CRON}.new"
    mv "${TEMP_CRON}.new" "$TEMP_CRON"
fi

# 添加新的cron任务 - 每30分钟运行一次
echo "*/30 * * * * cd $SCRIPT_DIR && /usr/bin/python3 $PYTHON_SCRIPT >> $LOG_FILE 2>&1" >> "$TEMP_CRON"

# 安装新的cron任务
crontab "$TEMP_CRON"

# 清理临时文件
rm "$TEMP_CRON"

echo "✅ 定时任务设置完成！"
echo "任务详情："
echo "  - 执行频率: 每30分钟"
echo "  - 执行脚本: $PYTHON_SCRIPT"
echo "  - 日志文件: $LOG_FILE"
echo ""
echo "查看当前cron任务："
crontab -l | grep update_cache_local.py
echo ""
echo "查看日志文件："
echo "  tail -f $LOG_FILE"
echo ""
echo "如需停止定时任务，请运行："
echo "  $SCRIPT_DIR/stop_local_cron.sh" 