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
    
    return xf, amplitude, phase

# FFTの結果を保存する関数
def save_fft_results(xf, amplitude, phase, output_file):
    fft_df = pd.DataFrame({
        'Frequency (Hz)': xf,
        'Amplitude': amplitude,
        'Phase (radians)': phase
    })
    fft_df.to_csv(output_file, index=False)
    print(f"FFT結果を {output_file} に保存しました。")

# 振幅をプロットする関数（対数スケール）
def plot_amplitude(xf, amplitude, column_name, output_image="fft_amplitude_plot.png"):
    plt.figure()
    plt.plot(xf, amplitude)
    plt.title(f'Amplitude of FFT of {column_name}')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.xscale('log')  # X軸を対数スケールに設定
    plt.yscale('log')  # Y軸を対数スケールに設定
    plt.grid(True, which="both", ls="--")
    plt.savefig(output_image)
    print(f"振幅プロットを {output_image} に保存しました。")

# 位相をプロットする関数
def plot_phase(xf, phase, column_name, output_image="fft_phase_plot.png"):
    plt.figure()
    plt.plot(xf, phase)
    plt.title(f'Phase of FFT of {column_name}')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Phase (radians)')
    plt.xscale('log')  # X軸を対数スケールに設定
    plt.grid(True, which="both", ls="--")
    plt.savefig(output_image)
    print(f"位相プロットを {output_image} に保存しました。")

# メインの処理
def main():
    parser = argparse.ArgumentParser(description='Perform FFT on specified time range and column in CSV.')
    parser.add_argument('file_path', type=str, help='Path to the CSV file.')
    parser.add_argument('--column', type=str, required=True, help='column name.')
    parser.add_argument('--start_time', type=float, required=True, help='Start time in seconds.')
    parser.add_argument('--duration', type=float, required=True, help='Duration of the time range in seconds.')
    parser.add_argument('--output', type=str, required=True, help='Output CSV file to save the FFT results.')
    parser.add_argument('--amplitude_plot_output', type=str, default="fft_amplitude_plot.png", help='Output image file for the FFT amplitude plot.')
    parser.add_argument('--phase_plot_output', type=str, default="fft_phase_plot.png", help='Output image file for the FFT phase plot.')

    args = parser.parse_args()

    # データを読み込む
    df = load_csv(args.file_path)

    # 時間範囲を指定
    start_time_sec = args.start_time
    end_time_sec = start_time_sec + args.duration

    # フィルタリングしたデータ
    filtered_df = filter_by_time(df, start_time_sec, end_time_sec)

    # 対象となるカラム名を指定
    column_name = args.column

    # 指定したカラムに対してFFTを実行
    signal = filtered_df[column_name].values

    # サンプル間隔を動的に計算
    sample_spacing = (filtered_df['timestamp'].iloc[1] - filtered_df['timestamp'].iloc[0]).total_seconds()

    # FFTを実行（オフセットを取り除いて計算）
    xf, amplitude, phase = perform_fft(signal, sample_spacing)

    # 結果を保存
    save_fft_results(xf, amplitude, phase, args.output)

    # 振幅のプロットを作成してファイルに保存
    plot_amplitude(xf, amplitude, column_name, args.amplitude_plot_output)

    # 位相のプロットを作成してファイルに保存
    plot_phase(xf, phase, column_name, args.phase_plot_output)

if __name__ == "__main__":
    main()
