import argparse
import matplotlib.pyplot as plt
import control as ctrl
import numpy as np
import math

import json
import re
from sympy import symbols, Poly

class TransParser:
    def __init__(self, json_file):
        self.json_file = json_file
        self.data = self.load_transfer_function()
        self.constants = self.evaluate_constants(self.data['constants'])
        if 'pd_args' in self.data:
            self.pd_args = self.data['pd_args']
        else:
            self.pd_args = None
        self.s = symbols('s')  # シンボル s をここで定義し、クラス全体で共有する

    def update_constant(self, const_name, new_value):
        if const_name in self.constants:
            self.constants[const_name] = new_value
        else:
            print(f"{const_name} is not found in constants")

    # JSONファイルの読み込み
    def load_transfer_function(self):
        with open(self.json_file, 'r') as file:
            data = json.load(file)
        return data

    # 伝達関数の各項を定数で置き換えて評価する
    def evaluate_terms(self, terms):
        evaluated_terms = []
        for term in terms:
            for const, value in self.constants.items():
                # 正規表現で変数名の前後が他の文字と一致しない場合のみ置き換え
                pattern = r'\b' + re.escape(const) + r'\b'
                term = re.sub(pattern, str(value), term)
            evaluated_terms.append(eval(term))  # 式を計算
        return evaluated_terms

    # 定数を評価するメソッド
    def evaluate_constants(self, constants):
        evaluated_constants = {}
        pending = constants.copy()  # 評価待ちの定数

        # 評価ループ: すべての定数が解決されるまで繰り返す
        while pending:
            unresolved = {}  # 未解決の定数を保存
            for const, value in pending.items():
                #print("key: ", const)
                if isinstance(value, str):
                    # 数式として評価を試みる
                    try:
                        #print("evaluated_consts: ", evaluated_constants)
                        evaluated_constants[const] = eval(value, {"__builtins__": None}, {**evaluated_constants, "math": math})
                        print("evaluated_value: ", evaluated_constants[const])
                    except NameError:
                        # 評価できない場合は未解決のまま保留
                        unresolved[const] = value
                        print("unsolved value: ", value)
                    except Exception as e:
                        print(f"Failed to evaluate {const}: {e}")
                else:
                    # 数値はそのまま評価
                    evaluated_constants[const] = value
                    #print("value: ", value)

            # もし未解決の定数が減っていなければループを終了
            if len(unresolved) == len(pending):
                raise ValueError("Circular dependency or undefined variables detected.")
            
            pending = unresolved  # 未解決の定数を再度評価
        return evaluated_constants
        
    
    # C(s) の取得（複数のコントローラに対応）
    def get_controllers(self):
        controllers_data = self.data['controllers']
        overall_num = Poly([1], self.s)  # 初期値 1
        overall_den = Poly([1], self.s)  # 初期値 1
        for controller in controllers_data:
            numerator = self.evaluate_terms(controller['num'])
            denominator = self.evaluate_terms(controller['den'])
            controller_num_poly = Poly(numerator, self.s)
            controller_den_poly = Poly(denominator, self.s)
            # 複数コントローラがある場合は掛け合わせる
            overall_num *= controller_num_poly
            overall_den *= controller_den_poly
        return overall_num, overall_den

    # P(s) (プラント) の取得
    def get_plants(self):
        plants_data = self.data['plants']
        overall_num = Poly([1], self.s)  # 初期値 1
        overall_den = Poly([1], self.s)  # 初期値 1
        for plant in plants_data:
            num = self.evaluate_terms(plant['num'])
            den = self.evaluate_terms(plant['den'])
            plant_num_poly = Poly(num, self.s)
            plant_den_poly = Poly(den, self.s)
            # 複数プラントがある場合は掛け合わせる
            overall_num *= plant_num_poly
            overall_den *= plant_den_poly
        return overall_num, overall_den

    # L(s) = C(s) * P(s) の計算
    def calculate_l(self):
        # コントローラ C(s) とプラント P(s) を取得
        C_num, C_den = self.get_controllers()
        P_num, P_den = self.get_plants()

        # L(s) の計算 (分子同士と分母同士の掛け算)
        L_num = C_num * P_num
        L_den = C_den * P_den
        return L_num, L_den

    # W(s) = L(s) / (1 + L(s)) の計算
    # W(s) = L_num / (L_den + L_num) の計算
    def calculate_w(self):
        # L(s) の分子と分母を取得
        L_num, L_den = self.calculate_l()

        # W(s) = L_num / (L_den + L_num) を計算
        W_num = L_num  # W(s) の分子は L(s) の分子
        W_den = L_den + L_num  # W(s) の分母は L(s) の分母 + L(s) の分子

        return W_num,  W_den
    
    # Ed(s) = P(s) / (1 + L(s)) の計算
    def calculate_ed(self):
        # プラント P(s) を取得
        P_num, P_den = self.get_plants()
        
        # L(s) の分子と分母を取得
        L_num, L_den = self.calculate_l()

        # Ed(s) = P_num / (P_den * (1 + L(s)))
        Ed_num = P_num  # Ed(s) の分子はプラント P(s) の分子
        Ed_den = P_den * (L_den + L_num)  # 分母は P(s) の分母と 1 + L(s) の掛け算
        
        return Ed_num, Ed_den

    # 多項式の係数をリスト形式で取得するメソッド
    def get_coefficients(self, poly):
        # sympyの `all_coeffs` メソッドを使用して係数をリストとして取得し、floatに変換
        return [float(coeff) for coeff in poly.all_coeffs()]



