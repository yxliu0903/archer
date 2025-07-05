# 🚀 GitHub Actions 自动更新缓存 - 快速设置指南

## 📋 已创建的文件

我已经为你创建了以下文件来实现每隔30分钟自动更新cache.json的功能：

### 核心文件
1. **`.github/workflows/update-cache.yml`** - GitHub Actions工作流配置
2. **`update_cache_github.py`** - 缓存更新脚本
3. **`test_update.py`** - 本地测试脚本
4. **`setup_github_actions.sh`** - 一键设置脚本

### 文档文件
5. **`README_github_actions.md`** - 详细使用说明
6. **`SETUP_SUMMARY.md`** - 本文件（快速指南）

## ⚡ 快速开始（3步完成）

### 第1步：本地测试
```bash
# 测试脚本是否正常工作
python test_update.py
```

### 第2步：推送到GitHub
```bash
# 添加所有文件
git add .

# 提交更改
git commit -m "Add GitHub Actions for automatic cache updates"

# 推送到GitHub
git push origin main
```

### 第3步：启用GitHub Actions
1. 打开你的GitHub仓库页面
2. 点击 "Actions" 标签
3. 如果提示启用Actions，点击启用
4. 你会看到 "Update Cache Data" 工作流

## 🎯 功能特性

- ⏰ **每30分钟自动运行** - 使用cron表达式 `*/30 * * * *`
- 🔄 **增量更新** - 只获取新数据，不重复下载
- 📝 **自动提交** - 有新数据时自动提交到GitHub
- 🎮 **手动触发** - 可以在GitHub页面手动运行
- 🛡️ **错误处理** - 包含完整的错误处理机制

## 📊 监控运行状态

1. 进入GitHub仓库的 "Actions" 页面
2. 查看 "Update Cache Data" 工作流的运行历史
3. 点击具体运行记录查看详细日志

## 🔧 自定义设置

### 修改运行频率
编辑 `.github/workflows/update-cache.yml` 中的cron表达式：
```yaml
schedule:
  - cron: '*/15 * * * *'  # 改为每15分钟
```

### 修改API地址
编辑 `update_cache_github.py` 中的API_BASE_URL：
```python
API_BASE_URL = "http://your-new-api-server:port"
```

## 🔍 故障排除

### 常见问题
- **工作流没有运行**: 检查仓库是否有活动，GitHub会暂停不活跃仓库的定时任务
- **API连接失败**: 检查服务器 `http://45.78.231.212:8001` 是否可访问
- **提交失败**: 检查GitHub权限设置

### 调试方法
1. 运行本地测试：`python test_update.py`
2. 查看GitHub Actions日志
3. 手动触发工作流测试

## 📈 预期效果

设置完成后，你的仓库将：
- 每30分钟自动检查新数据
- 有新数据时自动更新cache.json
- 自动提交更新到GitHub
- 保持数据始终最新

## 🎉 完成！

现在你的GitHub仓库将自动维护最新的cache.json文件，无需手动干预！

---

如有问题，请查看 `README_github_actions.md` 获取详细说明。 