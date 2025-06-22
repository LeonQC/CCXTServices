from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import ccxt
import time

app = FastAPI()

# ---------- 工厂函数 ----------

def create_exchange(exchange_name: str, api_key: Optional[str] = None, api_secret: Optional[str] = None):
    try:
        exchange_class = getattr(ccxt, exchange_name.lower())
        config = {
            'enableRateLimit': True
        }
        if api_key and api_secret:
            config['apiKey'] = api_key
            config['secret'] = api_secret
        exchange = exchange_class(config)
        exchange.load_markets()
        return exchange
    except AttributeError:
        raise ValueError(f"不支持的交易所名称: {exchange_name}")
    except Exception as e:
        raise ValueError(f"{exchange_name} 初始化失败: {e}")

# ---------- 请求模型 ----------

# class PublicMarketRequest(BaseModel):
#     exchange: str
#     base: str
#     quote: str
#     timeframe: Optional[str] = "1m"
#     limit: Optional[int] = 10

class OrderRequest(BaseModel):
    exchange: str
    api_key: str
    api_secret: str
    symbol: str
    side: str
    amount: float
    price: Optional[float] = None

class CancelRequest(BaseModel):
    exchange: str
    api_key: str
    api_secret: str
    symbol: str
    order_id: str

class BalanceRequest(BaseModel):
    exchange: str
    api_key: str
    api_secret: str

# ---------- 市场行情接口（不需要 API Key） ----------

@app.get("/price")
def api_get_price(exchange: str, base: str, quote: str):
    try:
        ex = create_exchange(exchange)
        symbol = f"{base.upper()}/{quote.upper()}"
        ticker = ex.fetch_ticker(symbol)
        return {
            "exchange": exchange,
            "symbol": symbol,
            "last": ticker["last"],
            "bid": ticker["bid"],
            "ask": ticker["ask"],
            "high": ticker["high"],
            "low": ticker["low"],
            "volume": ticker["baseVolume"],
        }
    except Exception as e:
        print("获取价格失败:", e)
        raise HTTPException(status_code=400, detail=f"{exchange} 获取价格失败: {e}")

@app.get("/ohlcv")
def api_get_ohlcv(exchange: str, base: str, quote: str, timeframe: str = "1m", limit: int = 10):
    try:
        ex = create_exchange(exchange)
        symbol = f"{base.upper()}/{quote.upper()}"
        data = ex.fetch_ohlcv(symbol, timeframe, limit)
        return [
            {"timestamp": o[0], "open": o[1], "high": o[2], "low": o[3], "close": o[4], "volume": o[5]}
            for o in data
        ]
    except Exception as e:
        print("获取K线失败:", e)
        raise HTTPException(status_code=400, detail=f"{exchange} 获取K线失败: {e}")

# ---------- 交易类接口（需要 API Key） ----------

@app.post("/order/limit")
def api_limit_order(req: OrderRequest):
    try:
        ex = create_exchange(req.exchange, req.api_key, req.api_secret)
        if req.side.lower() == "buy":
            return ex.create_limit_buy_order(req.symbol, req.amount, req.price)
        else:
            return ex.create_limit_sell_order(req.symbol, req.amount, req.price)
    except Exception as e:
        print("创建限价单失败:", e)
        raise HTTPException(status_code=400, detail="限价单失败")

@app.post("/order/market")
def api_market_order(req: OrderRequest):
    try:
        ex = create_exchange(req.exchange, req.api_key, req.api_secret)
        if req.side.lower() == "buy":
            return ex.create_market_buy_order(req.symbol, req.amount)
        else:
            return ex.create_market_sell_order(req.symbol, req.amount)
    except Exception as e:
        print("创建市价单失败:", e)
        raise HTTPException(status_code=400, detail="市价单失败")

@app.post("/order/cancel")
def api_cancel_order(req: CancelRequest):
    try:
        ex = create_exchange(req.exchange, req.api_key, req.api_secret)
        return ex.cancel_order(req.order_id, req.symbol)
    except Exception as e:
        print("撤销订单失败:", e)
        raise HTTPException(status_code=400, detail="撤销订单失败")

@app.get("/order")
def api_fetch_order(exchange: str, symbol: str, order_id: str, api_key: str, api_secret: str):
    try:
        ex = create_exchange(exchange, api_key, api_secret)
        return ex.fetch_order(order_id, symbol)
    except Exception as e:
        print("查询订单失败:", e)
        raise HTTPException(status_code=400, detail="订单查询失败")

@app.get("/orders")
def api_fetch_all_orders(exchange: str, base: str, quote: str, api_key: str, api_secret: str, limit: int = 20):
    try:
        ex = create_exchange(exchange, api_key, api_secret)
        symbol = f"{base.upper()}/{quote.upper()}"
        return ex.fetch_orders(symbol, limit=limit)
    except Exception as e:
        print("获取订单列表失败:", e)
        raise HTTPException(status_code=400, detail="获取订单列表失败")

@app.post("/balance")
def api_get_balance(req: BalanceRequest):
    try:
        ex = create_exchange(req.exchange, req.api_key, req.api_secret)
        return ex.fetch_balance()
    except Exception as e:
        print("获取余额失败:", e)
        raise HTTPException(status_code=400, detail="获取余额失败")