# ボード線図を表示する関数
def plot_bode_and_margins(num, den):
    system = ctrl.TransferFunction(num, den)
    
    # Bodeプロットと位相余裕・ゲイン余裕の計算
    mag, phase, omega = ctrl.bode(system, dB=True, Hz=False, omega_limits=(1e-2, 1e4), plot=False)
    gm, pm, wg, wp = ctrl.margin(system)
    
    # ゲイン余裕と位相余裕を表示
    print(f"ゲイン余裕 (Gain Margin): {20 * np.log10(gm) if gm else '∞'} dB")
    print(f"位相余裕 (Phase Margin): {pm} degrees")
    print(f"ゲイン余裕発生周波数: {wg} rad/s")
    print(f"位相余裕発生周波数: {wp} rad/s")
    
    # Bodeプロットを描画
    plt.figure()
    
    # ゲイン線図
    plt.subplot(2, 1, 1)
    plt.semilogx(omega, 20 * np.log10(mag))
    plt.title('Bode Plot')
    plt.ylabel('Magnitude (dB)')
    plt.grid(True, which="both", linestyle='--')
    
    # ゲイン交差周波数に縦線を追加
    if wg:
        plt.axvline(wg, color='r', linestyle='--', label=f'Gain Cross @ {wg:.2f} rad/s')
    plt.axhline(0, color='k', linestyle='--')

    # 位相線図
    phase = np.rad2deg(phase) 
    plt.subplot(2, 1, 2)
    plt.semilogx(omega, phase)
    plt.ylabel('Phase (degrees)')
    plt.xlabel('Frequency (rad/s)')
    plt.grid(True, which="both", linestyle='--')

    # 位相交差周波数に縦線を追加
    if wp:
        plt.axvline(wp, color='r', linestyle='--', label=f'Phase Cross @ {wp:.2f} rad/s')
    plt.axhline(-180, color='k', linestyle='--')

    plt.savefig('bode_plot.png')
    plt.show()
    plt.close()

# 極をプロットする関数
def plot_poles(num, den):
    system = ctrl.TransferFunction(num, den)
    poles = system.poles()
    for pole in poles:
        print(f"システムの極: Real={pole.real:.4f}, Imag={pole.imag:.4f}")

    # 極をプロット
    plt.figure()
    plt.scatter(poles.real, poles.imag, color='red', marker='x')
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.grid(True)
    plt.title('Pole-Zero Plot')
    plt.xlabel('Real')
    plt.ylabel('Imaginary')
    plt.savefig('poles_plot.png')
    plt.show()
    plt.close()


