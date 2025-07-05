#!/usr/bin/env python3
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import requests
from datetime import datetime

CACHE_FILE = "./cache.json"

class CacheHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/api/cache':
            self.handle_get_cache()
        elif parsed_path.path == '/api/update':
            self.handle_update_cache()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/cache':
            self.handle_save_cache()
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def handle_get_cache(self):
        """获取缓存数据"""
        cache_data = load_cache()
        self.send_json_response(cache_data)
    
    def handle_save_cache(self):
        """保存缓存数据"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            save_cache(data)
            self.send_json_response({"success": True})
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)})
    
    def handle_update_cache(self):
        """更新缓存 - 类似empty_benchmark.py的逻辑"""
        try:
            results = get_test_results()
            self.send_json_response({
                "success": True,
                "data": results,
                "total_records": len(results)
            })
        except Exception as e:
            self.send_json_response({
                "success": False,
                "error": str(e)
            })

def load_cache():
    """加载缓存文件"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error reading cache file {CACHE_FILE}. Starting with empty cache.")
    return {"total_records_at_last_run": 0, "results": []}

def save_cache(data):
    """保存缓存文件"""
    # 确保目录存在
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_index_num():
    """获取总记录数"""
    url = "http://45.78.231.212:8001/stats"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get('total_records', 0)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching total records: {e}")
    return 0

def get_test_results():
    """获取测试结果 - 参考empty_benchmark.py的逻辑"""
    current_total_records = get_index_num()
    cache = load_cache()
    
    cached_total_records = cache.get("total_records_at_last_run", 0)
    all_results = cache.get("results", [])

    new_results_fetched = []
    
    # 只获取新增的记录
    for i in range(cached_total_records + 1, current_total_records + 1):
        try:
            url = f"http://45.78.231.212:8001/elements/with-score/by-index/{i}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and 'test' in data['result']:
                    # 处理score字段，检查是否为nan（score在根级别）
                    raw_score = data.get('score', 0)
                    if raw_score != raw_score:  # 检查是否为NaN
                        score_value = 0
                        score_display = "无数据"
                    else:
                        score_value = raw_score
                        score_display = f"{raw_score:.4f}" if isinstance(raw_score, (int, float)) else str(raw_score)
                    
                    # 格式化数据
                    train_formatted = format_train_data(data['result']['train'])
                    test_formatted = format_test_data(data['result']['test'])
                    
                    result_entry = {
                        "index": i,
                        "name": data.get('name', f'Node {i}'),
                        "parent": data.get('parent'),
                        "train": train_formatted,
                        "test": test_formatted,
                        "score": score_display,
                        "motivation": data.get('motivation', '无描述'),
                        # 保存完整的原始数据
                        "raw_data": data,
                        "raw_train": data['result']['train'],
                        "raw_test": data['result']['test'],
                        "raw_score": raw_score
                    }
                    new_results_fetched.append(result_entry)
                    all_results.append(result_entry)
                    print(f"新增加的记录 - Index {i}: Test={data['result']['test']}, Score={score_display}")
            else:
                print(f"Error fetching index {i}: Status Code {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching index {i}: {e}")
    
    # 更新缓存
    cache["total_records_at_last_run"] = current_total_records
    cache["results"] = all_results
    save_cache(cache)
    
    return all_results

def format_train_data(train_data):
    """格式化训练数据"""
    if isinstance(train_data, (int, float)):
        return f"2000步 Loss: {train_data:.4f}"
    return str(train_data) if train_data is not None else '无数据'

def format_test_data(test_data):
    """格式化测试数据"""
    if isinstance(test_data, (int, float)):
        return f"平均准确率: {test_data * 100:.2f}%"
    return str(test_data) if test_data is not None else '无数据'

def start_server():
    """启动缓存服务器"""
    server_address = ('', 8012)
    httpd = HTTPServer(server_address, CacheHandler)
    print(f"缓存服务器启动在端口 8012")
    print("API端点:")
    print("  GET  /api/cache  - 获取缓存数据")
    print("  POST /api/cache  - 保存缓存数据")
    print("  GET  /api/update - 更新缓存数据")
    print("按 Ctrl+C 停止服务器")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n缓存服务器已停止")

if __name__ == "__main__":
    start_server() 