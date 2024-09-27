# hakoniwa-drone-education

本リポジトリでは、箱庭ドローンの数式を線形モデル化して、解析的にドローン制御のPIDパラメータを調査する方法をまとめています。

具体的には、こんなことができます。

- 解析的なPIDパラメータ調査手法としては、ボード線図や位相線図の作成からステップ応答解析などを Google Colab で簡単に行えます。
- 解析的に求めたパラメータを箱庭ドローンシミュレータで動作確認できます。この際、遅延時間やオーバーシュート量などを定量的に評価できます。

箱庭ドローンの物理モデルは[こちら](https://github.com/toppers/hakoniwa-px4sim/blob/main/drone_physics/README-ja.md#%E6%95%B0%E5%BC%8F)。

![image](https://github.com/user-attachments/assets/270c4b61-39f2-4451-b442-c6fc5c1100eb)


# Google Colab での解析


- 高度制御：[![Altitude Control](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/toppers/hakoniwa-drone-education/blob/main/colab/alt_control.ipynb)


# 箱庭ドローンシミュレータでの動作確認

共通操作：
```bash
cd workspace
```
```bash
export PYTHON_BIN=python3
```

## 高度制御

上空３メートルまでテイクオフする場合の動作確認するには、以下のコマンドで`Z:-3` としてください。他のパラメータは変更しないでください。
```bash
bash ../src/tools/eval-ctrl.bash -1 Z:-3 X:0 S:5
```
出力ログ：
```
NG c(Steady state value)  : 3.000   (Target: -3±-0.030 m)
OK T_r(Rise time)         : 0.576 s (Target: ≤ 10.000 s)
OK T_d(Delay time)        : 0.471 s (Target: ≤ 5.000 s)
OK O_s(Maximum overshoot) : 0.182   (Target: ≤ 1.000 m)
OK T_s(5% settling time)  : 1.428 s (Target: ≤ 20.000 s)
```

グラフ化方法：
```bash
python3 ../src/tools/hako_TimelineAnalyzer.py drone_log0/drone_dynamics.csv --columns Z --diff
```

成功すると、`plot.png` ファイルがカレントディレクトリ直下に出力されます。

![image](https://github.com/user-attachments/assets/f57e0d25-5fd5-438b-a9c3-989a848cb269)


実際の飛行状況を見たい場合は、リプレイ機能で確認できます(Nativeマシンの場合のみ利用できます)。

```bash
bash ../src/tools/replay.bash
```

以下のログが出力されたら、Webブラウザから`http://localhost:8000`にアクセスすればOKです。

```
INFO: start hakoniwa asset(web server)
INFO: start http server
INFO: start websocket server
INFO: Success for external initialization.
======== Running on http://localhost:8080 ========
(Press CTRL+C to quit)
WebSocket server started on ws://localhost:8765
Starting HTTP server on port 8000...
Press ENTER to start the services
```

リプレイ完了後、もう一度見たい場合は、`restart` とキー入力してENTERキーを押下してください。
終了する場合は、`exit` とキー入力して、ENTERキーを押下後、CTRL±Cで終了させてください。

***リプレイ：***


https://github.com/user-attachments/assets/228db9bb-6f13-43a8-9a44-6c13eea45682


***リスタート：***


https://github.com/user-attachments/assets/d81d4e5e-5f5e-4770-bd81-4e77e11e8488



# 箱庭ドローンシミュレータの環境構築手順

- サポート範囲：
  - Nativeマシン
    - MacOS(AppleSilicon/Intel)
    - Ubuntu 22.0.4
    - Windows/WSL2
  - Dockerコンテナ
  - Codespace

## Nativeマシンの場合

本リポジトリーをクローンします。

```bash
git clone https://github.com/toppers/hakoniwa-drone-education.git
```

ワークスペースを作ります。

```bash
cd hakoniwa-drone-education && mkdir workspace
```

ワークスペースに移動します。

```bash
cd workspace
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
export PYTHON_BIN=python3
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

