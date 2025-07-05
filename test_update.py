#!/usr/bin/env python3
"""
测试缓存更新功能的脚本
用于本地测试GitHub Actions脚本是否正常工作
"""

import subprocess
import sys
import os
from datetime import datetime

def test_update_script():
    """测试更新脚本"""
    print("=" * 60)
    print("🧪 测试缓存更新脚本")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 检查文件是否存在
    script_file = "update_cache_github.py"
    if not os.path.exists(script_file):
        print(f"❌ 错误: 找不到脚本文件 {script_file}")
        return False
    
    print(f"✅ 找到脚本文件: {script_file}")
    
    # 运行脚本
    try:
        print("\n🚀 开始运行更新脚本...")
        result = subprocess.run([sys.executable, script_file], 
                              capture_output=True, text=True, timeout=300)
        
        print("\n📄 脚本输出:")
        print("-" * 40)
        print(result.stdout)
        
        if result.stderr:
            print("\n⚠️ 错误输出:")
            print("-" * 40)
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ 脚本执行成功！")
            return True
        else:
            print(f"\n❌ 脚本执行失败，返回码: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n⏰ 脚本执行超时（5分钟）")
        return False
    except Exception as e:
        print(f"\n❌ 执行脚本时发生错误: {e}")
        return False

def check_cache_file():
    """检查缓存文件"""
    cache_file = "cache.json"
    if os.path.exists(cache_file):
        size = os.path.getsize(cache_file)
        print(f"📁 缓存文件大小: {size:,} 字节")
        
        # 检查文件修改时间
        mtime = os.path.getmtime(cache_file)
        mod_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"📅 最后修改时间: {mod_time}")
        return True
    else:
        print("❌ 缓存文件不存在")
        return False

def main():
    """主函数"""
    print("🔧 GitHub Actions 缓存更新测试工具")
    print()
    
    # 检查缓存文件状态（更新前）
    print("📋 更新前状态:")
    check_cache_file()
    print()
    
    # 运行测试
    success = test_update_script()
    print()
    
    # 检查缓存文件状态（更新后）
    print("📋 更新后状态:")
    check_cache_file()
    print()
    
    if success:
        print("🎉 测试完成！脚本运行正常。")
        print("💡 现在你可以将代码推送到GitHub，Actions将自动运行。")
    else:
        print("❌ 测试失败！请检查脚本和API连接。")
    
    print("=" * 60)

if __name__ == "__main__":
    main()