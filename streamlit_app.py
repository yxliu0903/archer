import streamlit as st
import os
import glob

# 设置页面配置
st.set_page_config(page_title="MAD Lab 分析查看器", layout="wide")

st.title("🧪 MAD Lab 分析文件查看器")


# 分析文件目录
analysis_dir = './thinker'

# 获取所有txt文件
txt_files = glob.glob(os.path.join(analysis_dir, '*.txt'))
txt_files.sort(reverse=True)  # 按时间倒序排列

if txt_files:
    # 文件选择
    file_names = [os.path.basename(f) for f in txt_files]
    selected_file = st.selectbox("选择要查看的分析文件:", file_names)
    
    if selected_file:
        file_path = os.path.join(analysis_dir, selected_file)
        
        # 显示文件名
        st.subheader(f"📄 {selected_file}")
        
        # 读取并显示文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 分离表格和文本内容
            lines = content.split('\n')
            current_content = []
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                # 检查是否是表格开始
                if 'Unnamed: 0' in line and 'Compress' in line:
                    # 先显示之前积累的文本内容
                    if current_content:
                        text_content = '\n'.join(current_content)
                        if text_content.strip():
                            st.markdown(f"```\n{text_content}\n```")
                        current_content = []
                    
                    # 处理表格
                    st.markdown("### 📊 性能数据表")
                    
                    # 创建表格头
                    table_data = []
                    table_data.append(['模型名称', 'Compress', 'Context Recall', 'Fuzzy Recall', 'Memorize', 'Noisy Recall', 'Selective Copy', 'Average'])
                    
                    # 查找表格数据行
                    j = i + 1
                    while j < len(lines):
                        data_line = lines[j].strip()
                        if data_line and data_line[0].isdigit():
                            parts = data_line.split()
                            if len(parts) >= 7:
                                model_name = ' '.join(parts[1:-6])
                                metrics = parts[-6:]
                                # 格式化数字并计算平均值
                                formatted_metrics = []
                                numeric_metrics = []
                                for m in metrics:
                                    try:
                                        value = float(m)
                                        formatted_metrics.append(f"{value:.4f}")
                                        numeric_metrics.append(value)
                                    except:
                                        formatted_metrics.append(m)
                                        numeric_metrics.append(0)
                                
                                # 计算平均值
                                if numeric_metrics:
                                    average = sum(numeric_metrics) / len(numeric_metrics)
                                    formatted_metrics.append(f"{average:.4f}")
                                else:
                                    formatted_metrics.append("N/A")
                                    
                                table_data.append([model_name] + formatted_metrics)
                            j += 1
                        else:
                            break
                    
                    # 显示表格
                    if len(table_data) > 1:
                        # 对数据行进行排序，将baseline模型放在前面
                        data_rows = table_data[1:]  # 除去表头
                        baseline_rows = []
                        other_rows = []
                        
                        for row in data_rows:
                            model_name = row[0]
                            if model_name == 'delta_net_4layer':
                                baseline_rows.insert(0, row)  # delta_net_4layer放在第一行
                            elif model_name == 'gated_delta_net_4layer':
                                baseline_rows.append(row)     # gated_delta_net_4layer放在第二行
                            else:
                                other_rows.append(row)
                        
                        # 重新组织数据：baseline在前，其他在后
                        sorted_data = baseline_rows + other_rows
                        
                        # 使用HTML表格来支持背景色
                        html_table = ['<table style="width:100%; border-collapse: collapse;">']
                        
                        # 表头
                        html_table.append('<thead>')
                        html_table.append('<tr style="background-color: #f0f0f0;">')
                        for header in table_data[0]:
                            html_table.append(f'<th style="border: 1px solid #ddd; padding: 8px; text-align: left;">{header}</th>')
                        html_table.append('</tr>')
                        html_table.append('</thead>')
                        
                        # 表体
                        html_table.append('<tbody>')
                        for row in sorted_data:
                            model_name = row[0]
                            # 为baseline模型设置灰色背景
                            if model_name in ['delta_net_4layer', 'gated_delta_net_4layer']:
                                html_table.append('<tr style="background-color: #e8e8e8;">')
                            else:
                                html_table.append('<tr>')
                            
                            for cell in row:
                                html_table.append(f'<td style="border: 1px solid #ddd; padding: 8px;">{cell}</td>')
                            html_table.append('</tr>')
                        html_table.append('</tbody>')
                        html_table.append('</table>')
                        
                        st.markdown('\n'.join(html_table), unsafe_allow_html=True)
                    
                    i = j
                else:
                    # 普通文本行，加入到当前内容
                    current_content.append(lines[i])
                    i += 1
            
            # 显示剩余的文本内容
            if current_content:
                text_content = '\n'.join(current_content)
                if text_content.strip():
                    st.markdown(f"```\n{text_content}\n```")
            
        except Exception as e:
            st.error(f"读取文件时出错: {e}")
else:
    st.warning("在analysis目录中没有找到任何txt文件") 