# ステップ応答をプロットし、各種パラメータを計算・表示する関数
def plot_step_response(num, den):
    system = ctrl.TransferFunction(num, den)
    
    # ステップ応答の計算
    t, y = ctrl.step_response(system)
    
    # オーバーシュートの計算
    overshoot = (np.max(y) - 1) * 100  # ステップ応答の最大値から1を引いて百分率に変換
    overshoot_time = t[np.argmax(y)]  # オーバーシュートが発生した時間
    
    # 定常偏差の計算
    steady_state_value = y[-1]  # 最終値
    steady_state_error = 1 - steady_state_value  # ステップ入力の目標値は1
    
    # 立ち上がり時間（Rise Time）の計算 (10% から 90%)
    rise_time_index = np.where((y >= 0.1) & (y <= 0.9))[0]
    rise_time = t[rise_time_index[-1]] - t[rise_time_index[0]] if len(rise_time_index) > 0 else None
    
    # 遅延時間（Delay Time）の計算 (初めて50%を超えた時間)
    delay_time_index = np.where(y >= 0.5)[0]
    delay_time = t[delay_time_index[0]] if len(delay_time_index) > 0 else None

    # 整定時間（Settling Time）の計算 (±2%の範囲に収まる)
    settling_threshold = 0.05  # 5%の範囲
    settling_index = np.where(np.abs(y - steady_state_value) <= settling_threshold)[0]
    settling_time = t[settling_index[-1]] if len(settling_index) > 0 else None

    # パラメータを表示
    print(f"Overshoot: {overshoot:.2f}% at {overshoot_time:.2f} seconds")
    print(f"Steady-State Value: {steady_state_value:.2f}")
    print(f"Steady-State Error: {steady_state_error:.2f}")
    print(f"Rise Time (10%-90%): {rise_time:.2f} seconds" if rise_time else "Rise Time: Not Defined")
    print(f"Delay Time (50%): {delay_time:.2f} seconds" if delay_time else "Delay Time: Not Defined")
    print(f"Settling Time (within ±5%): {settling_time:.2f} seconds" if settling_time else "Settling Time: Not Defined")
    
    # ステップ応答のプロット
    plt.figure()
    plt.plot(t, y)
    plt.title('Step Response')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    
    # オーバーシュートの箇所にマーカーを追加
    plt.axvline(x=overshoot_time, color='r', linestyle='--', label=f'Overshoot @ {overshoot_time:.2f}s')
    plt.axhline(y=steady_state_value, color='g', linestyle='--', label=f'Steady-State Value = {steady_state_value:.2f}')
    
    plt.legend()
    plt.savefig('step_plot.png')
    plt.show()
    plt.close()



# インパルス応答をプロットする関数
def plot_impulse_response(num, den):
    system = ctrl.TransferFunction(num, den)
    
    # インパルス応答の計算とプロット
    t, y = ctrl.impulse_response(system)
    plt.figure()
    plt.plot(t, y)
    plt.title('Impulse Response')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.savefig('impulse_plot.png')
    plt.show()
    plt.close()


# ナイキスト線図をプロットする関数
def plot_nyquist(num, den):
    # システムの伝達関数を定義
    system = ctrl.TransferFunction(num, den)
    
    # ナイキスト線図のプロット
    ctrl.nyquist(system)
    
    # 半径1の円を追加
    circle = plt.Circle((0, 0), 1, color='r', fill=False, linestyle='--', label='|L(s)|=1')
    plt.gca().add_artist(circle)
    
    # グラフの設定
    plt.title('Nyquist Plot')
    plt.grid(True)
    plt.gca().set_aspect('equal', 'box')  # 均等なスケールにする
    plt.legend()
    
    # 図を保存して表示
    plt.savefig('nyquist_plot_with_circle.png')
    plt.show()
    plt.close()

