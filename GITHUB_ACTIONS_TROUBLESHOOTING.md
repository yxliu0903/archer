# GitHub Actions 权限问题故障排除指南

## 🚨 遇到的问题

```
remote: Permission to yxliu0903/archer.git denied to github-actions[bot].
fatal: unable to access 'https://github.com/yxliu0903/archer/': The requested URL returned error: 403
```

这是一个常见的GitHub Actions权限问题。我已经更新了工作流文件来解决这个问题。

## 🔧 已应用的修复

### 1. 添加了权限配置
在 `.github/workflows/update-cache.yml` 中添加了：
```yaml
permissions:
  contents: write  # 允许写入仓库内容
```

### 2. 使用专用的git-auto-commit-action
替换了手动的git命令，使用更可靠的第三方action：
```yaml
- name: Commit and push changes
  if: steps.check_changes.outputs.changed == 'true'
  uses: stefanzweifel/git-auto-commit-action@v5
  with:
    commit_message: "Auto-update cache.json - $(date '+%Y-%m-%d %H:%M:%S UTC')"
    file_pattern: cache.json
    commit_user_name: github-actions[bot]
    commit_user_email: 41898282+github-actions[bot]@users.noreply.github.com
```

## 🔍 需要检查的仓库设置

### 1. Actions权限设置
1. 进入GitHub仓库页面
2. 点击 **Settings** (设置)
3. 在左侧菜单找到 **Actions** → **General**
4. 在 "Workflow permissions" 部分，确保选择了：
   - ✅ **Read and write permissions**
   - ✅ **Allow GitHub Actions to create and approve pull requests** (可选)

### 2. 检查分支保护规则
1. 在 Settings 中找到 **Branches**
2. 如果 `main` 分支有保护规则，需要：
   - 允许 GitHub Actions 推送
   - 或者添加 `github-actions[bot]` 到例外列表

## 🚀 重新部署步骤

### 第1步：推送更新的工作流
```bash
git add .github/workflows/update-cache.yml
git commit -m "Fix GitHub Actions permissions"
git push origin main
```

### 第2步：手动测试
1. 进入GitHub仓库的 **Actions** 页面
2. 点击 **Update Cache Data** 工作流
3. 点击 **Run workflow** 手动触发
4. 观察运行结果

### 第3步：检查运行日志
如果仍有问题，查看详细日志：
1. 点击失败的工作流运行
2. 展开各个步骤查看错误信息
3. 特别关注 "Commit and push changes" 步骤

## 🔄 备选方案

如果上述方法仍然不工作，可以尝试以下备选方案：

### 方案1：使用Personal Access Token
1. 创建GitHub Personal Access Token (PAT)
2. 在仓库 Settings → Secrets and variables → Actions 中添加
3. 修改工作流使用PAT而不是GITHUB_TOKEN

### 方案2：简化权限模型
使用更简单的提交方式：
```yaml
- name: Commit and push changes
  if: steps.check_changes.outputs.changed == 'true'
  run: |
    git config --global user.name 'github-actions'
    git config --global user.email 'github-actions@github.com'
    git add cache.json
    git commit -m "Auto-update cache.json"
    git push
```

## 📋 常见问题检查清单

- [ ] 仓库的 Actions 权限设置为 "Read and write"
- [ ] 没有分支保护规则阻止推送
- [ ] 工作流文件中包含了 `permissions: contents: write`
- [ ] 使用了正确的GitHub Actions bot邮箱
- [ ] 网络连接正常，能访问GitHub API

## 🎯 预期结果

修复后，你应该看到：
1. 工作流成功运行
2. cache.json文件被自动更新
3. 提交记录显示 "github-actions[bot]" 作为作者
4. 没有权限错误

## 📞 获取帮助

如果问题仍然存在：
1. 检查GitHub Status页面是否有服务问题
2. 查看GitHub Actions文档的最新权限要求
3. 在仓库中创建Issue描述具体错误

---

**更新时间**: 修复已应用，请重新推送并测试工作流。 