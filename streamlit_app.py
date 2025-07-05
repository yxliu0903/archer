#!/usr/bin/env python3
"""
Streamlit版本的Delta Net树结构可视化应用
"""

import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import os
import networkx as nx
from typing import Dict, List, Optional, Tuple

# 页面配置
st.set_page_config(
    page_title="Delta Net 树结构可视化",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 常量配置
CACHE_FILE = "./cache.json"
API_BASE_URL = "http://45.78.231.212:8001"

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .node-info {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 4px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 4px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# 缓存函数
@st.cache_data(ttl=300)  # 5分钟缓存
def load_cache_data():
    """加载缓存数据"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.error("缓存文件格式错误，将使用空数据")
    return {"total_records_at_last_run": 0, "results": []}

@st.cache_data(ttl=60)  # 1分钟缓存
def get_total_records():
    """获取总记录数"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('total_records', 0)
    except requests.exceptions.RequestException as e:
        st.error(f"获取总记录数失败: {e}")
    return 0

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

def fetch_single_record(index: int) -> Optional[Dict]:
    """获取单个记录"""
    try:
        url = f"{API_BASE_URL}/elements/with-score/by-index/{index}"
        response = requests.get(url, timeout=10)
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
        st.error(f"获取记录 {index} 失败: {e}")
    return None

def update_cache_data():
    """更新缓存数据"""
    current_total_records = get_total_records()
    cache = load_cache_data()
    
    cached_total_records = cache.get("total_records_at_last_run", 0)
    all_results = cache.get("results", [])
    
    new_results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 获取新增记录
    new_records_count = current_total_records - cached_total_records
    if new_records_count > 0:
        for i, index in enumerate(range(cached_total_records + 1, current_total_records + 1)):
            progress = (i + 1) / new_records_count
            progress_bar.progress(progress)
            status_text.text(f"正在获取记录 {index}/{current_total_records}")
            
            record = fetch_single_record(index)
            if record:
                new_results.append(record)
                all_results.append(record)
            
            time.sleep(0.1)  # 避免请求过快
    
    # 更新缓存
    cache["total_records_at_last_run"] = current_total_records
    cache["results"] = all_results
    
    # 保存缓存
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"保存缓存失败: {e}")
    
    progress_bar.empty()
    status_text.empty()
    
    return all_results, new_records_count

def build_tree_structure(nodes: List[Dict]) -> Optional[Dict]:
    """构建树形结构"""
    if not nodes:
        return None
    
    # 添加调试信息
    st.write(f"🔍 调试信息: 总共有 {len(nodes)} 个节点")
    
    # 创建节点映射
    node_map = {}
    for node in nodes:
        node_map[node['index']] = {
            **node,
            'children': []
        }
    
    # 分析所有节点的parent信息
    parent_info = {}
    root_candidates = []
    
    for node in nodes:
        parent = node.get('parent')
        parent_info[node['index']] = parent
        
        # 判断根节点的条件
        if parent is None or parent == 0 or parent == node['index']:
            root_candidates.append(node['index'])
        elif parent not in node_map:
            # 父节点不存在，也可能是根节点
            root_candidates.append(node['index'])
    
    # 调试信息
    st.write(f"🔍 父节点信息: {parent_info}")
    st.write(f"🔍 根节点候选: {root_candidates}")
    
    # 构建父子关系
    root = None
    orphaned_nodes = []  # 孤立节点
    
    for node in nodes:
        parent_id = node.get('parent')
        
        if node['index'] in root_candidates:
            # 这是根节点候选
            if root is None:
                root = node_map[node['index']]
                st.write(f"🌳 选择节点 {node['index']} 作为根节点")
            else:
                # 有多个根节点，选择index最小的作为真正的根节点
                if node['index'] < root['index']:
                    # 将之前的根节点作为新根节点的子节点
                    old_root = root
                    root = node_map[node['index']]
                    root['children'].append(old_root)
                    st.write(f"🌳 更换根节点为 {node['index']}，原根节点 {old_root['index']} 成为子节点")
                else:
                    # 将当前节点作为根节点的子节点
                    root['children'].append(node_map[node['index']])
                    st.write(f"🌳 节点 {node['index']} 成为根节点的子节点")
        else:
            # 这是子节点
            parent = node_map.get(parent_id)
            if parent:
                parent['children'].append(node_map[node['index']])
                st.write(f"🔗 节点 {node['index']} 连接到父节点 {parent_id}")
            else:
                orphaned_nodes.append(node['index'])
                st.write(f"⚠️ 节点 {node['index']} 的父节点 {parent_id} 不存在")
    
    # 处理孤立节点
    if orphaned_nodes:
        st.write(f"🔍 发现 {len(orphaned_nodes)} 个孤立节点: {orphaned_nodes}")
        if root:
            # 将孤立节点作为根节点的子节点
            for orphan_id in orphaned_nodes:
                root['children'].append(node_map[orphan_id])
                st.write(f"🔗 孤立节点 {orphan_id} 连接到根节点")
    
    if root:
        # 统计树的结构
        def count_tree_nodes(node):
            count = 1
            for child in node.get('children', []):
                count += count_tree_nodes(child)
            return count
        
        total_nodes_in_tree = count_tree_nodes(root)
        st.write(f"🌳 树结构构建完成: 根节点 {root['index']}, 树中总节点数 {total_nodes_in_tree}")
        
        if total_nodes_in_tree != len(nodes):
            st.warning(f"⚠️ 树中节点数({total_nodes_in_tree})与原始节点数({len(nodes)})不匹配")
    else:
        st.error("❌ 未能找到根节点")
    
    return root

def calculate_hierarchical_layout(root: Dict) -> Dict:
    """计算层次化布局位置 - 子节点在父节点下方"""
    positions = {}
    
    # 递归计算每个节点的位置
    def calculate_subtree_positions(node, level=0, parent_x=0):
        node_id = node['index']
        children = node.get('children', [])
        
        # 垂直间距
        y = level * 800  # 大幅增加垂直间距
        
        if not children:
            # 叶子节点，直接使用父节点的x坐标
            x = parent_x
            positions[node_id] = (x, y)
            return x, x  # 返回子树的左右边界
        
        # 有子节点，递归计算子节点位置
        child_positions = []
        total_width = 0
        
        # 先计算所有子节点的位置
        for i, child in enumerate(children):
            # 给每个子节点分配初始x位置
            child_x = i * 1000  # 大幅增加水平间距，确保不重叠
            left_bound, right_bound = calculate_subtree_positions(child, level + 1, child_x)
            child_positions.append((left_bound, right_bound))
        
        # 重新调整子节点位置，确保它们在父节点下方居中
        if child_positions:
            # 计算子节点的总宽度
            leftmost = min(pos[0] for pos in child_positions)
            rightmost = max(pos[1] for pos in child_positions)
            subtree_width = rightmost - leftmost
            
            # 调整所有子节点的位置，使它们以父节点为中心
            offset = parent_x - (leftmost + rightmost) / 2
            
            for i, child in enumerate(children):
                child_id = child['index']
                old_x, old_y = positions[child_id]
                new_x = old_x + offset
                positions[child_id] = (new_x, old_y)
                
                # 递归调整子节点的子节点
                adjust_subtree_positions(child, offset)
        
        # 父节点位置
        if children:
            # 父节点位于子节点的中央上方
            child_x_positions = [positions[child['index']][0] for child in children]
            x = sum(child_x_positions) / len(child_x_positions)
        else:
            x = parent_x
            
        positions[node_id] = (x, y)
        
        # 返回子树的边界
        if children:
            all_x = [positions[child['index']][0] for child in children] + [x]
            return min(all_x), max(all_x)
        else:
            return x, x
    
    def adjust_subtree_positions(node, offset):
        """递归调整子树中所有节点的位置"""
        for child in node.get('children', []):
            child_id = child['index']
            if child_id in positions:
                old_x, old_y = positions[child_id]
                positions[child_id] = (old_x + offset, old_y)
                adjust_subtree_positions(child, offset)
    
    # 从根节点开始计算
    calculate_subtree_positions(root, 0, 0)
    
    # 调试信息
    for node_id, (x, y) in positions.items():
        print(f"Node {node_id}: x={x:.1f}, y={y:.1f}")
    
    return positions

def create_tree_visualization(root: Dict):
    """创建树形可视化图表"""
    if not root:
        return None
    
    # 使用NetworkX构建图
    G = nx.DiGraph()
    
    def add_nodes_edges(node, parent_id=None):
        node_id = node['index']
        G.add_node(node_id, **node)
        
        if parent_id is not None:
            G.add_edge(parent_id, node_id)
        
        for child in node.get('children', []):
            add_nodes_edges(child, node_id)
    
    add_nodes_edges(root)
    
    # 使用层次布局 - 手动计算位置
    pos = calculate_hierarchical_layout(root)
    
    # 创建边的轨迹 - 使用直角连接线
    edge_traces = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        # 创建直角连接线：从父节点向下，然后水平到子节点
        mid_y = y0 + (y1 - y0) / 2
        
        edge_traces.append(go.Scatter(
            x=[x0, x0, x1, x1],
            y=[y0, mid_y, mid_y, y1],
            mode='lines',
            line=dict(width=3, color='#666'),
            hoverinfo='none',
            showlegend=False
        ))
    
    # 创建节点轨迹
    node_x = []
    node_y = []
    node_text = []
    node_info = []
    node_colors = []
    node_sizes = []
    
    # 计算节点层级用于大小调整
    node_levels = {}
    def calc_node_level(node, level=0):
        node_levels[node['index']] = level
        for child in node.get('children', []):
            calc_node_level(child, level + 1)
    
    calc_node_level(root)
    
    for node_id in G.nodes():
        x, y = pos[node_id]
        node_x.append(x)
        node_y.append(y)
        
        node_data = G.nodes[node_id]
        node_text.append(f"{node_id}")
        
        # 悬停信息
        hover_text = f"""
        <b>节点 {node_id}</b><br>
        名称: {node_data.get('name', '未知')}<br>
        层级: {node_levels.get(node_id, 0)}<br>
        训练: {node_data.get('train', '无数据')}<br>
        测试: {node_data.get('test', '无数据')}<br>
        评分: {node_data.get('score', '无数据')}<br>
        描述: {node_data.get('motivation', '无描述')[:50]}...
        """
        node_info.append(hover_text)
        
        # 根据评分设置颜色
        try:
            score = float(node_data.get('raw_score', 0))
            if score != score:  # NaN检查
                score = 0
            node_colors.append(score)
        except (ValueError, TypeError):
            node_colors.append(0)
        
        # 根据层级设置大小（根节点最大）
        level = node_levels.get(node_id, 0)
        if level == 0:
            node_sizes.append(50)  # 根节点 - 增大
        elif level == 1:
            node_sizes.append(35)  # 第一层子节点
        else:
            node_sizes.append(30)  # 其他子节点 - 增大
    
    # 创建图表
    fig = go.Figure()
    
    # 添加所有边
    for edge_trace in edge_traces:
        fig.add_trace(edge_trace)
    
    # 添加节点
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='none',  # 禁用悬停信息
        text=node_text,
        textposition="middle center",
        textfont=dict(
            size=14,
            color='white',
            family='Arial Black'
        ),
        marker=dict(
            size=node_sizes,
            color=node_colors,
            colorscale='RdYlBu',
            showscale=True,
            colorbar=dict(
                title="评分",
                x=1.02
            ),
            line=dict(width=3, color='white'),
            opacity=0.8
        ),
        name='节点',
        # 添加自定义数据来存储节点ID
        customdata=node_text  # 存储节点ID用于点击事件
    ))
    
    fig.update_layout(
        title=dict(
            text="Delta Net 树结构可视化",
            font=dict(size=18, color='#2E86AB'),
            x=0.5
        ),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=50, l=50, r=100, t=80),
        annotations=[
            dict(
                text="💡 颜色表示评分高低，可拖拽和缩放，点击节点查看详情",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.5, y=-0.05,
                xanchor='center', yanchor='top',
                font=dict(color='gray', size=12)
            )
        ],
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=1,
            zeroline=False,
            showticklabels=False,
            title="",
            range=[-5000, 5000]  # 设置x轴范围以适应大间距
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=1,
            zeroline=False,
            showticklabels=False,
            title="",
            autorange='reversed',  # 根节点在顶部
            range=[-500, 5000]  # 设置y轴范围
        ),
        plot_bgcolor='#fafafa',
        paper_bgcolor='white',
        height=1400,  # 进一步增加高度以适应更大间距
        width=2200,   # 大幅增加宽度以适应更大的水平间距
        font=dict(family="Arial, sans-serif"),
        # 启用拖拽功能
        dragmode='pan'  # 设置为拖拽模式
    )
    
    return fig

