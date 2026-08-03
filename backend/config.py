"""A股量化监控系统配置 - Tushare版"""
import os

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "10000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "300"))

# Tushare Token (从 https://tushare.pro 注册获取)
TUSHARE_TOKEN = os.getenv("TUSHARE_TOKEN", "")

INDEX_SYMBOLS = [
    "000001.SH",   # 上证指数
    "399001.SZ",   # 深证成指
    "399006.SZ",   # 创业板指
    "000300.SH",   # 沪深300
    "000688.SH",   # 科创50
]

STOCK_SYMBOLS = [
    "600519.SH",   # 贵州茅台
    "000001.SZ",   # 平安银行
    "300750.SZ",   # 宁德时代
    "600036.SH",   # 招商银行
    "000858.SZ",   # 五粮液
    "002594.SZ",   # 比亚迪
    "601318.SH",   # 中国平安
    "600276.SH",   # 恒瑞医药
]

ALL_SYMBOLS = INDEX_SYMBOLS + STOCK_SYMBOLS
HISTORY_DAYS = 90

RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BB_PERIOD = 20
BB_STD = 2
ATR_PERIOD = 14

CORS_ORIGINS = ["*"]
