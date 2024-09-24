# hakoniwa-drone-education
This repository is designed to provide a clear, educational framework for controlling drones using the Hakoniwa Drone Simulator.

# 箱庭ドローンシミュレータの環境構築手順

- サポート範囲：
  - Nativeマシン
    - MacOS(AppleSilicon/Intel)
    - Ubuntu 22.0.4
    - Windows/WSL2
  - Dockerコンテナ

## Nativeマシンの場合

本リポジトリーをクローンします。

```bash
git clone https://github.com/toppers/hakoniwa-drone-education.git
```

ワークスペースを作ります。

```bash
cd hakoniwa-drone-education && mkdir workspace
```

インストーラを起動します。

mac:
```
bash ../installer/mac/install.bash
```

linux:
```
bash ../installer/linux/install.bash
```

成功すると、以下のようになります。

```bash
% ls
hakoniwa-px4sim root            setup.bash
```

箱庭ドローンシミュレータのバイナリやコンフィグファイル類は、すべて `root` に入っています。
`setup.bash` は、環境変数定義ファイルです。ツール利用する際に `source` してください。

最後に、利用している `python` コマンドを環境変数として定義してください。

例：
```
export PYTHON_BIN=python3.12
```

## Dockerマシンの場合

```bash
git clone https://github.com/toppers/hakoniwa-drone-education.git
```

docker イメージを取得します。

```bash
cd hakoniwa-drone-education
```

TODO

# 評価実行方法

## Nativeマシンの場合

```bash
cd workspace
```

```bash
source setup.bash
```

```bash
bash ../src/tools/eval-ctrl.bash -1 Z:-3 X:0 S:5
```

成功すると結果が出力されます。

```
NG c(Steady state value)  : 3.000   (Target: -3±-0.030 m)
OK T_r(Rise time)         : 0.576 s (Target: ≤ 10.000 s)
OK T_d(Delay time)        : 0.471 s (Target: ≤ 5.000 s)
OK O_s(Maximum overshoot) : 0.182   (Target: ≤ 1.000 m)
OK T_s(5% settling time)  : 1.428 s (Target: ≤ 20.000 s)
```


## Dockerマシンの場合

TODO

## PIDパラメータの変更方法

PIDパラメータは、以下に配置されています。

`workspace/root/var/lib/hakoniwa/config/param-api-mixer.txt`

高度制御の場合は、以下のパラメータで調整できます。

```
PID_PARM_ALT_Kp 10.0
PID_PARM_ALT_Ki 0.0
PID_PARM_ALT_Kd 4.0
```

# Open this repository in Colab

## Altitude Control

[![Altitude Control](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/toppers/hakoniwa-drone-education/blob/main/colab/alt_control.ipynb)