def display_node_details(node: Dict):
    """显示节点详细信息"""
    st.markdown(f"""
    <div class="node-info">
        <h3>节点 {node['index']} - {node.get('name', '未知')}</h3>
        <p><strong>父节点:</strong> {node.get('parent', '无')}</p>
        <p><strong>训练结果:</strong> {node.get('train', '无数据')}</p>
        <p><strong>测试结果:</strong> {node.get('test', '无数据')}</p>
        <p><strong>评分:</strong> {node.get('score', '无数据')}</p>
        <p><strong>描述:</strong> {node.get('motivation', '无描述')}</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """主函数"""
    # 页面标题
    st.markdown("""
    <div class="main-header">
        <h1>🌳 Delta Net 树结构可视化</h1>
        <p>交互式模型层次结构展示</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 侧边栏
    st.sidebar.title("🔧 控制面板")
    
    # 数据更新按钮
    if st.sidebar.button("🔄 更新数据", help="从服务器获取最新数据"):
        with st.spinner("正在更新数据..."):
            all_results, new_count = update_cache_data()
            st.cache_data.clear()  # 清除缓存
            if new_count > 0:
                st.success(f"成功获取 {new_count} 条新记录！")
            else:
                st.info("没有新数据需要更新")
    
    # 加载数据
    cache_data = load_cache_data()
    all_results = cache_data.get("results", [])
    
    # 显示统计信息
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(all_results)}</h3>
            <p>总节点数</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        variants = max(0, len(all_results) - 1)
        st.markdown(f"""
        <div class="metric-card">
            <h3>{variants}</h3>
            <p>变体数量</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        current_total = get_total_records()
        st.markdown(f"""
        <div class="metric-card">
            <h3>{current_total}</h3>
            <p>服务器记录</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 主要内容区域
    if not all_results:
        st.warning("没有数据可显示。请点击'更新数据'按钮获取数据。")
        return
    
    # 构建树结构
    root = build_tree_structure(all_results)
    
    if not root:
        st.error("无法构建树结构，请检查数据格式。")
        return
    
    # 创建选项卡
    tab1, tab2, tab3 = st.tabs(["🌳 树形图", "📊 数据表", "🔍 节点详情"])
    
    with tab1:
        st.subheader("交互式树形结构")
        
        # 显示树结构信息
        def get_tree_info(node, level=0):
            level_info = {}
            if level not in level_info:
                level_info[level] = 0
            level_info[level] += 1
            
            for child in node.get('children', []):
                child_info = get_tree_info(child, level + 1)
                for l, count in child_info.items():
                    level_info[l] = level_info.get(l, 0) + count
            
            return level_info
        
        tree_info = get_tree_info(root)
        
        # 显示层级信息
        info_cols = st.columns(len(tree_info))
        for i, (level, count) in enumerate(tree_info.items()):
            with info_cols[i]:
                st.metric(f"第 {level} 层", f"{count} 个节点")
        
        # 创建并显示树形图
        fig = create_tree_visualization(root)
        if fig:
            # 配置图表交互选项
            config = {
                'displayModeBar': True,  # 显示工具栏
                'displaylogo': False,    # 隐藏Plotly logo
                'modeBarButtonsToAdd': [
                    'pan2d',      # 拖拽
                    'zoomIn2d',   # 放大
                    'zoomOut2d',  # 缩小
                    'autoScale2d', # 自动缩放
                    'resetScale2d' # 重置缩放
                ],
                'modeBarButtonsToRemove': ['lasso2d', 'select2d'],  # 移除不需要的工具
                'scrollZoom': True,      # 启用滚轮缩放
                'doubleClick': 'reset',  # 双击重置视图
                'showTips': True         # 显示提示
            }
            
            # 显示图表并捕获点击事件
            clicked_data = st.plotly_chart(fig, use_container_width=True, config=config, 
                                         on_select="rerun", key="tree_chart")
            
            # 检查是否有点击事件，如果有则弹出信息框
            if clicked_data and 'selection' in clicked_data and clicked_data['selection']:
                # 获取点击的节点
                points = clicked_data['selection']['points']
                if points:
                    # 获取第一个点击的节点
                    point = points[0]
                    clicked_node_id = None
                    
                    # 尝试从多个来源获取节点ID
                    if 'customdata' in point:
                        # 从customdata获取节点ID
                        clicked_node_id = int(point['customdata'])
                    elif 'pointIndex' in point:
                        # 从pointIndex获取节点ID
                        point_index = point['pointIndex']
                        # 从节点文本中获取节点ID
                        node_data = fig.data[-1]  # 节点数据是最后一个trace
                        if point_index < len(node_data.text):
                            clicked_node_id = int(node_data.text[point_index])
                    elif 'text' in point:
                        # 直接从text获取节点ID
                        clicked_node_id = int(point['text'])
                    
                    if clicked_node_id is not None:
                        # 找到对应的节点详细信息
                        clicked_node = next((result for result in all_results if result['index'] == clicked_node_id), None)
                        if clicked_node:
                                # 弹出节点信息框
                                with st.container():
                                    st.markdown("---")
                                    # 创建一个突出的弹出框样式
                                    st.markdown(f"""
                                    <div style="
                                        position: relative;
                                        border: 3px solid #667eea;
                                        border-radius: 15px;
                                        padding: 20px;
                                        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                                        margin: 20px 0;
                                        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
                                        animation: fadeIn 0.3s ease-in;
                                    ">
                                        <div style="
                                            position: absolute;
                                            top: -15px;
                                            left: 20px;
                                            background: #667eea;
                                            color: white;
                                            padding: 5px 15px;
                                            border-radius: 20px;
                                            font-size: 14px;
                                            font-weight: bold;
                                        ">
                                            点击的节点信息
                                        </div>
                                        <div style="margin-top: 15px;">
                                            <h3 style="color: #667eea; margin-bottom: 15px;">🔍 节点 {clicked_node['index']} 详细信息</h3>
                                            <div style="margin-bottom: 15px;">
                                                <div style="margin-bottom: 8px;"><strong>父节点:</strong> {clicked_node.get('parent', '无')}</div>
                                                <div style="margin-bottom: 8px;"><strong>名称:</strong> {clicked_node.get('name', '未知')}</div>
                                                <div style="margin-bottom: 8px;"><strong>测试结果:</strong> {clicked_node.get('test', '无数据')}</div>
                                                <div style="margin-bottom: 8px;"><strong>训练结果:</strong> {clicked_node.get('train', '无数据')}</div>
                                                <div style="margin-bottom: 8px;"><strong>层级:</strong> 第 {clicked_node.get('level', '未知')} 层</div>
                                                <div style="margin-bottom: 8px;"><strong>评分:</strong> {clicked_node.get('score', '无数据')}</div>
                                            </div>
                                            <div style="margin-top: 15px;">
                                                <strong>描述:</strong><br/>
                                                <div style="background: #f8f9fa; padding: 10px; border-radius: 8px; margin-top: 5px;">
                                                    {clicked_node.get('motivation', '无描述')}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <style>
                                        @keyframes fadeIn {{
                                            from {{ opacity: 0; transform: translateY(-10px); }}
                                            to {{ opacity: 1; transform: translateY(0); }}
                                        }}
                                    </style>
                                    """, unsafe_allow_html=True)
                                    
                                    # 添加关闭按钮
                                    col1, col2, col3 = st.columns([1, 1, 1])
                                    with col2:
                                        if st.button("✖️ 关闭信息框", key="close_popup", type="primary"):
                                            st.rerun()
            
            # 在图表下方添加节点选择器（作为备选方案）
            st.markdown("---")
            st.markdown("### 🔍 或手动选择节点查看详情")
            
            # 创建选择器
            node_options = {result['index']: f"节点 {result['index']} - {result.get('name', '未知')}" 
                           for result in all_results}
            selected_node_id = st.selectbox(
                "选择节点查看详情：",
                options=list(node_options.keys()),
                format_func=lambda x: node_options[x],
                key="manual_node_selector"
            )
            
            # 显示手动选择的节点信息
            if selected_node_id:
                selected_node = next((result for result in all_results if result['index'] == selected_node_id), None)
                if selected_node:
                    with st.expander(f"📋 节点 {selected_node['index']} 详细信息", expanded=True):
                        display_node_details(selected_node)
        else:
            st.error("无法创建树形图")
    
    with tab2:
        st.subheader("数据表格")
        
        # 创建数据表
        df_data = []
        for result in all_results:
            df_data.append({
                '节点ID': result['index'],
                '名称': result.get('name', '未知'),
                '父节点': result.get('parent', '无'),
                '训练结果': result.get('train', '无数据'),
                '测试结果': result.get('test', '无数据'),
                '评分': result.get('score', '无数据'),
                '描述': result.get('motivation', '无描述')[:50] + '...' if len(result.get('motivation', '')) > 50 else result.get('motivation', '无描述')
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
        
        # 下载按钮
        csv = df.to_csv(index=False, encoding='utf-8')
        st.download_button(
            label="📥 下载CSV",
            data=csv,
            file_name=f"tree_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with tab3:
        st.subheader("节点详情查看")
        
        # 节点选择器
        node_ids = [result['index'] for result in all_results]
        selected_node_id = st.selectbox("选择节点", node_ids, format_func=lambda x: f"节点 {x}")
        
        # 显示选中节点的详情
        selected_node = next((result for result in all_results if result['index'] == selected_node_id), None)
        if selected_node:
            display_node_details(selected_node)
            
            # 显示子节点
            children = [result for result in all_results if result.get('parent') == selected_node_id]
            if children:
                st.subheader("子节点")
                for child in children:
                    with st.expander(f"节点 {child['index']} - {child.get('name', '未知')}"):
                        display_node_details(child)
    
    # 侧边栏附加信息
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 系统状态")
    
    # 显示缓存状态
    cache_time = cache_data.get("last_updated", "未知")
    st.sidebar.info(f"缓存更新时间: {cache_time}")
    
    # 显示连接状态
    try:
        total_records = get_total_records()
        if total_records > 0:
            st.sidebar.success("✅ 服务器连接正常")
        else:
            st.sidebar.warning("⚠️ 服务器无数据")
    except:
        st.sidebar.error("❌ 服务器连接失败")
    
    # 帮助信息
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 使用帮助")
    st.sidebar.markdown("""
    - **更新数据**: 点击更新按钮获取最新数据
    - **树形图**: 查看模型层次结构
    - **数据表**: 浏览所有节点信息
    - **节点详情**: 查看单个节点详细信息
    """)

if __name__ == "__main__":
    main() 