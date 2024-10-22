import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider, QLineEdit, QHBoxLayout
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
from analyze_model import TransParser
import matplotlib.pyplot as plt
import control as ctrl
import matplotlib
import numpy as np

# matplotlibのバックエンドをPyQtと連携
matplotlib.use('Qt5Agg')

class PIDSliderApp(QWidget):
    def __init__(self, tfd, uptime_msec, scale_range, scale_value, p, i, d, show_step_response, show_bode_phase, show_ny):
        super().__init__()
        self.tfd = tfd
        self.show_step_response = show_step_response
        self.show_bode_phase = show_bode_phase
        self.show_ny = show_ny
        self.p = p
        self.i = i
        self.d = d
        self.saved_x_limit = 1
        self.saved_y_limit = 1
        self.scale_slider = scale_range
        self.scale_param = scale_value
        self.update_timer = QTimer(self)  # タイマーを設定
        self.update_timer.setInterval(uptime_msec) 
        self.update_timer.timeout.connect(self.update_graph)  # タイムアウトで描画更新

        # matplotlibのFigureとAxisを初期化
        self.figure, self.ax = plt.subplots()
        plt.ion()  # インタラクティブモードを有効化
        plt.show()  # 最初に一度だけFigureを表示

        if self.show_step_response:
            self.figure_step, self.ax_step = plt.subplots()
            plt.ion()  # インタラクティブモードを有効化
            plt.show()  # 最初に一度だけFigureを表示

        if self.show_bode_phase:
            self.figure_bode, self.ax_bode = plt.subplots(2, 1)  # ゲインと位相のために2つのサブプロット
            plt.ion()  # インタラクティブモードを有効化
            plt.show()  # 最初に一度だけFigureを表示

        if self.show_ny:
            self.figure_ny, self.ax_ny = plt.subplots()
            plt.ion()
            plt.show()

        self.initUI()

        # TransParserから初期値を取得
        self.kp_init = self.tfd.constants.get(self.p, 0) * self.scale_param
        self.ki_init = self.tfd.constants.get(self.i, 0) * self.scale_param
        self.kd_init = self.tfd.constants.get(self.d, 0) * self.scale_param

        # 初期値をスライダーと入力フィールドに反映
        self.slider_p.setValue(int(self.kp_init))
        self.slider_i.setValue(int(self.ki_init))
        self.slider_d.setValue(int(self.kd_init))

        self.input_p.setText(str(self.kp_init / self.scale_param))
        self.input_i.setText(str(self.ki_init / self.scale_param))
        self.input_d.setText(str(self.kd_init / self.scale_param))

    def initUI(self):
        main_layout = QVBoxLayout()

        # P, I, D のスライダーと入力フィールドの作成
        main_layout.addLayout(self.create_slider_with_input("P", self.p))
        main_layout.addLayout(self.create_slider_with_input("I", self.i))
        main_layout.addLayout(self.create_slider_with_input("D", self.d))

        # スペーサーを追加してスライダーとラベルの表示エリアを分ける
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # システムタイプと定常偏差表示用のラベルのレイアウトを作成
        label_layout = QVBoxLayout()

        self.system_type_label = QLabel("System Type: -", self)
        self.system_gain_label = QLabel("System Gain: -", self)
        self.error_p_label = QLabel("Position Error (ep): -", self)
        self.error_v_label = QLabel("Velocity Error (ev): -", self)
        self.error_a_label = QLabel("Acceleration Error (ea): -", self)

        # ラベルにスタイルを追加
        for label in [self.system_type_label, self.system_gain_label, self.error_p_label, self.error_v_label, self.error_a_label]:
            label.setStyleSheet("font-size: 14px; padding: 5px;")  # フォントサイズとパディングを設定
            label_layout.addWidget(label)

        # ラベルのレイアウトをメインレイアウトに追加
        main_layout.addLayout(label_layout)

        # ウィンドウサイズを固定（横長に設定）
        self.setFixedSize(600, 400)
        #main_layout.setContentsMargins(10, 10, 10, 10)

        self.setLayout(main_layout)
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
        # 値を更新するだけで、すぐに描画はしない
        const_map = {'p': self.p, 'i': self.i, 'd': self.d}
        const_name_full = const_map.get(const_name)

        if const_name_full in self.tfd.constants:
            self.tfd.update_constant(const_name_full, value / self.scale_param)
            input_field = getattr(self, f"input_{const_name}")
            input_field.setText(str(value / self.scale_param))

            # タイマーをリセットして再スタート
            self.update_timer.start()  # タイマーが再起動して200ms後に描画される


    def update_from_input(self, const_name, input_field):
        try:
            new_value = float(input_field.text()) * self.scale_param
            slider = getattr(self, f"slider_{const_name}")
            slider.setValue(int(new_value))
            input_field.setStyleSheet("")  # 正常入力の場合、背景色をリセット
        except ValueError:
            input_field.setStyleSheet("background-color: red")  # エラー時に背景を赤く


    def update_graph(self):
        self.W_num, self.W_den = self.tfd.calculate_w()
        self.L_num, self.L_den = self.tfd.calculate_l()
        self.update_poles()
        if self.show_step_response:
            self.update_step_response()
        if self.show_bode_phase:
            self.update_bode()
        if self.show_ny:
            self.update_nyquist()
        plt.draw()
        self.calculate_steady_state_errors()

    def update_poles(self):
        num = self.tfd.get_coefficients(self.W_num)
        den = self.tfd.get_coefficients(self.W_den)
        self.ax.clear()
        self.plot_poles(num, den)

    # ナイキスト線図をプロットする関数
    def update_nyquist(self):
        num = self.tfd.get_coefficients(self.L_num)
        den = self.tfd.get_coefficients(self.L_den)
        system = ctrl.TransferFunction(num, den)
        
        # axをクリア
        self.ax_ny.clear()

        # ナイキスト線図のプロット
        ctrl.nyquist(system, ax=self.ax_ny)
        
        # 半径1の円を追加
        circle = plt.Circle((0, 0), 1, color='r', fill=False, linestyle='--', label='|L(s)|=1')
        self.ax_ny.add_artist(circle)

        # 凡例をカスタマイズ
        self.ax_ny.legend(['Nyquist', '|L(s)|=1'])

        # グラフの設定
        self.ax_ny.set_title('Nyquist Plot')
        self.ax_ny.grid(True)
        self.ax_ny.set_aspect('equal', 'box')


        
    def update_bode(self):
        num = tfd.get_coefficients(self.L_num)
        den = tfd.get_coefficients(self.L_den)
        system = ctrl.TransferFunction(num, den)

        # Bodeプロットと余裕の計算
        mag, phase, omega = ctrl.bode(system, dB=True, Hz=False, plot=False)
        gm, pm, wg, wp = ctrl.margin(system)

        self.ax_bode[0].clear()
        self.ax_bode[1].clear()

        # ゲイン線図のプロット
        self.ax_bode[0].semilogx(omega, 20 * np.log10(mag), label='Theoretical Gain')
        self.ax_bode[0].set_title('Bode Plot')
        self.ax_bode[0].set_ylabel('Magnitude (dB)')
        self.ax_bode[0].grid(True, which="both", linestyle='--')

        # 位相線図のプロット
        phase = np.rad2deg(phase)
        self.ax_bode[1].semilogx(omega, phase, label='Theoretical Phase')
        self.ax_bode[1].set_ylabel('Phase (degrees)')
        self.ax_bode[1].set_xlabel('Frequency (rad/s)')
        self.ax_bode[1].grid(True, which="both", linestyle='--')


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

    def calculate_steady_state_errors(self):
        num = self.tfd.get_coefficients(self.L_num)
        den = self.tfd.get_coefficients(self.L_den)
        # 共通の因子 s を相殺する
        while num[-1] == 0 and den[-1] == 0:
            num = num[:-1]
            den = den[:-1]
        system = ctrl.TransferFunction(num, den)

        # システムの型を判別
        poles = system.poles()
        num_poles_at_origin = np.sum(np.isclose(poles, 0, atol=1e-6))

        # 定常偏差の計算とUIへの反映
        try:
            dc_gain = ctrl.dcgain(system)
            #print("dc_gain: ", dc_gain)
            #print("num: ", num)
            #print("den: ", den)
        except Exception as e:
            dc_gain = None

        if num_poles_at_origin == 0:
            system_type = "0型"
            ep = 1 / (dc_gain + 1) if dc_gain is not None else "N/A"
            ev = "∞"
            ea = "∞"
        elif num_poles_at_origin == 1:
            system_type = "1型"
            ep = 0
            ev = 1 / dc_gain if dc_gain is not None else "N/A"
            ea = "∞"
        elif num_poles_at_origin == 2:
            system_type = "2型"
            ep = 0
            ev = 0
            ea = 1 / dc_gain if dc_gain is not None else "N/A"
        else:
            system_type = f"{num_poles_at_origin}型"
            ep = "N/A"
            ev = "N/A"
            ea = "N/A"

        # ラベルに計算結果を表示
        dc_gain_str = f"{dc_gain:.2f}" if isinstance(dc_gain, (int, float)) else dc_gain
        ep_str = f"{ep:.2f}" if isinstance(ep, (int, float)) else ep
        ev_str = f"{ev:.2f}" if isinstance(ev, (int, float)) else ev
        ea_str = f"{ea:.2f}" if isinstance(ea, (int, float)) else ea

        self.system_type_label.setText(f"System Type: {system_type}")
        self.system_gain_label.setText(f"System Gain: {dc_gain_str}")
        self.error_p_label.setText(f"Position Error (ep): {ep_str}")
        self.error_v_label.setText(f"Velocity Error (ev): {ev_str}")
        self.error_a_label.setText(f"Acceleration Error (ea): {ea_str}")



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

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="PID パラメータ調整とステップ応答")
    parser.add_argument('file_path', type=str, help='Transfer function JSONファイルのパス')
    parser.add_argument('--uptime', type=int, default=100, help='グラフ描画感覚。単位はmsecです')
    parser.add_argument('--max_input_value', type=float, default=10.0, help='入力可能な最大値')
    parser.add_argument('--input_increment', type=float, default=0.1, help='数値入力のステップサイズ')
    parser.add_argument('--step', action='store_true', help='ステップ応答を表示するかどうか')
    parser.add_argument('--bode', action='store_true', help='ボード線図と位相線図を表示するかどうか')
    parser.add_argument('--ny', action='store_true', help=' ナイキスト線図を表示するかどうか')
    parser.add_argument('--p', type=str, default='VAlt_Kp', help='Pゲインのパラメータ名')
    parser.add_argument('--i', type=str, default='VAlt_Ki', help='Iゲインのパラメータ名')
    parser.add_argument('--d', type=str, default='VAlt_Kd', help='Dゲインのパラメータ名')
    args = parser.parse_args()

    app = QApplication(sys.argv)
    tfd = TransParser(args.file_path)
    scale_range = int(args.max_input_value / args.input_increment)
    scale_value = int(1 / args.input_increment)
    print("P: ", args.p)
    print("I: ", args.i)
    print("D: ", args.d)
    ex = PIDSliderApp(tfd, args.uptime, scale_range, scale_value, args.p, args.i, args.d, args.step, args.bode, args.ny)
    sys.exit(app.exec_())
