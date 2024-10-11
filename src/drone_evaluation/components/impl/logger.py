import pandas as pd

class Logger:
    def __init__(self, filename='in.csv', cache_len=1024):
        self.data_cache = []
        self.filename = filename
        self.cache_len = cache_len  # キャッシュサイズを設定
        self.columns = ["timestamp", "value"]  # デフォルトのカラム名を設定

    def set_columns(self, columns):
        """カラム名を設定するメソッド"""
        self.columns = columns

    def log(self, *values):
        """ログに複数の値を記録する"""
        if len(values) != len(self.columns):
            raise ValueError(f"Expected {len(self.columns)} values, but got {len(values)}")
        self.data_cache.append(values)
        
        # キャッシュサイズを超えたら保存
        if len(self.data_cache) >= self.cache_len:
            self.save()
            self.data_cache = []  # キャッシュをクリア

    def save(self):
        """キャッシュをCSVに保存する"""
        df = pd.DataFrame(self.data_cache, columns=self.columns)
        df.to_csv(self.filename, mode='a', header=not pd.io.common.file_exists(self.filename), index=False)

    def flush(self):
        """強制的に現在のキャッシュを保存する"""
        if self.data_cache:
            self.save()
            self.data_cache = []  # キャッシュをクリア
