import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider
from PyQt5.QtCore import Qt
from analyze_model import TransParser
import matplotlib.pyplot as plt
import control as ctrl
import matplotlib
import numpy as np

# matplotlibのバックエンドをPyQtと連携
matplotlib.use('Qt5Agg')

global tfd

class PIDSliderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.saved_x_limit = 1
        self.saved_y_limit = 1

        # matplotlibのFigureとAxisを初期化
        self.figure, self.ax = plt.subplots()
        plt.ion()  # インタラクティブモードを有効化
        plt.show()  # 最初に一度だけFigureを表示

        # TransParserから初期値を取得
        self.kp_init = tfd.constants.get("VAlt_Kp", 0) * 10  # 10倍してスライダー用に変換
        self.ki_init = tfd.constants.get("VAlt_Ki", 0) * 10
        self.kd_init = tfd.constants.get("VAlt_Kd", 0) * 10

        # 初期値をスライダーに反映
        self.slider_p.setValue(int(self.kp_init))
        self.slider_i.setValue(int(self.ki_init))
        self.slider_d.setValue(int(self.kd_init))


    def initUI(self):
        layout = QVBoxLayout()

        # P, I, D ラベルとスライダーの作成
        self.label_p = QLabel("P: 0", self)
        layout.addWidget(self.label_p)
        self.slider_p = QSlider(Qt.Horizontal, self)
        self.slider_p.setMinimum(0)
        self.slider_p.setMaximum(100)
        self.slider_p.valueChanged.connect(self.update_p)
        layout.addWidget(self.slider_p)

        self.label_i = QLabel("I: 0", self)
        layout.addWidget(self.label_i)
        self.slider_i = QSlider(Qt.Horizontal, self)
        self.slider_i.setMinimum(0)
        self.slider_i.setMaximum(100)
        self.slider_i.valueChanged.connect(self.update_i)
        layout.addWidget(self.slider_i)

        self.label_d = QLabel("D: 0", self)
        layout.addWidget(self.label_d)
        self.slider_d = QSlider(Qt.Horizontal, self)
        self.slider_d.setMinimum(0)
        self.slider_d.setMaximum(100)
        self.slider_d.valueChanged.connect(self.update_d)
        layout.addWidget(self.slider_d)

        self.setLayout(layout)
        self.setWindowTitle('PID パラメータ調整')
        self.show()

    def update_poles(self):
        # コントローラとプラントの伝達関数を計算
        W_num, W_den = tfd.calculate_w()
        num = tfd.get_coefficients(W_num)
        den = tfd.get_coefficients(W_den)

        # 極をプロット（Figureを再利用）
        self.ax.clear()  # 以前のプロットをクリア
        self.plot_poles(num, den)  # 極を再描画
        plt.draw()  # 描画を更新

    def update_p(self, value):
        # Pパラメータの値を更新
        tfd.update_constant("VAlt_Kp", value / 10.0)  # 値を変換して更新
        
        self.update_poles()
        # Pの値をラベルに反映
        self.label_p.setText(f"P: {value}")

    def update_i(self, value):
        # Iパラメータの値を更新
        tfd.update_constant("VAlt_Ki", value / 10.0)
        self.update_poles()
        self.label_i.setText(f"I: {value}")

    def update_d(self, value):
        # Dパラメータの値を更新
        tfd.update_constant("VAlt_Kd", value / 10.0)
        self.update_poles()
        self.label_d.setText(f"D: {value}")

    def plot_poles(self, num, den):
        system = ctrl.TransferFunction(num, den)
        poles = system.poles()
        zeros = system.zeros()  # 零点を取得
        for pole in poles:
            print(f"システムの極: Real={pole.real:.4f}, Imag={pole.imag:.4f}")

        # 以前のプロットをクリア
        self.ax.clear()

        # 極と零点の実部と虚部の最大・最小値を計算
        real_parts = np.concatenate([poles.real, zeros.real]) if len(poles) > 0 or len(zeros) > 0 else np.array([0])
        imag_parts = np.concatenate([poles.imag, zeros.imag]) if len(poles) > 0 or len(zeros) > 0 else np.array([0])

        max_real = max(abs(real_parts)) if real_parts.size > 0 else 1  # 実部の絶対値の最大値
        max_imag = max(abs(imag_parts)) if imag_parts.size > 0 else 1  # 虚部の絶対値の最大値

        # スケールに余裕を持たせるために少し余裕を加える（例: 1.1倍）
        margin = 1.1
        x_limit = margin * max_real
        y_limit = margin * max_imag
        #self.saved_x_limit = max(self.saved_x_limit, x_limit)
        #self.saved_y_limit = max(self.saved_y_limit, y_limit)
        self.saved_x_limit = x_limit
        self.saved_y_limit = y_limit

        # 極を赤い大きな 'x' でプロット
        if len(poles) > 0:
            self.ax.scatter(poles.real, poles.imag, color='red', marker='x', s=100, label='Poles')

        # 零点を青い大きな 'o' でプロット
        if len(zeros) > 0:
            self.ax.scatter(zeros.real, zeros.imag, color='blue', marker='o', s=100, facecolors='none', label='Zeros')

        # 縦軸と横軸を0ラインでプロット
        self.ax.axhline(0, color='black', linewidth=0.5)
        self.ax.axvline(0, color='black', linewidth=0.5)

        # 軸の範囲を動的に設定
        self.ax.set_xlim([-self.saved_x_limit, self.saved_x_limit])  # 横軸の範囲を動的に設定
        self.ax.set_ylim([-self.saved_y_limit, self.saved_y_limit])  # 縦軸の範囲を動的に設定

        # グリッド、タイトル、ラベル、凡例を設定
        self.ax.grid(True)
        self.ax.set_title('Pole-Zero Plot')
        self.ax.set_xlabel('Real')
        self.ax.set_ylabel('Imaginary')
        self.ax.legend()


if __name__ == '__main__':
    # PyQtアプリケーションの初期化
    app = QApplication(sys.argv)
    
    # TransParserの初期化
    transfer_function_data = 'workspace/model.json'
    tfd = TransParser(transfer_function_data)
    
    # PIDスライダーのUIを作成
    ex = PIDSliderApp()

    # PyQtアプリケーションを実行
    sys.exit(app.exec_())
