import pandas as pd
import numpy as np
from scipy.fft import fft, fftfreq
import argparse

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

# 入力信号を最大値で正規化する関数
def normalize_signal(signal, max_val):
    if max_val != 0:
        return signal / max_val
    else:
        return signal

# FFTを実行する関数 (信号の平均値を取り除き、振幅を取得)
def perform_fft(signal, sample_spacing=1.0):
    signal_centered = signal - np.mean(signal)  # オフセットを取り除く
    N = len(signal_centered)
    yf = fft(signal_centered)
    xf = fftfreq(N, sample_spacing)[:N//2]  # 正の周波数成分のみ取得
    
    amplitude = 2.0/N * np.abs(yf[:N//2])  # 振幅
    return xf, amplitude

# 与えられた周波数に最も近い振幅を見つける関数
def get_amplitude_at_frequency(xf, amplitude, target_freq):
    idx = (np.abs(xf - target_freq)).argmin()  # target_freqに最も近いインデックスを取得
    return xf[idx], amplitude[idx]

# 振幅ゲイン（dB）を計算する関数
def calculate_amplitude_gain(input_amplitude, output_amplitude):
    gain = output_amplitude / input_amplitude  # 振幅比
    gain_db = 20 * np.log10(gain)  # dBに変換
    return gain_db

# メインの処理
def main():
    parser = argparse.ArgumentParser(description='Calculate amplitude change at a given frequency for input and output signals.')
    parser.add_argument('file_path_input', type=str, help='Path to the input CSV file (sine wave).')
    parser.add_argument('file_path_output', type=str, help='Path to the output CSV file (drone altitude speed).')
    parser.add_argument('--column1', type=str, required=True, help='Column name to analyze in the input file.')
    parser.add_argument('--column2', type=str, required=True, help='Column name to analyze in the output file.')
    parser.add_argument('--start_time', type=float, required=True, help='Start time in seconds.')
    parser.add_argument('--duration', type=float, required=True, help='Duration of the time range in seconds.')
    parser.add_argument('--target_frequency', type=float, required=True, help='Target frequency to analyze.')
    parser.add_argument('--input_max_value', type=float, required=True, help='input signal max value.')


    args = parser.parse_args()

    # 入力データを読み込む
    df_input = load_csv(args.file_path_input)

    # 出力データを読み込む
    df_output = load_csv(args.file_path_output)

    # 時間範囲を指定
    start_time_sec = args.start_time
    end_time_sec = start_time_sec + args.duration

    # フィルタリングしたデータ
    filtered_input = filter_by_time(df_input, start_time_sec, end_time_sec)
    filtered_output = filter_by_time(df_output, start_time_sec, end_time_sec)

    # 入力信号を正規化
    input_signal = normalize_signal(filtered_input[args.column1].values, args.input_max_value)  # 入力信号を正規化
    output_signal = filtered_output[args.column2].values  # 出力信号（そのまま）

    # サンプル間隔を計算
    sample_spacing = (filtered_input['timestamp'].iloc[1] - filtered_input['timestamp'].iloc[0]).total_seconds()

    # FFTを実行して振幅を取得
    xf_input, amplitude_input = perform_fft(input_signal, sample_spacing)
    xf_output, amplitude_output = perform_fft(output_signal, sample_spacing)

    # 指定された周波数での入力振幅と出力振幅を取得
    freq_input, amp_input_at_freq = get_amplitude_at_frequency(xf_input, amplitude_input, args.target_frequency)
    freq_output, amp_output_at_freq = get_amplitude_at_frequency(xf_output, amplitude_output, args.target_frequency)

    # 振幅ゲインを計算
    amplitude_gain_db = calculate_amplitude_gain(amp_input_at_freq, amp_output_at_freq)

    # 結果を出力
    print(f"指定された周波数 {args.target_frequency} Hz での正規化後の入力振幅: {amp_input_at_freq}")
    print(f"指定された周波数 {args.target_frequency} Hz での出力振幅: {amp_output_at_freq}")
    print(f"指定された周波数 {args.target_frequency} Hz での振幅ゲイン: {amplitude_gain_db} dB")

if __name__ == "__main__":
    main()
