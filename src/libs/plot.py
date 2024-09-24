import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

class HakoTimelineAnalyzer:
    def __init__(self, time_colname='timestamp'):
        self.time_colname = time_colname

    def validate_and_merge_time_columns(self, df_list):
        # 全てのデータフレームのTIME列を比較して、共通の値を見つける
        common_times = set(df_list[0][self.time_colname])
        for df in df_list[1:]:
            common_times.intersection_update(set(df[self.time_colname]))

        if len(common_times) < len(df_list[0][self.time_colname]):
            print(f"Warning: Only {len(common_times)} common time points found. Others will be skipped.")

        # 共通のTIME値に基づいて各データフレームをフィルタリング
        filtered_df_list = []
        for df in df_list:
            filtered_df = df[df[self.time_colname].isin(common_times)]
            filtered_df_list.append(filtered_df)

        return filtered_df_list

    def load_and_process_files(self, file_paths, is_multiple_files):
        df_list = []
        for file_path in file_paths:
            df = pd.read_csv(file_path)
            if is_multiple_files:
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                df.rename(columns=lambda x: f"{file_name}.{x}" if x != self.time_colname else x, inplace=True)
            df_list.append(df)
        return df_list

    def plot(self, df, columns, start_time=0, duration=sys.maxsize, diff=False):
        # TIME列の差分計算が指定されている場合は処理を行う
        if diff:
            df[self.time_colname] = (df[self.time_colname] - df[self.time_colname].iloc[0]) / 1e6  # μsから秒に変換

        # フィルタリング
        end_time = start_time + duration
        filtered_df = df[(df[self.time_colname] >= start_time) & (df[self.time_colname] <= end_time)]

        # グラフの描画
        plt.figure(figsize=(10, 6))

        # 複数の列のデータをプロット
        for column_name in columns:
            plt.plot(filtered_df[self.time_colname].to_numpy(), filtered_df[column_name].to_numpy(), label=column_name)

        plt.title('Data over Time')
        plt.xlabel('Time (seconds)' if diff else 'Time')
        plt.ylabel('Values')
        plt.grid(True)
        plt.legend()
        plt.savefig('plot.png')
        plt.close()

