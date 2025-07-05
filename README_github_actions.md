# GitHub Actions 自动更新 Cache.json

这个项目使用 GitHub Actions 来每隔30分钟自动更新 `cache.json` 文件，确保数据始终保持最新状态。

## 🚀 功能特性

- ⏰ **定时更新**: 每隔30分钟自动运行
- 🔄 **增量更新**: 只获取新增的数据记录
- 📝 **自动提交**: 有新数据时自动提交到GitHub
- 🛡️ **错误处理**: 包含完整的错误处理和日志记录
- 🎯 **手动触发**: 支持手动触发更新任务

## 📁 文件结构

```
.github/
└── workflows/
    └── update-cache.yml          # GitHub Actions 工作流配置
update_cache_github.py            # 缓存更新脚本
cache.json                        # 缓存数据文件
```

## ⚙️ 设置步骤

### 1. 确保文件结构正确

确保你的仓库中有以下文件：
- `.github/workflows/update-cache.yml` - GitHub Actions 工作流
- `update_cache_github.py` - 更新脚本
- `cache.json` - 缓存文件（如果不存在会自动创建）

### 2. 推送到GitHub

将所有文件推送到你的GitHub仓库：

```bash
git add .
git commit -m "Add GitHub Actions for automatic cache updates"
git push origin main
```

### 3. 启用GitHub Actions

1. 进入你的GitHub仓库页面
2. 点击 "Actions" 标签页
3. 如果这是第一次使用Actions，点击 "I understand my workflows, go ahead and enable them"
4. 你应该能看到 "Update Cache Data" 工作流

### 4. 手动测试（可选）

你可以手动触发一次更新来测试：

1. 在 Actions 页面点击 "Update Cache Data" 工作流
2. 点击 "Run workflow" 按钮
3. 点击绿色的 "Run workflow" 按钮确认

## 🔧 工作流配置说明

### 定时设置

```yaml
schedule:
  - cron: '*/30 * * * *'  # 每30分钟运行一次
```

你可以修改这个cron表达式来改变运行频率：
- `*/15 * * * *` - 每15分钟
- `0 * * * *` - 每小时整点
- `0 */2 * * *` - 每2小时

### 工作流步骤

1. **检出代码**: 获取仓库代码
2. **设置Python**: 安装Python 3.9环境
3. **安装依赖**: 安装requests库
4. **运行更新脚本**: 执行缓存更新
5. **检查变更**: 检查cache.json是否有变化
6. **提交变更**: 如果有新数据，自动提交到仓库

## 📊 监控和日志

### 查看运行状态

1. 进入GitHub仓库的 "Actions" 页面
2. 点击具体的工作流运行记录
3. 查看每个步骤的详细日志

### 运行日志示例

```
开始更新缓存数据...
服务器总记录数: 150
缓存记录数: 145
发现 5 条新记录，开始获取...
正在获取记录 146/150 (1/5)
正在获取记录 147/150 (2/5)
...
成功更新缓存，新增 5 条记录
✅ 缓存更新成功
```

## 🛠️ 自定义配置

### 修改API地址

如果需要修改API服务器地址，编辑 `update_cache_github.py` 文件：

```python
API_BASE_URL = "http://your-api-server:port"
```

### 修改更新频率

编辑 `.github/workflows/update-cache.yml` 文件中的cron表达式：

```yaml
schedule:
  - cron: '*/15 * * * *'  # 改为每15分钟
```

### 添加通知

你可以在工作流中添加通知步骤，例如发送邮件或Slack消息：

```yaml
- name: Notify on success
  if: steps.check_changes.outputs.changed == 'true'
  run: echo "Cache updated successfully! New data available."
```

## 🔍 故障排除

### 常见问题

1. **工作流没有运行**
   - 检查cron语法是否正确
   - 确保仓库有活动（GitHub会暂停不活跃仓库的定时任务）

2. **API请求失败**
   - 检查API服务器是否可访问
   - 检查网络连接和超时设置

3. **提交失败**
   - 检查GITHUB_TOKEN权限
   - 确保没有其他进程同时修改文件

### 调试步骤

1. 手动运行工作流查看详细日志
2. 检查API服务器状态
3. 验证cache.json文件格式
4. 查看GitHub Actions的限制和配额

## 📈 性能优化

- 脚本使用增量更新，只获取新数据
- 添加了请求间隔避免服务器压力
- 使用适当的超时设置
- 只在有变更时才提交代码

## 🔒 安全考虑

- 使用GitHub提供的GITHUB_TOKEN
- 不在代码中硬编码敏感信息
- 合理设置API请求超时
- 添加错误处理避免脚本崩溃

## 📝 维护建议

1. 定期检查工作流运行状态
2. 监控cache.json文件大小
3. 根据需要调整运行频率
4. 及时处理API变更或服务器迁移

---

如果你遇到任何问题或需要帮助，请查看GitHub Actions的运行日志或创建Issue。 