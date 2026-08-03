"""FastAPI主服务 - Tushare版"""
import os, asyncio, json, math
from datetime import datetime
from typing import Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from config import HOST, PORT, ALL_SYMBOLS, UPDATE_INTERVAL, CORS_ORIGINS, TUSHARE_TOKEN
from data_fetcher import DataFetcher
from quant_engine import QuantEngine

app_state = {'data':{}, 'results':{}, 'chart_data':{}, 'last_update':None, 'clients':set()}
fetcher = DataFetcher(token=TUSHARE_TOKEN)

def get_name(t):
    return {'000001.SH':'上证指数','399001.SZ':'深证成指','399006.SZ':'创业板指',
            '000300.SH':'沪深300','000688.SH':'科创50','600519.SH':'贵州茅台',
            '000001.SZ':'平安银行','300750.SZ':'宁德时代','600036.SH':'招商银行',
            '000858.SZ':'五粮液','002594.SZ':'比亚迪','601318.SH':'中国平安',
            '600276.SH':'恒瑞医药'}.get(t, t)

def pd_ok(v): 
    if v is None: return False
    try: return not math.isnan(v)
    except: return True

async def update_loop():
    while True:
        try:
            raw = fetcher.fetch_batch(ALL_SYMBOLS, days=90)
            results, charts = {}, {}
            for ticker, df in raw.items():
                p = QuantEngine.process(df)
                sc = QuantEngine.score(p)
                r = p.iloc[-1]
                key = ticker.replace('.','_')
                results[key] = {
                    'name': get_name(ticker), 'ticker': ticker,
                    'close': round(r['close'],2), 'open': round(r['open'],2),
                    'high': round(r['high'],2), 'low': round(r['low'],2),
                    'volume': int(r['volume']),
                    'change_pct': round(r['change_pct'],2) if pd_ok(r['change_pct']) else 0,
                    'change_pct_5d': round(r['change_pct_5d'],2) if pd_ok(r['change_pct_5d']) else 0,
                    'change_pct_20d': round(r['change_pct_20d'],2) if pd_ok(r['change_pct_20d']) else 0,
                    'rsi': round(r['rsi'],1) if pd_ok(r['rsi']) else 50,
                    'macd_hist': round(r['macd_hist'],3) if pd_ok(r['macd_hist']) else 0,
                    'bb_pos': round(r['bb_pos'],2) if pd_ok(r['bb_pos']) else 0.5,
                    'vol_ratio': round(r['vol_ratio'],2) if pd_ok(r['vol_ratio']) else 1,
                    'volatility': round(r['volatility'],2) if pd_ok(r['volatility']) else 0,
                    'atr': round(r['atr'],2) if pd_ok(r['atr']) else 0,
                    'ma5': round(r['ma5'],2) if pd_ok(r['ma5']) else None,
                    'ma20': round(r['ma20'],2) if pd_ok(r['ma20']) else None,
                    'ma60': round(r['ma60'],2) if pd_ok(r['ma60']) else None,
                    'k': round(r['k'],1) if pd_ok(r['k']) else 50,
                    'd': round(r['d'],1) if pd_ok(r['d']) else 50,
                    'date': str(r['time'])[:10] if 'time' in r else datetime.now().strftime('%Y-%m-%d'),
                    'scores': sc, 'total_score': sc['total'],
                    'signal': sc['signal'], 'risk': sc['risk'],
                }
                d30 = p.tail(30)
                charts[key] = {
                    'dates': [str(x)[:10] for x in d30['time'].values] if 'time' in d30.columns else [],
                    'close': [round(x,2) for x in d30['close'].values],
                    'volume': [int(x) for x in d30['volume'].values],
                    'ma5': [round(x,2) if pd_ok(x) else None for x in d30['ma5'].values],
                    'ma20': [round(x,2) if pd_ok(x) else None for x in d30['ma20'].values],
                    'bb_upper': [round(x,2) if pd_ok(x) else None for x in d30['bb_upper'].values],
                    'bb_lower': [round(x,2) if pd_ok(x) else None for x in d30['bb_lower'].values],
                }
            app_state['results'] = results
            app_state['chart_data'] = charts
            app_state['strategy'] = QuantEngine.strategy(results)
            app_state['last_update'] = datetime.now().isoformat()
            await broadcast({'type':'update','data':results,'chart_data':charts,
                           'strategy':app_state['strategy'],'timestamp':app_state['last_update']})
        except Exception as e:
            print(f"Update error: {e}")
        await asyncio.sleep(UPDATE_INTERVAL)

async def broadcast(msg):
    dead = set()
    for ws in app_state['clients']:
        try: await ws.send_json(msg)
        except: dead.add(ws)
    app_state['clients'] -= dead

@asynccontextmanager
async def lifespan(app):
    task = asyncio.create_task(update_loop())
    yield
    task.cancel()

app = FastAPI(title="A股量化监控API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

static_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def root():
    idx = os.path.join(static_dir, 'index.html')
    if os.path.exists(idx):
        return FileResponse(idx)
    return {"msg":"A股量化监控API运行中","version":"1.0.0","data_source":"Tushare"}

@app.get("/api/data")
def get_data():
    return {'data':app_state.get('results',{}), 'chart_data':app_state.get('chart_data',{}),
            'strategy':app_state.get('strategy',''), 'last_update':app_state.get('last_update')}

@app.get("/api/symbols")
def symbols():
    return {'indices':[{'key':'000001_SH','name':'上证指数'},{'key':'399001_SZ','name':'深证成指'},
                      {'key':'399006_SZ','name':'创业板指'},{'key':'000300_SH','name':'沪深300'},
                      {'key':'000688_SH','name':'科创50'}],
            'stocks':[{'key':'600519_SH','name':'贵州茅台'},{'key':'000001_SZ','name':'平安银行'},
                     {'key':'300750_SZ','name':'宁德时代'},{'key':'600036_SH','name':'招商银行'},
                     {'key':'000858_SZ','name':'五粮液'},{'key':'002594_SZ','name':'比亚迪'},
                     {'key':'601318_SH','name':'中国平安'},{'key':'600276_SH','name':'恒瑞医药'}]}

@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    app_state['clients'].add(websocket)
    if app_state.get('results'):
        await websocket.send_json({'type':'init','data':app_state['results'],
            'chart_data':app_state.get('chart_data',{}),'strategy':app_state.get('strategy',''),
            'timestamp':app_state.get('last_update')})
    try:
        while True:
            msg = await websocket.receive_text()
            if msg == 'ping': await websocket.send_text('pong')
    except (WebSocketDisconnect, Exception):
        app_state['clients'].discard(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
