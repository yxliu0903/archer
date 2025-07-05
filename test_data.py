#!/usr/bin/env python3
import requests
import json

def test_api():
    """测试API数据获取"""
    print("测试API数据获取...")
    
    # 测试获取总记录数
    try:
        response = requests.get("http://45.78.231.212:8001/stats")
        if response.status_code == 200:
            data = response.json()
            total_records = data.get('total_records', 0)
            print(f"总记录数: {total_records}")
            
            # 测试获取第一个记录
            if total_records > 0:
                response = requests.get("http://45.78.231.212:8001/elements/with-score/by-index/1")
                if response.status_code == 200:
                    data = response.json()
                    print(f"第一个记录: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    # 检查各个字段
                    if 'result' in data:
                        result = data['result']
                        print(f"Train: {result.get('train', 'N/A')}")
                        print(f"Test: {result.get('test', 'N/A')}")
                        
                        # score在根级别，不在result里
                        score = data.get('score', 'N/A')
                        print(f"Score: {score}")
                        print(f"Score type: {type(score)}")
                        
                        # 检查是否为NaN
                        if score != score:  # NaN检查
                            print("Score is NaN!")
                        elif isinstance(score, (int, float)):
                            print(f"Score is numeric: {score}")
                        else:
                            print(f"Score is not numeric: {score}")
                    else:
                        print("No result field found")
                else:
                    print(f"获取第一个记录失败: {response.status_code}")
        else:
            print(f"获取总记录数失败: {response.status_code}")
    except Exception as e:
        print(f"API测试失败: {e}")

if __name__ == "__main__":
    test_api() 