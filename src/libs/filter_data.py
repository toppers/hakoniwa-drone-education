import numpy as np
import pandas as pd
import sys

def process_data(input_file, start_time, duration, columns, output_file='output.csv', inverse=False):
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

    # タイムスタンプを0始まりに調整
    filtered_data['timestamp'] = filtered_data['timestamp'] - start_time

    # --inverse オプションが指定された場合、指定したカラムのデータ値を符号判定
    if inverse:
        for column in columns:
            filtered_data[column] = filtered_data[column] * -1

    # 結果を CSV に出力
    filtered_data.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")

if __name__ == "__main__":
    # 引数のパース
    if len(sys.argv) < 5:
        print("Usage: python script.py <input_file> <start_time> <duration> <columns> [output_file] [--inverse]")
        print("Example: python script.py data.csv 10 5 sensor_data1,sensor_data2 output.csv --inverse")
        sys.exit(1)

    input_file = sys.argv[1]
    start_time = int(float(sys.argv[2]) * 1000000.0)
    duration = int(float(sys.argv[3]) * 1000000.0)

    # カラム名はカンマ区切りで渡されるため、リストに変換
    columns = sys.argv[4].split(',')

    # 出力ファイル名が指定されている場合はそれを使用
    output_file = sys.argv[5] if len(sys.argv) > 5 and not sys.argv[5].startswith('--') else 'output.csv'

    # --inverse オプションが指定されているか確認
    inverse = '--inverse' in sys.argv

    # データ処理の実行
    process_data(input_file, start_time, duration, columns, output_file, inverse)
