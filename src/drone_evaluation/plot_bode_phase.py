import numpy as np
import matplotlib.pyplot as plt
import argparse

# コマンド引数の処理
parser = argparse.ArgumentParser(description='Bode plot generator from CSV file.')
parser.add_argument('csv_file', type=str, help='Path to the CSV file containing frequency, gain, and phase data')
args = parser.parse_args()

# CSVファイルからデータを読み込む
data = np.genfromtxt(args.csv_file, delimiter=',', skip_header=1)

# データの列をそれぞれ取得
frequency = data[:, 0]  # 周波数（Hz）
gain = data[:, 2]       # ゲイン（dB）
phase = data[:, 3]      # 位相（度）

# ボード線図をプロット
plt.figure(figsize=(10, 8))

# ゲインプロット
plt.subplot(2, 1, 1)
plt.semilogx(frequency, gain, 'b', marker='o', linestyle='-', markersize=5)  # 横軸を対数スケールにし、点を表記
plt.xlabel('Frequency (Hz)')
plt.ylabel('Gain (dB)')
plt.title('Bode Plot')
plt.grid(which='both', linestyle='--')

# 位相プロット
plt.subplot(2, 1, 2)
plt.semilogx(frequency, phase, 'r', marker='o', linestyle='-', markersize=5)  # 横軸を対数スケールにし、点を表記
plt.xlabel('Frequency (Hz)')
plt.ylabel('Phase (degrees)')
plt.grid(which='both', linestyle='--')

plt.tight_layout()
plt.show()