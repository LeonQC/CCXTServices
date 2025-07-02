from fastapi import APIRouter, HTTPException
import ccxt

router = APIRouter()

def create_exchange(exchange_name: str):
    try:
        exchange_class = getattr(ccxt, exchange_name.lower())
        exchange = exchange_class({'enableRateLimit': True})
        exchange.load_markets()
        return exchange
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{exchange_name} 初始化失败: {e}")

@router.get("/price")
def api_get_price(exchange: str, base: str, quote: str):
    try:
        ex = create_exchange(exchange)
        symbol = f"{base.upper()}/{quote.upper()}"
        ticker = ex.fetch_ticker(symbol)
        return {
            "exchange": exchange,
            "symbol": symbol,
            "timestamp": ticker["timestamp"],  # 交易所提供的时间戳（毫秒）
            "datetime": ticker["datetime"],    # ISO格式时间字符串
            "last": ticker["last"],
            "bid": ticker["bid"],
            "ask": ticker["ask"],
            "high": ticker["high"],
            "low": ticker["low"],
            "volume": ticker["baseVolume"],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{exchange} 获取价格失败: {e}")

@router.get("/ohlcv")
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
        raise HTTPException(status_code=400, detail=f"{exchange} 获取K线失败: {e}")
