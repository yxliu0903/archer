#!/bin/bash
cd /mnt/iem-nas/home/liuyixiu/AI_Archer_local/tree_visual

echo "正在启动Streamlit版本的树形可视化..."
echo "清理可能占用的端口..."

# 清理端口8501 (Streamlit默认端口)
echo "清理端口8501..."
fuser -k 8501/tcp 2>/dev/null || true
pkill -f "streamlit.*streamlit_app.py" 2>/dev/null || true

# 等待端口释放
sleep 5

# 检查是否安装了必要的包
echo "检查依赖包..."
python3 -c "import streamlit, plotly, networkx, requests, pandas" 2>/dev/null || {
    echo "缺少必要的依赖包，正在安装..."
    pip3 install streamlit plotly networkx requests pandas
}

# 更新缓存数据
echo "更新缓存数据..."
python3 -c "
import requests
import json
import os

# 缓存文件路径
CACHE_FILE = '/mnt/iem-nas/home/liuyixiu/AI_Archer_local/tree_visual/cache.json'

def get_total_records():
    try:
        response = requests.get('http://45.78.231.212:8001/stats', timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('total_records', 0)
    except:
        return 0

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {'total_records_at_last_run': 0, 'results': []}

def fetch_record(index):
    try:
        url = f'http://45.78.231.212:8001/elements/with-score/by-index/{index}'
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'result' in data and 'test' in data['result']:
                raw_score = data.get('score', 0)
                if raw_score != raw_score:  # NaN check
                    score_value = 0
                    score_display = '无数据'
                else:
                    score_value = raw_score
                    score_display = f'{raw_score:.4f}' if isinstance(raw_score, (int, float)) else str(raw_score)
                
                train_data = data['result']['train']
                test_data = data['result']['test']
                
                train_formatted = f'2000步 损失: {train_data:.4f}' if isinstance(train_data, (int, float)) else str(train_data) if train_data is not None else '无数据'
                test_formatted = f'平均准确率: {test_data * 100:.2f}%' if isinstance(test_data, (int, float)) else str(test_data) if test_data is not None else '无数据'
                
                return {
                    'index': index,
                    'name': data.get('name', f'节点 {index}'),
                    'parent': data.get('parent'),
                    'train': train_formatted,
                    'test': test_formatted,
                    'score': score_display,
                    'motivation': data.get('motivation', '无描述'),
                    'raw_data': data,
                    'raw_train': train_data,
                    'raw_test': test_data,
                    'raw_score': raw_score
                }
    except:
        pass
    return None

# 更新缓存
current_total = get_total_records()
cache = load_cache()
cached_total = cache.get('total_records_at_last_run', 0)
all_results = cache.get('results', [])

new_count = 0
if current_total > cached_total:
    print(f'发现 {current_total - cached_total} 条新记录，正在更新缓存...')
    for i in range(cached_total + 1, current_total + 1):
        record = fetch_record(i)
        if record:
            all_results.append(record)
            new_count += 1
            print(f'已获取记录 {i}/{current_total}')
    
    # 保存缓存
    cache['total_records_at_last_run'] = current_total
    cache['results'] = all_results
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=4, ensure_ascii=False)
    
    print(f'缓存更新完成，新增 {new_count} 条记录')
else:
    print('缓存已是最新状态')
"

echo "启动Streamlit应用..."
echo "访问地址: http://localhost:8502"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动Streamlit应用
streamlit run streamlit_app.py --server.port=8502 --server.address=0.0.0.0 --server.headless=true 