import pandas as pd
import matplotlib.pyplot as plt
import argparse
import sys
import os

timecolumn = 'timestamp'

def read_and_preprocess(file_paths, start_time, duration, diff):
    df_list = []

    for file_path in file_paths:
        df = pd.read_csv(file_path)

        # --diff オプションが指定されている場合、時間差分を計算し、単位を秒に変換
        if diff:
            df[timecolumn] = (df[timecolumn] - df[timecolumn].iloc[0]) / 1e6

        # 時間範囲でフィルタリング
        end_time = start_time + duration
        filtered_df = df[(df[timecolumn] >= start_time) & (df[timecolumn] <= end_time)]

        df_list.append(filtered_df)

    return df_list

def prepare_scatter_data(df_list, independent_var, dependent_var):
    if len(df_list) > 1:
        independent_df = df_list[0] if independent_var in df_list[0] else df_list[1]
        dependent_df = df_list[1] if independent_var in df_list[0] else df_list[0]
    else:
        independent_df = df_list[0]
        dependent_df = df_list[0]

    scatter_data = []
    last_index = 0

    for _, row in independent_df.iterrows():
        closest_time = row[timecolumn]
        closest_value = None

        for idx in range(last_index, len(dependent_df)):
            dependent_time = dependent_df.iloc[idx][timecolumn]

            if dependent_time >= closest_time:
                closest_value = dependent_df.iloc[idx][dependent_var]
                last_index = idx
                break

        if closest_value is not None:
            scatter_data.append({
                timecolumn: closest_time,
                independent_var: row[independent_var],
                dependent_var: closest_value
            })
        else:
            break

    return pd.DataFrame(scatter_data)

def normalize_series(data):
    min_val = data.min()
    max_val = data.max()
    return (data - min_val) / (max_val - min_val)

def prepare_line_data(df_list, independent_var, dependent_var):
    if len(df_list) == 1:
        line_data = df_list[0]
    else:
        independent_df = df_list[0] if independent_var in df_list[0] else df_list[1]
        dependent_df = df_list[1] if independent_var in df_list[0] else df_list[0]
        line_data = pd.merge_asof(independent_df.sort_values(timecolumn), dependent_df.sort_values(timecolumn), on=timecolumn)

    line_data = line_data[[independent_var, dependent_var, timecolumn]].dropna()
    return line_data

def analyze_causal_relationship(df, independent_var, dependent_var, graph_type, invert_independent, invert_dependent):
    if invert_independent:
        # 独立変数が含まれるデータフレームを特定して反転
        for d in df:
            if independent_var in d.columns:
                d[independent_var] = -d[independent_var]

    if invert_dependent:
        # 従属変数が含まれるデータフレームを特定して反転
        for d in df:
            if dependent_var in d.columns:
                d[dependent_var] = -d[dependent_var]

    if graph_type == 'scatter':
        return prepare_scatter_data(df, independent_var, dependent_var)
    elif graph_type == 'line':
        return prepare_line_data(df, independent_var, dependent_var)

def plot_data(df, independent_var, dependent_var, graph_type):
    fig, ax1 = plt.subplots(figsize=(10, 6))

    if graph_type == 'scatter':
        plt.scatter(df[independent_var], df[dependent_var], color='purple')
        plt.xlabel(independent_var)
        plt.ylabel(dependent_var)
        plt.title(f'{independent_var} vs {dependent_var} - {graph_type.title()} Plot')
        plt.grid(True)
        plt.legend()
        plt.grid(True)
    elif graph_type == 'line':
        ax1.plot(df[timecolumn], df[independent_var], color='blue', label=independent_var)
        ax1.set_xlabel(timecolumn)
        ax1.set_ylabel(independent_var, color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        ax2 = ax1.twinx()
        ax2.plot(df[timecolumn], df[dependent_var], color='orange', label=dependent_var)
        ax2.set_ylabel(dependent_var, color='orange')
        ax2.tick_params(axis='y', labelcolor='orange')

        plt.title(f'{independent_var} and {dependent_var} over Time')
        ax1.grid(True)

        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='upper left')

    plt.show()

# コマンドライン引数の処理
parser = argparse.ArgumentParser(description="Analyze and plot causal relationships from time series data.")
parser.add_argument("file_paths", nargs='+', help="Path(s) to the CSV file(s)")
parser.add_argument("--independent", required=True, help="Independent variable name")
parser.add_argument("--dependent", required=True, help="Dependent variable name")
parser.add_argument("--graph_type", choices=['scatter', 'line'], default='scatter', help="Type of graph to plot")
parser.add_argument("--start_time", type=float, default=0, help="Start time for analysis")
parser.add_argument("--duration", type=float, default=60, help="Duration for analysis")
parser.add_argument("--diff", action='store_true', help="Calculate time differences")
parser.add_argument("--invert_independent", action='store_true', help="Invert the sign of the independent variable")
parser.add_argument("--invert_dependent", action='store_true', help="Invert the sign of the dependent variable")
args = parser.parse_args()

# データの読み込みと前処理
df = read_and_preprocess(args.file_paths, args.start_time, args.duration, args.diff)

# 因果関係の分析
analyzed_data = analyze_causal_relationship(df, args.independent, args.dependent, args.graph_type, args.invert_independent, args.invert_dependent)

# データのプロット
plot_data(analyzed_data, args.independent, args.dependent, args.graph_type)