class PDEvaluator:
    def __init__(self, PM, Ki, Wc):
        self.PM = PM
        self.Ki = Ki
        self.Wc = Wc
    
    def calc(self, plant_num, plant_den):
        # s = 1j * Wc の値を代入する
        s_value = 1j * self.Wc
        
        # np.polyval を使用して、多項式の評価を行う
        # 分子と分母にそれぞれ s_value を代入して評価
        p_s_num = np.polyval(plant_num, s_value)
        p_s_den = np.polyval(plant_den, s_value)
        
        # 分子/分母で伝達関数を計算
        p_s = p_s_num / p_s_den
        
        # 実部と虚部を表示
        print("real: ", p_s.real)
        print("im: ", p_s.imag)

        # 実部と虚部を保存
        self.u = p_s.real
        self.v = p_s.imag

    def calc_phi_m(self):
        """PMからφmを計算"""
        pm = math.radians(self.PM)
        return pm - math.pi
    
    def getKp(self):
        """Kpを計算"""
        phi_m = self.calc_phi_m()
        print("phi_m", phi_m)
        numerator = self.u * math.cos(phi_m) + self.v * math.sin(phi_m)
        denominator = self.u**2 + self.v**2
        kp = numerator / denominator
        return kp

    def getKd(self):
        """Kdを計算"""
        phi_m = self.calc_phi_m()
        numerator = self.u * math.sin(phi_m) - self.v * math.cos(phi_m)
        denominator = self.Wc * (self.u**2 + self.v**2)
        kd = ((self.Ki / self.Wc**2) + (numerator / denominator))
        return kd

def calc_pd(tfd):
    if tfd.pd_args is None:
        print("ERROR: not found pd_args")
        return False
    e = PDEvaluator(tfd.pd_args['PM'], tfd.pd_args['Ki'], tfd.pd_args['Wc'])
    P_num, P_den = tfd.get_plants()
    e.calc(tfd.get_coefficients(P_num), tfd.get_coefficients(P_den))
    Kp = e.getKp()
    Kd = e.getKd()
    print(f"\"Kp\": {Kp},")
    print(f"\"Ki\": {tfd.pd_args['Ki']},")
    print(f"\"Kd\": {Kd},")
    return True

# メイン処理
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bode, Step, Impulse, and Pole-Zero Plotter from transfer function JSON file")
    parser.add_argument('file_path', type=str, help="Path to the transfer function JSON file")
    parser.add_argument('func_type', type=str, choices=['ps', 'ws', 'ls', 'eds'], default='ls', help="Type of transfer function type")
    parser.add_argument('--mode', type=str, choices=['bode', 'step', 'impulse', 'poles', 'pd', 'ny' ], default='bode', help="Type of response to plot (bode, step, impulse, poles, ny)")
    args = parser.parse_args()

    transfer_function_data = args.file_path
    tfd = TransParser(transfer_function_data)

    # s をシンボルとして定義
    s = symbols('s')
    num = []
    den = []
    if args.func_type == 'ws':
        # W(s) の計算
        W_num, W_den = tfd.calculate_w()
        num = tfd.get_coefficients(W_num)
        den = tfd.get_coefficients(W_den)
    elif args.func_type == 'ls':
        # L(s) の計算
        L_num, L_den = tfd.calculate_l()
        num = tfd.get_coefficients(L_num)
        den = tfd.get_coefficients(L_den)
    elif args.func_type == 'ps':
        # L(s) の計算
        P_num, P_den = tfd.get_plants()
        num = tfd.get_coefficients(P_num)
        den = tfd.get_coefficients(P_den)
    else:
        Ed_num, Ed_den = tfd.calculate_ed()
        num = tfd.get_coefficients(Ed_num)
        den = tfd.get_coefficients(Ed_den)

    print('num: ', num)
    print('den: ', den)

    # ボード線図、ステップ応答、インパルス応答、極のプロットのいずれかをプロット
    if args.mode == 'bode':
        plot_bode_and_margins(num, den)
    elif args.mode == 'step':
        plot_step_response(num, den)
    elif args.mode == 'impulse':
        plot_impulse_response(num, den)
    elif args.mode == 'poles':
        plot_poles(num, den)
    elif args.mode == 'pd':
        calc_pd(tfd)
    elif args.mode == 'ny':
        plot_nyquist(num, den)

