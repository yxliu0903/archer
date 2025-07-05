#!/usr/bin/env python3
"""
Model Performance Comparison Table Generator

This script generates a beautiful HTML table comparing model performance 
from training loss data and evaluation metrics.

Usage:
    python model_comparison.py --train_csv path/to/train.csv --eval_csv path/to/eval.csv --output output.html

Requirements:
    pip install pandas argparse
"""

import pandas as pd
import argparse
import os
import webbrowser
from typing import Dict, List, Tuple, Optional

def read_training_data(train_csv_path: str) -> Dict[str, float]:
    """
    Read training CSV and extract final loss for each model.
    
    Args:
        train_csv_path: Path to training CSV file
        
    Returns:
        Dictionary mapping model names to final loss values
    """
    try:
        df = pd.read_csv(train_csv_path)
        final_losses = {}
        
        for _, row in df.iterrows():
            model_name = row.iloc[0]  # First column is model name
            if pd.isna(model_name) or model_name == '':
                continue
                
            # Find the last non-null value in the row (final loss)
            values = row.iloc[1:].dropna()
            if len(values) > 0:
                final_losses[model_name] = float(values.iloc[-1])
        
        print(f"✓ Loaded training data for {len(final_losses)} models")
        return final_losses
        
    except Exception as e:
        print(f"✗ Error reading training CSV: {e}")
        return {}

def read_evaluation_data(eval_csv_path: str) -> Tuple[pd.DataFrame, List[str]]:
    """
    Read evaluation CSV and return metrics data.
    
    Args:
        eval_csv_path: Path to evaluation CSV file
        
    Returns:
        Tuple of (DataFrame with evaluation data, list of metric names)
    """
    try:
        df = pd.read_csv(eval_csv_path, header=None)
        
        # First column is model names, rest are metrics
        model_names = df.iloc[:, 0].tolist()
        metric_values = df.iloc[:, 1:].values
        
        # Create metric names if not provided (assuming standard metrics)
        metric_names = [
            'arc_challenge', 'arc_easy', 'boolq', 'fda', 'hellaswag', 
            'lambada_openai', 'openbookqa', 'piqa', 'social_iqa', 
            'squad_completion', 'swde', 'winogrande'
        ]
        
        # Adjust metric names if we have different number of columns
        num_metrics = metric_values.shape[1]
        if num_metrics != len(metric_names):
            metric_names = [f'metric_{i+1}' for i in range(num_metrics)]
        
        # Create DataFrame
        eval_data = pd.DataFrame(metric_values, columns=metric_names)
        eval_data.insert(0, 'model', model_names)
        
        print(f"✓ Loaded evaluation data for {len(model_names)} models with {num_metrics} metrics")
        return eval_data, metric_names
        
    except Exception as e:
        print(f"✗ Error reading evaluation CSV: {e}")
        return pd.DataFrame(), []

def combine_data(final_losses: Dict[str, float], eval_data: pd.DataFrame, metric_names: List[str]) -> pd.DataFrame:
    """
    Combine training and evaluation data.
    
    Args:
        final_losses: Dictionary of model names to final losses
        eval_data: DataFrame with evaluation metrics
        metric_names: List of metric column names
        
    Returns:
        Combined DataFrame with all data
    """
    combined_data = []
    
    for _, row in eval_data.iterrows():
        model_name = row['model']
        if model_name in final_losses:
            data_row = {
                'model': model_name,
                'final_loss': final_losses[model_name]
            }
            
            # Add all metrics
            for metric in metric_names:
                data_row[metric] = float(row[metric]) if pd.notna(row[metric]) else 0.0
            
            # Calculate average of metrics (excluding final_loss)
            metric_values = [data_row[metric] for metric in metric_names]
            data_row['average'] = sum(metric_values) / len(metric_values)
            
            combined_data.append(data_row)
    
    # Add manual data for gated_delta_net
    gated_data = {
        'model': 'gated_delta_net',
        'final_loss': 4.3772,
        'arc_challenge': 0.168,
        'arc_easy': 0.374,
        'boolq': 0.37,
        'fda': 0.0,
        'hellaswag': 0.282,
        'lambada_openai': 0.002,
        'openbookqa': 0.144,
        'piqa': 0.562,
        'social_iqa': 0.35,
        'squad_completion': 0.004,
        'swde': 0.002,
        'winogrande': 0.456
    }
    
    # Calculate average for gated_delta_net
    gated_metric_values = [gated_data[metric] for metric in metric_names if metric in gated_data]
    gated_data['average'] = sum(gated_metric_values) / len(gated_metric_values)
    
    combined_data.append(gated_data)
    
    df = pd.DataFrame(combined_data)
    # Sort by average score (descending)
    df = df.sort_values('average', ascending=False)
    
    print(f"✓ Combined data for {len(df)} models (including gated_delta_net)")
    return df

