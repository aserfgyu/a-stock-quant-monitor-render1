"""数据获取 - Tushare免费版"""
import os, time, logging
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self, token: str = ""):
        self.token = token
        self.pro = None
        self._cache = {}
        self._cache_time = {}
        self.ttl = 300
        self._init_tushare()

    def _init_tushare(self):
        """初始化Tushare连接"""
        try:
            import tushare as ts
            if self.token:
                ts.set_token(self.token)
                self.pro = ts.pro_api()
                logger.info("Tushare initialized with token")
            else:
                logger.warning("TUSHARE_TOKEN not set, using mock data")
        except ImportError:
            logger.warning("tushare not installed, using mock data")

    def _mock(self, ticker: str, start: str, end: str) -> pd.DataFrame:
        """模拟数据fallback"""
        np.random.seed(hash(ticker) % 2**32)
        s = datetime.strptime(start, '%Y-%m-%d')
        e = datetime.strptime(end, '%Y-%m-%d')
        dates = []
        c = s
        while c <= e:
            if c.weekday() < 5: dates.append(c)
            c += timedelta(days=1)
        base = {'000001.SH':3900,'399001.SZ':14500,'399006.SZ':3600,'000300.SH':4700,'000688.SH':1800,
                '600519.SH':1300,'000001.SZ':11,'300750.SZ':400,'600036.SH':35,'000858.SZ':160,
                '002594.SZ':280,'601318.SH':48,'600276.SH':45}.get(ticker, 100)
        n = len(dates)
        ret = np.random.normal(0.0005, 0.015, n)
        prices = base * np.exp(np.cumsum(ret))
        data = []
        for i,d in enumerate(dates):
            p = prices[i]
            data.append({
                'time': d.strftime('%Y%m%d'),
                'open': round(p*(1+np.random.normal(0,0.005)),2),
                'high': round(p*(1+abs(np.random.normal(0,0.008))),2),
                'low': round(p*(1-abs(np.random.normal(0,0.008))),2),
                'close': round(p,2),
                'volume': int(np.random.uniform(1e7,5e8)),
                'thscode': ticker, 'thsname_cn': ticker,
            })
        return pd.DataFrame(data)

    def _fetch_tushare(self, ticker: str, start: str, end: str) -> pd.DataFrame:
        """从Tushare获取数据"""
        if not self.pro:
            return self._mock(ticker, start, end)

        try:
            # Tushare格式: 600519.SH -> 600519.SH (保持不变)
            # 指数日线用 index_daily, 股票日线用 daily
            is_index = ticker in ['000001.SH','399001.SZ','399006.SZ','000300.SH','000688.SH']

            if is_index:
                df = self.pro.index_daily(ts_code=ticker, start_date=start.replace('-',''), end_date=end.replace('-',''))
            else:
                df = self.pro.daily(ts_code=ticker, start_date=start.replace('-',''), end_date=end.replace('-',''))

            if df is None or df.empty:
                logger.warning(f"Tushare returned empty for {ticker}, using mock")
                return self._mock(ticker, start, end)

            # 重命名列以兼容现有代码
            df = df.rename(columns={
                'trade_date': 'time',
                'ts_code': 'thscode',
                'vol': 'volume',
            })
            # Tushare volume单位是手，转为股
            if 'volume' in df.columns:
                df['volume'] = df['volume'].astype(float) * 100

            df['thsname_cn'] = ticker
            df = df.sort_values('time').reset_index(drop=True)
            return df

        except Exception as e:
            logger.error(f"Tushare fetch error for {ticker}: {e}")
            return self._mock(ticker, start, end)

    def fetch(self, ticker: str, days: int = 90) -> pd.DataFrame:
        end = datetime.now().strftime('%Y-%m-%d')
        start = (datetime.now()-timedelta(days=days)).strftime('%Y-%m-%d')
        key = f"{ticker}_{start}_{end}"
        if key in self._cache and time.time()-self._cache_time.get(key,0) < self.ttl:
            return self._cache[key]

        df = self._fetch_tushare(ticker, start, end)
        self._cache[key] = df
        self._cache_time[key] = time.time()
        return df

    def fetch_batch(self, tickers: List[str], days: int = 90) -> Dict[str, pd.DataFrame]:
        results = {}
        for t in tickers:
            results[t] = self.fetch(t, days)
            time.sleep(0.2)  # 免费版限流，间隔调用
        return results
