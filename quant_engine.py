"""量化计算引擎"""
import pandas as pd
import numpy as np
from typing import Dict, Any

class QuantEngine:
    @staticmethod
    def calc_ma(s, n): return s.rolling(n).mean()

    @staticmethod
    def calc_rsi(s, n=14):
        d = s.diff()
        g = d.where(d>0,0).rolling(n).mean()
        l = (-d.where(d<0,0)).rolling(n).mean()
        return 100-(100/(1+g/l))

    @staticmethod
    def calc_macd(s, fast=12, slow=26, signal=9):
        ef = s.ewm(span=fast).mean()
        es = s.ewm(span=slow).mean()
        m = ef-es
        sig = m.ewm(span=signal).mean()
        return m, sig, m-sig

    @staticmethod
    def calc_bb(s, n=20, k=2.0):
        m = s.rolling(n).mean()
        std = s.rolling(n).std()
        return m, m+k*std, m-k*std

    @staticmethod
    def calc_atr(df, n=14):
        tr = pd.concat([df['high']-df['low'], (df['high']-df['close'].shift()).abs(), (df['low']-df['close'].shift()).abs()], axis=1).max(axis=1)
        return tr.rolling(n).mean()

    @classmethod
    def process(cls, df):
        df = df.copy().sort_values('time').reset_index(drop=True)
        for n in [5,10,20,60]: df[f'ma{n}'] = cls.calc_ma(df['close'], n)
        df['rsi'] = cls.calc_rsi(df['close'])
        df['macd'], df['macd_signal'], df['macd_hist'] = cls.calc_macd(df['close'])
        df['bb_mid'], df['bb_upper'], df['bb_lower'] = cls.calc_bb(df['close'])
        df['atr'] = cls.calc_atr(df)
        df['vol_ma5'] = df['volume'].rolling(5).mean()
        df['vol_ma20'] = df['volume'].rolling(20).mean()
        df['vol_ratio'] = df['volume']/df['vol_ma5']
        df['vol_trend'] = df['vol_ma5']/df['vol_ma20']
        df['change_pct'] = df['close'].pct_change()*100
        df['change_pct_5d'] = (df['close']/df['close'].shift(5)-1)*100
        df['change_pct_20d'] = (df['close']/df['close'].shift(20)-1)*100
        df['volatility'] = df['change_pct'].rolling(20).std()
        df['bb_pos'] = (df['close']-df['bb_lower'])/(df['bb_upper']-df['bb_lower'])
        low14 = df['low'].rolling(14).min()
        high14 = df['high'].rolling(14).max()
        df['k'] = 100*(df['close']-low14)/(high14-low14)
        df['d'] = df['k'].rolling(3).mean()
        return df

    @classmethod
    def score(cls, df):
        r = df.iloc[-1]
        s = {}
        s['trend'] = (5 if r['close']>r['ma5'] else 0) + (5 if r['ma5']>r['ma10'] else 0) + (5 if r['ma10']>r['ma20'] else 0) + (5 if r['close']>r['ma20'] else 0) + (5 if r['close']>r['ma60'] else 0)
        mom = 0
        rsi = r['rsi'] if pd.notna(r['rsi']) else 50
        if 40<=rsi<=60: mom+=8
        elif rsi>60: mom+=15
        elif rsi>40: mom+=10
        else: mom+=5
        if r['macd_hist']>0: mom+=5
        if r['macd']>r['macd_signal']: mom+=5
        k = r['k'] if pd.notna(r['k']) else 50
        if k>50: mom+=5
        s['momentum'] = min(mom,25)

        vol=0; vr=r['vol_ratio'] if pd.notna(r['vol_ratio']) else 1; vt=r['vol_trend'] if pd.notna(r['vol_trend']) else 1
        if vr>1.5: vol+=10
        elif vr>1.0: vol+=7
        elif vr>0.8: vol+=5
        else: vol+=3
        if vt>1.2: vol+=10
        elif vt>1.0: vol+=7
        elif vt>0.9: vol+=5
        else: vol+=3
        s['volume'] = min(vol,20)

        pos=0; bp=r['bb_pos'] if pd.notna(r['bb_pos']) else 0.5
        if bp<0.2: pos+=12
        elif bp<0.4: pos+=10
        elif bp<0.6: pos+=7
        elif bp<0.8: pos+=5
        else: pos+=3
        vlt=r['volatility'] if pd.notna(r['volatility']) else 2
        if vlt<1: pos+=3
        elif vlt<2: pos+=2
        else: pos+=1
        s['position'] = min(pos,15)

        perf=0; c5=r['change_pct_5d'] if pd.notna(r['change_pct_5d']) else 0; c20=r['change_pct_20d'] if pd.notna(r['change_pct_20d']) else 0
        if c5>3: perf+=8
        elif c5>0: perf+=5
        elif c5>-3: perf+=3
        else: perf+=1
        if c20>5: perf+=7
        elif c20>0: perf+=5
        elif c20>-5: perf+=3
        else: perf+=1
        s['performance'] = min(perf,15)

        s['total'] = s['trend']+s['momentum']+s['volume']+s['position']+s['performance']
        t = s['total']
        if t>=75: s['signal']='强烈买入'
        elif t>=60: s['signal']='买入'
        elif t>=45: s['signal']='观望偏多'
        elif t>=35: s['signal']='观望'
        elif t>=25: s['signal']='观望偏空'
        elif t>=15: s['signal']='卖出'
        else: s['signal']='强烈卖出'

        vlt=r['volatility'] if pd.notna(r['volatility']) else 2
        if vlt>3: s['risk']='高风险'
        elif vlt>2: s['risk']='中高风险'
        elif vlt>1.5: s['risk']='中等风险'
        elif vlt>1: s['risk']='中低风险'
        else: s['risk']='低风险'
        return s

    @classmethod
    def strategy(cls, results):
        buy = [k for k,v in results.items() if v['total_score']>=60]
        sell = [k for k,v in results.items() if v['total_score']<30]
        parts = []
        if buy: parts.append(f'<b>推荐关注:</b> {", ".join([results[k]["name"] for k in buy])} (评分≥60)')
        if sell: parts.append(f'<b>谨慎回避:</b> {", ".join([results[k]["name"] for k in sell])} (评分偏低)')
        idx = [results[k]['total_score'] for k in results if k in ['000001_SH','399001_SZ','399006_SZ','000300_SH']]
        avg = sum(idx)/len(idx) if idx else 50
        if avg>=55: parts.extend(['<b>大盘研判:</b> 市场整体偏强，可适当加仓。','<b>操作建议:</b> 维持6-7成仓位，关注科技成长与消费龙头。'])
        elif avg>=40: parts.extend(['<b>大盘研判:</b> 市场震荡分化，结构性机会为主。','<b>操作建议:</b> 控制仓位5成左右，精选个股，回避高波动板块。'])
        else: parts.extend(['<b>大盘研判:</b> 市场整体偏弱，防御为主。','<b>操作建议:</b> 降低仓位至3-4成，关注银行、白酒等防御板块。'])
        return '<br>'.join(parts)
