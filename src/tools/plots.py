import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import glob
import os

# カレントディレクトリにある全てのPNGファイルを取得
png_files = glob.glob(os.path.join(os.getcwd(), '*.png'))

# 画像が1つ以上ある場合のみ表示
if png_files:
    # 画像数に応じてプロットの行数・列数を決定（2列で表示）
    num_images = len(png_files)
    cols = 2
    rows = (num_images + 1) // cols  # 列に2つずつ表示するための行数計算

    fig, axes = plt.subplots(rows, cols, figsize=(10, 5 * rows))

    # flattenで2次元配列を1次元に変換
    axes = axes.flatten()

    # PNGファイルを1つずつ読み込み、表示
    for i, img_path in enumerate(png_files):
        img = mpimg.imread(img_path)
        axes[i].imshow(img)
        axes[i].set_title(os.path.basename(img_path))  # ファイル名をタイトルに
        axes[i].axis('off')  # 軸を非表示

    # 余ったサブプロットを非表示にする
    for j in range(i + 1, len(axes)):
        axes[j].axis('off')

    plt.tight_layout()
    plt.show()
else:
    print("PNGファイルが見つかりません。")
