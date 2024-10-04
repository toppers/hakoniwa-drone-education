import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import sys

def plot_fitting_result(filtered_data, trend, column):
    # フィッティング結果のプロット（デバッグ用）
    plt.plot(filtered_data['timestamp'], filtered_data[column], label=f"Original {column}")
    plt.plot(filtered_data['timestamp'], trend, label=f"Fitted Trend {column}")
    plt.title(f"Fitted Quadratic Trend for {column}")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Values")
    plt.legend()
    plt.show()

def process_data(input_file, start_time, duration, columns, output_file='output.csv'):
    # データの読み込み (CSV形式)
    data = pd.read_csv(input_file)

    # カラム名が存在するか確認
    if not all(col in data.columns for col in columns):
        print(f"Error: Some columns in {columns} not found in the input file.")
        return

    # タイムスタンプを元にデータを範囲でフィルタリング
    end_time = start_time + duration
    filtered_data = data[(data['timestamp'] >= start_time) & (data['timestamp'] <= end_time)].copy()

    if filtered_data.empty:
        print(f"No data found between {start_time} and {end_time}.")
        return

    # 指定されたカラムだけに絞り込む
    filtered_data = filtered_data[['timestamp'] + columns]

    # データフィッティング（低周波領域）
    for column in columns:  # 指定されたカラムに対して実施
        coefficients = np.polyfit(filtered_data['timestamp'], filtered_data[column], 3)
        cubic_trend = np.polyval(coefficients, filtered_data['timestamp'])

        plot_fitting_result(filtered_data, cubic_trend, column)

        # トレンドを差し引き
        filtered_data[column] = filtered_data[column] - cubic_trend

    # ノーマライズ (0-1の範囲にスケール)
    scaler = MinMaxScaler()
    filtered_data[columns] = scaler.fit_transform(filtered_data[columns])

    # 結果を CSV に出力
    filtered_data.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")

if __name__ == "__main__":
    # 引数のパース
    if len(sys.argv) < 5:
        print("Usage: python script.py <input_file> <start_time> <duration> <columns> [output_file]")
        print("Example: python script.py data.csv 10 5 sensor_data1,sensor_data2 output.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    start_time = int(float(sys.argv[2]) * 1000000.0)
    duration = int(float(sys.argv[3]) * 1000000.0)

    # カラム名はカンマ区切りで渡されるため、リストに変換
    columns = sys.argv[4].split(',')

    # 出力ファイル名が指定されている場合はそれを使用
    output_file = sys.argv[5] if len(sys.argv) > 5 else 'output.csv'

    # データ処理の実行
    process_data(input_file, start_time, duration, columns, output_file)
