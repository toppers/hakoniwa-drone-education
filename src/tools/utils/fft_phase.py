import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
import argparse

# 'Agg'バックエンドを使用してGUI表示を避ける
matplotlib.use('Agg')

# CSVファイルを読み込む関数
def load_csv(filename):
    df = pd.read_csv(filename)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='us')
    return df

# 時間範囲でフィルタリングする関数 (秒単位で指定)
def filter_by_time(df, start_time_sec, end_time_sec):
    start_time = pd.Timestamp(start_time_sec, unit='s')
    end_time = pd.Timestamp(end_time_sec, unit='s')
    return df[(df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)]

# FFTを実行する関数 (信号の平均値を取り除き、位相をアンラップ)
def perform_fft(signal, sample_spacing=1.0):
    signal_centered = signal - np.mean(signal)  # オフセットを取り除く
    N = len(signal_centered)
    yf = fft(signal_centered)
    xf = fftfreq(N, sample_spacing)[:N//2]  # 正の周波数成分のみ取得
    
    amplitude = 2.0/N * np.abs(yf[:N//2])  # 振幅
    phase = np.unwrap(np.angle(yf[:N//2]))  # 位相をアンラップ
    phase_degrees = np.degrees(phase)  # 位相を度に変換
    
    return xf, amplitude, phase_degrees

# FFTの位相差をプロットする関数（位相を度で表示）
def plot_phase_difference(xf, phase_diff, output_image="phase_difference_plot.png"):
    plt.figure()
    plt.plot(xf, phase_diff)
    plt.title('Phase Difference Between Two Signals (Degrees)')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Phase Difference (degrees)')
    plt.xscale('log')
    plt.grid(True)
    plt.savefig(output_image)
    print(f"位相差プロットを {output_image} に保存しました。")

# 線形補間を使って指定された周波数での位相差を推定
def interpolate_phase_difference(xf, phase_diff, target_freq=1.0):
    # target_freqより下の周波数とtarget_freqより上の周波数を見つける
    lower_idx = np.where(xf < target_freq)[0][-1]
    upper_idx = np.where(xf > target_freq)[0][0]
    
    # 周波数と位相差の値
    freq_lower, phase_lower = xf[lower_idx], phase_diff[lower_idx]
    freq_upper, phase_upper = xf[upper_idx], phase_diff[upper_idx]
    
    # 線形補間の式: (y2 - y1) / (x2 - x1) = (y - y1) / (x - x1)
    phase_at_target = phase_lower + (phase_upper - phase_lower) * (target_freq - freq_lower) / (freq_upper - freq_lower)
    
    return phase_at_target

# メインの処理
def main():
    parser = argparse.ArgumentParser(description='Perform FFT on two signals and calculate phase difference.')
    parser.add_argument('file_path1', type=str, help='Path to the first CSV file.')
    parser.add_argument('file_path2', type=str, help='Path to the second CSV file.')
    parser.add_argument('--column1', type=str, required=True, help='Column name to analyze in the first file.')
    parser.add_argument('--column2', type=str, required=True, help='Column name to analyze in the second file.')
    parser.add_argument('--start_time', type=float, required=True, help='Start time in seconds.')
    parser.add_argument('--duration', type=float, required=True, help='Duration of the time range in seconds.')
    parser.add_argument('--output', type=str, required=True, help='Output CSV file to save the phase difference results.')
    parser.add_argument('--plot_output', type=str, default="phase_difference_plot.png", help='Output image file for the phase difference plot.')
    parser.add_argument('--target_frequency', type=float, required=True, help='Frequency at which to calculate the phase difference.')

    args = parser.parse_args()

    # 1つ目のデータを読み込む
    df1 = load_csv(args.file_path1)

    # 2つ目のデータを読み込む
    df2 = load_csv(args.file_path2)

    # 時間範囲を指定
    start_time_sec = args.start_time
    end_time_sec = start_time_sec + args.duration

    # フィルタリングしたデータ
    filtered_df1 = filter_by_time(df1, start_time_sec, end_time_sec)
    filtered_df2 = filter_by_time(df2, start_time_sec, end_time_sec)

    # 対象となるカラムをそれぞれ指定
    column1 = args.column1
    column2 = args.column2

    # 指定したカラムに対してFFTを実行
    signal1 = filtered_df1[column1].values
    signal2 = filtered_df2[column2].values

    # サンプル間隔を動的に計算
    sample_spacing = (filtered_df1['timestamp'].iloc[1] - filtered_df1['timestamp'].iloc[0]).total_seconds()

    # 2つの信号に対してFFTを実行
    xf1, amplitude1, phase1 = perform_fft(signal1, sample_spacing)
    xf2, amplitude2, phase2 = perform_fft(signal2, sample_spacing)

    # 位相差を計算
    phase_diff = phase1 - phase2

    # 結果を保存
    fft_df = pd.DataFrame({
        'Frequency (Hz)': xf1,
        'Phase Difference (degrees)': phase_diff
    })
    fft_df.to_csv(args.output, index=False)
    print(f"位相差結果を {args.output} に保存しました。")

    # 位相差のプロットを作成してファイルに保存
    plot_phase_difference(xf1, phase_diff, args.plot_output)

    # 指定された周波数での位相差を線形補間で計算
    phase_diff_at_target_freq = interpolate_phase_difference(xf1, phase_diff, args.target_frequency)
    print(f"補間された {args.target_frequency} Hz での位相差: {phase_diff_at_target_freq} 度")

if __name__ == "__main__":
    main()
