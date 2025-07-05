import requests
import json
import os

CACHE_FILE = "./cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error reading cache file {CACHE_FILE}. Starting with empty cache.")
    return {"total_records_at_last_run": 0, "results": []}

def save_cache(data):
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f, indent=4)


def get_index_num():
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
    current_total_records = get_index_num()
    cache = load_cache()
    
    cached_total_records = cache.get("total_records_at_last_run", 0)
    all_results = cache.get("results", [])

    new_results_fetched = []
    # Only fetch new records that have been added since the last run
    for i in range(cached_total_records + 1, current_total_records + 1):
        try:
            url = f"http://45.78.231.212:8001/elements/by-index/{i}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and 'test' in data['result']:
                    result_entry = {"index": i, "test": data['result']['test'], "train": data['result']['train'], "name": data['name'], "parent": data['parent']}
                    new_results_fetched.append(result_entry)
                    print(f"新增加的记录 - Index {i}: {data['result']['test']}")
            else:
                print(f"Error fetching index {i}: Status Code {response.status_code}. Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching index {i}: {e}")
    
    # Append new results to the overall list of results in cache
    all_results.extend(new_results_fetched)
    
    # Update cache and save
    cache["total_records_at_last_run"] = current_total_records
    cache["results"] = all_results
    save_cache(cache)
    
    return all_results

if __name__ == "__main__":
    results = get_test_results()
    print("\n所有已缓存的测试结果:")
    for res in results:
        print(f"Index {res['index']}: {res['test_result']}")
