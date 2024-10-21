import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider, QLineEdit, QHBoxLayout
from PyQt5.QtCore import Qt
from analyze_model import TransParser
import matplotlib.pyplot as plt
import control as ctrl
import matplotlib
import numpy as np

# matplotlibのバックエンドをPyQtと連携
matplotlib.use('Qt5Agg')

class PIDSliderApp(QWidget):
    def __init__(self, tfd, show_step_response):
        super().__init__()
        self.tfd = tfd
        self.show_step_response = show_step_response
        self.saved_x_limit = 1
        self.saved_y_limit = 1
        self.scale_slider = 1000
        self.scale_param = 10

        self.initUI()

        # matplotlibのFigureとAxisを初期化
        self.figure, self.ax = plt.subplots()
        plt.ion()  # インタラクティブモードを有効化
        plt.show()  # 最初に一度だけFigureを表示

        if self.show_step_response:
            self.figure_step, self.ax_step = plt.subplots()
            plt.ion()  # インタラクティブモードを有効化
            plt.show()  # 最初に一度だけFigureを表示

        # TransParserから初期値を取得
        self.kp_init = self.tfd.constants.get("VAlt_Kp", 0) * self.scale_param
        self.ki_init = self.tfd.constants.get("VAlt_Ki", 0) * self.scale_param
        self.kd_init = self.tfd.constants.get("VAlt_Kd", 0) * self.scale_param

        # 初期値をスライダーと入力フィールドに反映
        self.slider_p.setValue(int(self.kp_init))
        self.slider_i.setValue(int(self.ki_init))
        self.slider_d.setValue(int(self.kd_init))

        self.input_p.setText(str(self.kp_init / self.scale_param))
        self.input_i.setText(str(self.ki_init / self.scale_param))
        self.input_d.setText(str(self.kd_init / self.scale_param))

    def initUI(self):
        layout = QVBoxLayout()

        # P, I, D のスライダーと入力フィールドの作成
        layout.addLayout(self.create_slider_with_input("P", "VAlt_Kp"))
        layout.addLayout(self.create_slider_with_input("I", "VAlt_Ki"))
        layout.addLayout(self.create_slider_with_input("D", "VAlt_Kd"))

        self.setLayout(layout)
        self.setWindowTitle('PID パラメータ調整')
        self.show()

    def create_slider_with_input(self, label_text, const_name):
        layout = QHBoxLayout()

        # ラベル作成
        label = QLabel(f"{label_text}: ", self)
        layout.addWidget(label)

        # スライダー作成
        slider = QSlider(Qt.Horizontal, self)
        slider.setMinimum(0)
        slider.setMaximum(self.scale_slider)
        slider.valueChanged.connect(lambda value, c=label_text.lower(): self.update_value(value, c))  # 変更
        layout.addWidget(slider)

        # 入力フィールド作成
        input_field = QLineEdit(self)
        input_field.setFixedWidth(50)
        input_field.editingFinished.connect(lambda c=label_text.lower(), field=input_field: self.update_from_input(c, field))  # 変更
        layout.addWidget(input_field)

        # スライダーと入力フィールドを属性にセット
        setattr(self, f"slider_{label_text.lower()}", slider)
        setattr(self, f"input_{label_text.lower()}", input_field)

        return layout

    def update_value(self, value, const_name):
        # 'p', 'i', 'd' を対応する定数名に変換
        if const_name == 'p':
            const_name_full = 'VAlt_Kp'
        elif const_name == 'i':
            const_name_full = 'VAlt_Ki'
        elif const_name == 'd':
            const_name_full = 'VAlt_Kd'

        # 定数の更新
        if const_name_full in tfd.constants:
            tfd.update_constant(const_name_full, value / self.scale_param)
            input_field = getattr(self, f"input_{const_name}")
            input_field.setText(str(value / self.scale_param))
            self.update_graph()
        else:
            print(f"{const_name_full} is not found in constants")


    def update_from_input(self, const_name, input_field):
        try:
            # 入力フィールドの値をスライダーと定数に反映
            new_value = float(input_field.text()) * self.scale_param
            slider = getattr(self, f"slider_{const_name.split('_')[-1].lower()}")
            slider.setValue(int(new_value))
        except ValueError:
            pass

    def update_graph(self):
        self.W_num, self.W_den = self.tfd.calculate_w()
        self.update_poles()
        if self.show_step_response:
            self.update_step_response()

    def update_poles(self):
        num = self.tfd.get_coefficients(self.W_num)
        den = self.tfd.get_coefficients(self.W_den)
        self.ax.clear()
        self.plot_poles(num, den)
        plt.draw()

    def update_step_response(self):
        num = self.tfd.get_coefficients(self.W_num)
        den = self.tfd.get_coefficients(self.W_den)
        system = ctrl.TransferFunction(num, den)
        t, y = ctrl.step_response(system)
        self.ax_step.clear()
        self.ax_step.plot(t, y, label='Step Response')
        self.ax_step.set_title('Step Response')
        self.ax_step.set_xlabel('Time (s)')
        self.ax_step.set_ylabel('Amplitude')
        self.ax_step.grid(True)
        self.ax_step.legend()
        plt.draw()

    def plot_poles(self, num, den):
        system = ctrl.TransferFunction(num, den)
        poles = system.poles()
        zeros = system.zeros()

        self.ax.clear()
        self.ax.scatter(poles.real, poles.imag, color='red', marker='x', s=100, label='Poles')
        self.ax.scatter(zeros.real, zeros.imag, color='blue', marker='o', s=100, facecolors='none', label='Zeros')
        self.ax.axhline(0, color='black', linewidth=0.5)
        self.ax.axvline(0, color='black', linewidth=0.5)
        self.ax.grid(True)
        self.ax.set_title('Pole-Zero Plot')
        self.ax.set_xlabel('Real')
        self.ax.set_ylabel('Imaginary')
        self.ax.legend()
        plt.draw()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="PID パラメータ調整とステップ応答")
    parser.add_argument('file_path', type=str, help='Transfer function JSONファイルのパス')
    parser.add_argument('--step', action='store_true', help='ステップ応答を表示するかどうか')
    args = parser.parse_args()

    app = QApplication(sys.argv)
    tfd = TransParser(args.file_path)
    ex = PIDSliderApp(tfd, args.step)
    sys.exit(app.exec_())
