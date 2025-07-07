#!/usr/bin/env python3
"""
本地定时缓存更新脚本
每隔30分钟自动运行，更新cache.json文件并推送到GitHub
"""

import requests
import json
import os
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

# 常量配置
CACHE_FILE = "./cache.json"
API_BASE_URL = "http://45.78.231.212:8001"

def format_train_data(train_data):
    """格式化训练数据"""
    if isinstance(train_data, (int, float)):
        return f"2000步 损失: {train_data:.4f}"
    return str(train_data) if train_data is not None else '无数据'

def format_test_data(test_data):
    """格式化测试数据"""
    if isinstance(test_data, (int, float)):
        return f"平均准确率: {test_data * 100:.2f}%"
    return str(test_data) if test_data is not None else '无数据'

def load_cache_data():
    """加载缓存数据"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("缓存文件格式错误，将使用空数据")
    return {"total_records_at_last_run": 0, "results": [], "last_updated": None}

def get_total_records():
    """获取总记录数"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=60)
        if response.status_code == 200:
            data = response.json()
            return data.get('total_records', 0)
    except requests.exceptions.RequestException as e:
        print(f"获取总记录数失败: {e}")
    return 0

def fetch_single_record(index: int) -> Optional[Dict]:
    """获取单个记录"""
    try:
        url = f"{API_BASE_URL}/elements/with-score/by-index/{index}"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if 'result' in data and 'test' in data['result']:
                # 处理score字段
                raw_score = data.get('score', 0)
                if raw_score != raw_score:  # 检查是否为NaN
                    score_value = 0
                    score_display = "无数据"
                else:
                    score_value = raw_score
                    score_display = f"{raw_score:.4f}" if isinstance(raw_score, (int, float)) else str(raw_score)
                
                return {
                    "index": index,
                    "name": data.get('name', f'节点 {index}'),
                    "parent": data.get('parent'),
                    "train": format_train_data(data['result']['train']),
                    "test": format_test_data(data['result']['test']),
                    "score": score_display,
                    "motivation": data.get('motivation', '无描述'),
                    "raw_data": data,
                    "raw_train": data['result']['train'],
                    "raw_test": data['result']['test'],
                    "raw_score": raw_score
                }
    except requests.exceptions.RequestException as e:
        print(f"获取记录 {index} 失败: {e}")
    return None

def git_push_changes():
    """提交并推送更改到GitHub"""
    try:
        # 检查是否有更改
        result = subprocess.run(['git', 'diff', '--quiet', 'cache.json'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("没有检测到cache.json的更改")
            return False
        
        # 添加文件
        subprocess.run(['git', 'add', 'cache.json'], check=True)
        
        # 提交更改
        commit_message = f"Auto-update cache.json - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # 推送到远程仓库
        subprocess.run(['git', 'push'], check=True)
        
        print("✅ 成功推送更改到GitHub")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git操作失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 推送过程中发生错误: {e}")
        return False

def update_cache_data():
    """更新缓存数据"""
    print("开始更新缓存数据...")
    
    current_total_records = get_total_records()
    if current_total_records == 0:
        print("无法获取服务器数据，跳过更新")
        return False
    
    cache = load_cache_data()
    cached_total_records = cache.get("total_records_at_last_run", 0)
    all_results = cache.get("results", [])
    
    print(f"服务器总记录数: {current_total_records}")
    print(f"缓存记录数: {cached_total_records}")
    
    new_results = []
    new_records_count = current_total_records - cached_total_records
    
    if new_records_count > 0:
        print(f"发现 {new_records_count} 条新记录，开始获取...")
        
        for i, index in enumerate(range(cached_total_records + 1, current_total_records + 1)):
            print(f"正在获取记录 {index}/{current_total_records} ({i+1}/{new_records_count})")
            
            record = fetch_single_record(index)
            if record:
                new_results.append(record)
                all_results.append(record)
            else:
                print(f"获取记录 {index} 失败")
            
            # 避免请求过快
            time.sleep(0.5)
        
        # 更新缓存
        cache["total_records_at_last_run"] = current_total_records
        cache["results"] = all_results
        cache["last_updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 保存缓存
        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
            print(f"成功更新缓存，新增 {len(new_results)} 条记录")
            return True
        except Exception as e:
            print(f"保存缓存失败: {e}")
            return False
    else:
        print("没有新数据需要更新")
        # 即使没有新数据，也更新时间戳
        cache["last_updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"更新时间戳失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print(f"本地缓存更新任务开始")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # 切换到脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        updated = update_cache_data()
        if updated:
            print("✅ 缓存更新成功")
            # 推送更改到GitHub
            git_push_changes()
        else:
            print("ℹ️ 没有新数据更新")
    except Exception as e:
        print(f"❌ 更新过程中发生错误: {e}")
        exit(1)
    
    print("=" * 50)
    print("本地缓存更新任务完成")
    print("=" * 50)

if __name__ == "__main__":
    main() 