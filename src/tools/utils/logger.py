import pandas as pd

class Logger:
    def __init__(self, filename='out.csv'):
        self.data_cache = []
        self.filename = filename

    def log(self, timestamp, value):
        # データをキャッシュに保存
        self.data_cache.append([timestamp, value])

    def save(self):
        # pandasのDataFrameに変換し、CSVファイルに保存
        df = pd.DataFrame(self.data_cache, columns=["timestamp", "value"])
        df.to_csv(self.filename, index=False)
