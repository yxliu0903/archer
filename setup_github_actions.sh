#!/bin/bash

# GitHub Actions 自动更新缓存设置脚本
# 这个脚本会帮助你快速设置所有必要的文件和配置

echo "🚀 GitHub Actions 自动更新缓存设置工具"
echo "======================================="

# 检查当前目录
echo "📁 当前目录: $(pwd)"

# 检查必要文件
echo "🔍 检查必要文件..."

# 检查 .github/workflows 目录
if [ ! -d ".github/workflows" ]; then
    echo "📂 创建 .github/workflows 目录..."
    mkdir -p .github/workflows
fi

# 检查工作流文件
if [ -f ".github/workflows/update-cache.yml" ]; then
    echo "✅ GitHub Actions 工作流文件已存在"
else
    echo "❌ 缺少 GitHub Actions 工作流文件"
fi

# 检查更新脚本
if [ -f "update_cache_github.py" ]; then
    echo "✅ 缓存更新脚本已存在"
else
    echo "❌ 缺少缓存更新脚本"
fi

# 检查缓存文件
if [ -f "cache.json" ]; then
    echo "✅ 缓存文件已存在"
    echo "📊 缓存文件大小: $(du -h cache.json | cut -f1)"
else
    echo "⚠️  缓存文件不存在，将在首次运行时创建"
fi

# 检查测试脚本
if [ -f "test_update.py" ]; then
    echo "✅ 测试脚本已存在"
else
    echo "❌ 缺少测试脚本"
fi

echo ""
echo "🔧 设置步骤:"
echo "1. 确保所有文件都已创建"
echo "2. 运行测试: python test_update.py"
echo "3. 提交到GitHub: git add . && git commit -m 'Add GitHub Actions' && git push"
echo "4. 在GitHub仓库中启用Actions"

echo ""
echo "📝 下一步操作:"

# 检查git状态
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "✅ 当前目录是Git仓库"
    
    # 检查是否有未提交的更改
    if [ -n "$(git status --porcelain)" ]; then
        echo "📋 发现未提交的更改:"
        git status --short
        echo ""
        echo "💡 建议运行以下命令提交更改:"
        echo "   git add ."
        echo "   git commit -m 'Add GitHub Actions for automatic cache updates'"
        echo "   git push origin main"
    else
        echo "✅ 没有未提交的更改"
    fi
    
    # 检查远程仓库
    if git remote -v | grep -q origin; then
        echo "✅ 已配置远程仓库"
        echo "🌐 远程仓库: $(git remote get-url origin)"
    else
        echo "⚠️  未配置远程仓库，请先添加GitHub远程仓库"
    fi
else
    echo "❌ 当前目录不是Git仓库"
    echo "💡 请先运行: git init"
fi

echo ""
echo "🧪 测试建议:"
echo "1. 运行本地测试: python test_update.py"
echo "2. 检查API连接是否正常"
echo "3. 验证缓存文件是否正确更新"

echo ""
echo "📚 文档参考:"
echo "- README_github_actions.md - 详细设置说明"
echo "- GitHub Actions 页面: https://github.com/你的用户名/你的仓库名/actions"

echo ""
echo "✨ 设置完成！"
echo "=======================================" 