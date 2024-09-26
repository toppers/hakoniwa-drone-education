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

```bash
bash docker/pull-image.bash
```

成功した場合は、こうなります。
```
% docker images
REPOSITORY                               TAG            IMAGE ID       CREATED             SIZE
toppersjp/hakoniwa-drone-education       v1.0.0         4ca1775ffb9a   13 minutes ago      1.47GB
```

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

Dockerコンテナを起動します。
```bash
bash docker/run.bash
```

成功すると、以下のログが出力されます。

```
Configuration updated with custom path.
INFO: updated //etc/hakoniwa/cpp_core_config.json
LD_LIBRARY_PATH added to setup.bash
PATH added to setup.bash
PYTHONPATH added to setup.bash
DRONE_CONFIG_PATH added to setup.bash
HAKO_CONTROLLER_PARAM_FILE added to setup.bash
HAKO_CUSTOM_JSON_PATH added to setup.bash
BIN_PATH added to setup.bash
CONFIG_PATH added to setup.bash
Installation complete. Environment variables have been set.
```

ディレクトリを作業場所に移動します。
```bash
cd workspace
```

シミュレーションを実行します。

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