def find_best_values(df: pd.DataFrame, metric_names: List[str]) -> Dict[str, float]:
    """Find the best value for each metric."""
    best_values = {}
    
    # For final_loss, lower is better
    best_values['final_loss'] = df['final_loss'].min()
    
    # For all other metrics, higher is better
    for metric in metric_names:
        best_values[metric] = df[metric].max()
    
    best_values['average'] = df['average'].max()
    
    return best_values

def generate_html_table(df: pd.DataFrame, metric_names: List[str], best_values: Dict[str, float], output_path: str):
    """Generate beautiful HTML table."""
    
    baseline_model = None
    gated_model = None
    
    # Find baseline and gated models
    for model in df['model']:
        if model.strip().lower() in ['delta_net', 'baseline', 'base_model']:
            baseline_model = model
        elif model.strip().lower() == 'gated_delta_net':
            gated_model = model
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Model Performance Comparison</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            overflow-x: auto;
            max-width: 100%;
        }}
        
        h1 {{
            color: #2d3748;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .stats-bar {{
            display: flex;
            justify-content: space-around;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border-radius: 15px;
            color: white;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            display: block;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 13px;
            min-width: 1200px;
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        th, td {{
            padding: 12px 8px;
            text-align: center;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        th {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 100;
            text-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }}
        
        .model-name {{
            text-align: left;
            font-weight: 500;
            max-width: 280px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            padding-left: 15px;
        }}
        
        .baseline-row {{
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            border-left: 5px solid #ff6b6b;
            font-weight: 600;
        }}
        
        .baseline-row .model-name {{
            font-weight: bold;
            color: #c53030;
        }}
        
        .gated-row {{
            background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
            border-left: 5px solid #4caf50;
            font-weight: 600;
        }}
        
        .gated-row .model-name {{
            font-weight: bold;
            color: #2e7d32;
        }}
        
        .best-value {{
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            font-weight: bold;
            color: #155724;
            position: relative;
        }}
        
        .best-value::before {{
            content: '★';
            position: absolute;
            top: 2px;
            right: 2px;
            font-size: 10px;
            color: #28a745;
        }}
        
        .metric-header {{
            writing-mode: vertical-rl;
            text-orientation: mixed;
            min-width: 35px;
            height: 120px;
            vertical-align: bottom;
            font-weight: 600;
        }}
        
        tr:nth-child(even) {{
            background-color: #f8fafc;
        }}
        
        tr:hover {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            transform: scale(1.01);
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .numeric {{
            font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
            font-weight: 500;
        }}
        
        .average-col {{
            background: linear-gradient(135deg, #e8f4f8 0%, #d1ecf1 100%);
            font-weight: bold;
            border-left: 3px solid #17a2b8;
        }}
        
        .final-loss-col {{
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            border-left: 3px solid #ffc107;
        }}
        
        .legend {{
            margin-top: 30px;
            padding: 25px;
            background: linear-gradient(135deg, #f8f9ff 0%, #e6f3ff 100%);
            border-radius: 15px;
            font-size: 14px;
            border: 1px solid #e2e8f0;
        }}
        
        .legend h3 {{
            margin-bottom: 15px;
            color: #2d3748;
            font-size: 1.2rem;
        }}
        
        .legend-item {{
            margin-bottom: 8px;
            display: flex;
            align-items: center;
        }}
        
        .legend-indicator {{
            display: inline-block;
            width: 16px;
            height: 16px;
            margin-right: 10px;
            border-radius: 3px;
        }}
        
        .baseline-indicator {{
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            border: 2px solid #ff6b6b;
        }}
        
        .gated-indicator {{
            background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
            border: 2px solid #4caf50;
        }}
        
        .best-indicator {{
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border: 2px solid #28a745;
        }}
        
        .rank-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            margin-right: 8px;
        }}
        
        .rank-1 {{ background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%); color: #8b4513; }}
        .rank-2 {{ background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%); color: #555; }}
        .rank-3 {{ background: linear-gradient(135deg, #cd7f32 0%, #deb887 100%); color: white; }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
                border-radius: 15px;
            }}
            
            h1 {{
                font-size: 2rem;
            }}
            
            .stats-bar {{
                flex-direction: column;
                gap: 15px;
            }}
            
            table {{
                font-size: 11px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏆 Model Performance Comparison</h1>
        
        <div class="stats-bar">
            <div class="stat-item">
                <span class="stat-number">{len(df)}</span>
                <span class="stat-label">Models Compared</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{len(metric_names)}</span>
                <span class="stat-label">Evaluation Metrics</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{df['final_loss'].min():.3f}</span>
                <span class="stat-label">Best Final Loss</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{df['average'].max():.3f}</span>
                <span class="stat-label">Best Average Score</span>
            </div>
        </div>
        
        <table id="resultsTable">
            <thead>
                <tr>
                    <th class="model-name">🎯 Model Name</th>
                    <th class="metric-header final-loss-col">📉 Final Loss</th>"""
    
    # Add metric headers
    for metric in metric_names:
        display_name = metric.replace('_', ' ').title()
        html_template += f'<th class="metric-header">📊 {display_name}</th>'
    
    html_template += '<th class="metric-header average-col">📈 Average</th></tr></thead><tbody>'
    
    # Add data rows
    for idx, (_, row) in enumerate(df.iterrows(), 1):
        is_baseline = baseline_model and row['model'] == baseline_model
        is_gated = gated_model and row['model'] == gated_model
        
        row_class = ''
        if is_baseline:
            row_class = 'baseline-row'
        elif is_gated:
            row_class = 'gated-row'
        
        # Add rank badge
        rank_class = f'rank-{idx}' if idx <= 3 else ''
        rank_badge = f'<span class="rank-badge {rank_class}">#{idx}</span>'
        
        html_template += f'<tr class="{row_class}">'
        html_template += f'<td class="model-name">{rank_badge}{row["model"]}</td>'
        
        # Final loss (lower is better)
        is_best_loss = abs(row['final_loss'] - best_values['final_loss']) < 0.0001
        loss_class = 'best-value' if is_best_loss else ''
        html_template += f'<td class="numeric final-loss-col {loss_class}">{row["final_loss"]:.3f}</td>'
        
        # Metrics (higher is better)
        for metric in metric_names:
            is_best = abs(row[metric] - best_values[metric]) < 0.0001
            metric_class = 'best-value' if is_best else ''
            html_template += f'<td class="numeric {metric_class}">{row[metric]:.3f}</td>'
        
        # Average
        is_best_avg = abs(row['average'] - best_values['average']) < 0.0001
        avg_class = 'best-value' if is_best_avg else ''
        html_template += f'<td class="numeric average-col {avg_class}">{row["average"]:.3f}</td>'
        html_template += '</tr>'
    
    html_template += f"""
            </tbody>
        </table>
        
        <div class="legend">
            <h3>📋 Legend & Information</h3>
            <div class="legend-item">
                <span class="legend-indicator baseline-indicator"></span>
                <strong>Baseline Model (delta_net)</strong> - Original reference model
            </div>
            <div class="legend-item">
                <span class="legend-indicator gated-indicator"></span>
                <strong>Gated Model (gated_delta_net)</strong> - Enhanced gated version
            </div>
            <div class="legend-item">
                <span class="legend-indicator best-indicator"></span>
                <strong>Best Performance ★</strong> - Highest score for each metric (lowest for Final Loss)
            </div>
            <div class="legend-item">
                <span style="margin-right: 26px;"></span>
                <strong>📊 Metrics:</strong> Final Loss (lower is better), All other metrics (higher is better)
            </div>
            <div class="legend-item">
                <span style="margin-right: 26px;"></span>
                <strong>🏆 Ranking:</strong> Models sorted by average performance across all evaluation metrics
            </div>
            <div class="legend-item">
                <span style="margin-right: 26px;"></span>
                <strong>⭐ Top Model:</strong> {df.iloc[0]['model']} (Average: {df.iloc[0]['average']:.3f})
            </div>
        </div>
    </div>
</body>
</html>"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✓ Generated HTML table: {output_path}")
    print(f"✓ Added gated_delta_net with special highlighting")
        
    # Average
    is_best_avg = abs(row['average'] - best_values['average']) < 0.0001
    avg_class = 'best-value' if is_best_avg else ''
    html_template += f'<td class="numeric average-col {avg_class}">{row["average"]:.3f}</td>'
    html_template += '</tr>'
    
    html_template += f"""
            </tbody>
        </table>
        
        <div class="legend">
            <h3>📋 Legend & Information</h3>
            <div class="legend-item">
                <span class="legend-indicator baseline-indicator"></span>
                <strong>Baseline Model (delta_net)</strong> - Original reference model
            </div>
            <div class="legend-item">
                <span class="legend-indicator gated-indicator"></span>
                <strong>Gated Model (gated_delta_net)</strong> - Enhanced gated version
            </div>
            <div class="legend-item">
                <span class="legend-indicator best-indicator"></span>
                <strong>Best Performance ★</strong> - Highest score for each metric (lowest for Final Loss)
            </div>
            <div class="legend-item">
                <span style="margin-right: 26px;"></span>
                <strong>📊 Metrics:</strong> Final Loss (lower is better), All other metrics (higher is better)
            </div>
            <div class="legend-item">
                <span style="margin-right: 26px;"></span>
                <strong>🏆 Ranking:</strong> Models sorted by average performance across all evaluation metrics
            </div>
            <div class="legend-item">
                <span style="margin-right: 26px;"></span>
                <strong>⭐ Top Model:</strong> {df.iloc[0]['model']} (Average: {df.iloc[0]['average']:.3f})
            </div>
        </div>
    </div>
</body>
</html>"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✓ Generated HTML table: {output_path}")
    print(f"✓ Added gated_delta_net with special highlighting")
        
    # Average
    is_best_avg = abs(row['average'] - best_values['average']) < 0.0001
    avg_class = 'best-value' if is_best_avg else ''
    html_template += f'<td class="numeric average-col {avg_class}">{row["average"]:.3f}</td>'
    html_template += '</tr>'
    
    html_template += f"""
            </tbody>
        </table>
        
        <div class="legend">
            <h3>📋 Legend & Information</h3>
            <div class="legend-item">
                <span class="legend-indicator baseline-indicator"></span>
                <strong>Baseline Model</strong> - Reference model for comparison
            </div>
            <div class="legend-item">
                <span class="legend-indicator best-indicator"></span>
                <strong>Best Performance ★</strong> - Highest score for each metric (lowest for Final Loss)
            </div>
            <div class="legend-item">
                <span style="margin-right: 26px;"></span>
                <strong>📊 Metrics:</strong> Final Loss (lower is better), All other metrics (higher is better)
            </div>
            <div class="legend-item">
                <span style="margin-right: 26px;"></span>
                <strong>🏆 Ranking:</strong> Models sorted by average performance across all evaluation metrics
            </div>
            <div class="legend-item">
                <span style="margin-right: 26px;"></span>
                <strong>⭐ Top Model:</strong> {df.iloc[0]['model']} (Average: {df.iloc[0]['average']:.3f})
            </div>
        </div>
    </div>
</body>
</html>"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✓ Generated HTML table: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Generate model comparison table from training and evaluation CSVs')
    parser.add_argument('--train_csv', default="/inspire/hdd/project/qproject-fundationmodel/public/ai-design-ai/back/results/accuracies_df.csv", help='Path to training CSV file (with loss data)')
    parser.add_argument('--eval_csv', default="/inspire/hdd/project/qproject-fundationmodel/public/ai-design-ai/back/results/eval_results_df.csv", help='Path to evaluation CSV file (with metrics)')
    parser.add_argument('--output', default='/inspire/hdd/project/qproject-fundationmodel/public/ai-design-ai/back/results/model_comparison.html', help='Output HTML file path')
    parser.add_argument('--no-open', action='store_true', help='Do not automatically open the HTML file in browser')
    
    args = parser.parse_args()
    
    # Validate input files
    if not os.path.exists(args.train_csv):
        print(f"✗ Training CSV file not found: {args.train_csv}")
        return
    
    if not os.path.exists(args.eval_csv):
        print(f"✗ Evaluation CSV file not found: {args.eval_csv}")
        return
    
    print("🚀 Starting model comparison table generation...")
    print(f"📁 Training data: {args.train_csv}")
    print(f"📁 Evaluation data: {args.eval_csv}")
    print(f"📄 Output: {args.output}")
    print("-" * 50)
    
    # Process data
    final_losses = read_training_data(args.train_csv)
    eval_data, metric_names = read_evaluation_data(args.eval_csv)
    
    if not final_losses or eval_data.empty:
        print("✗ Failed to load data. Please check your CSV files.")
        return
    
    # Combine and analyze
    combined_df = combine_data(final_losses, eval_data, metric_names)
    if combined_df.empty:
        print("✗ No matching models found between training and evaluation data.")
        return
    
    best_values = find_best_values(combined_df, metric_names)
    
    # Generate HTML
    generate_html_table(combined_df, metric_names, best_values, args.output)
    
    print("-" * 50)
    print("🎉 Successfully generated model comparison table!")
    print(f"📊 Top performing model: {combined_df.iloc[0]['model']}")
    print(f"📈 Best average score: {combined_df.iloc[0]['average']:.3f}")
    print(f"📉 Best final loss: {combined_df['final_loss'].min():.3f}")
    
    # Auto-open in browser unless disabled
    if not args.no_open:
        try:
            # Convert to absolute path for better browser compatibility
            output_path = os.path.abspath(args.output)
            file_url = f"file://{output_path}"
            print(f"🌐 Opening in browser: {file_url}")
            webbrowser.open(file_url)
            print("✓ HTML table opened in your default browser!")
        except Exception as e:
            print(f"⚠️  Could not auto-open browser: {e}")
            print(f"💡 Please manually open: {os.path.abspath(args.output)}")
    else:
        print(f"💡 HTML file saved to: {os.path.abspath(args.output)}")
        print("🌐 Use --no-open flag was specified, file not opened automatically")

if __name__ == "__main__":
    main()