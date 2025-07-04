from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import ccxt

router = APIRouter()

# ---- 模拟从数据库获取 API Key ----
def get_api_credentials(user_id: str):
    # TODO: 这里后续替换成数据库读取
    if user_id == "testuser":
        return {
            "apiKey": "---",
            "secret": "---"
        }
    else:
        raise HTTPException(status_code=404, detail="用户不存在或未配置密钥")

def create_exchange(exchange_name: str, creds: dict):
    try:
        exchange_class = getattr(ccxt, exchange_name.lower())
        config = {
            'apiKey': creds['apiKey'],
            'secret': creds['secret'],
            'enableRateLimit': True
        }
        exchange = exchange_class(config)
        exchange.load_markets()
        return exchange
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{exchange_name} 初始化失败: {e}")

# ---- 请求模型 ----
class OrderRequest(BaseModel):
    exchange: str
    user_id: str
    symbol: str
    side: str
    amount: float
    price: Optional[float] = None

class CancelRequest(BaseModel):
    exchange: str
    user_id: str
    symbol: str
    order_id: str

class BalanceRequest(BaseModel):
    exchange: str
    user_id: str

# ---- 下单接口 ----
@router.post("/order/limit")
def api_limit_order(req: OrderRequest):
    creds = get_api_credentials(req.user_id)
    ex = create_exchange(req.exchange, creds)
    try:
        if req.side.lower() == "buy":
            return ex.create_limit_buy_order(req.symbol, req.amount, req.price)
        else:
            return ex.create_limit_sell_order(req.symbol, req.amount, req.price)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"限价单失败: {e}")

@router.post("/order/market")
def api_market_order(req: OrderRequest):
    creds = get_api_credentials(req.user_id)
    ex = create_exchange(req.exchange, creds)
    try:
        if req.side.lower() == "buy":
            return ex.create_market_buy_order(req.symbol, req.amount)
        else:
            return ex.create_market_sell_order(req.symbol, req.amount)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"市价单失败: {e}")

@router.post("/order/cancel")
def api_cancel_order(req: CancelRequest):
    creds = get_api_credentials(req.user_id)
    ex = create_exchange(req.exchange, creds)
    try:
        return ex.cancel_order(req.order_id, req.symbol)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"撤销订单失败: {e}")

@router.get("/order")
def api_fetch_order(exchange: str, symbol: str, order_id: str, user_id: str):
    creds = get_api_credentials(user_id)
    ex = create_exchange(exchange, creds)
    try:
        return ex.fetch_order(order_id, symbol)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"订单查询失败: {e}")

@router.get("/orders")
def api_fetch_all_orders(exchange: str, base: str, quote: str, user_id: str, limit: int = 20):
    creds = get_api_credentials(user_id)
    ex = create_exchange(exchange, creds)
    symbol = f"{base.upper()}/{quote.upper()}"
    try:
        return ex.fetch_orders(symbol, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取订单列表失败: {e}")
    
SUPPORTED_SYMBOLS = ["BTC", "USDT", "ETH"]

@router.post("/balance")
def api_get_balance(req: BalanceRequest):
    creds = get_api_credentials(req.user_id)
    ex = create_exchange(req.exchange, creds)
    try:
        raw = ex.fetch_balance()
        result = {}

        for symbol in SUPPORTED_SYMBOLS:
            result[symbol] = {
                "free": raw['free'].get(symbol, 0),
                "used": raw['used'].get(symbol, 0),
                "total": raw['total'].get(symbol, 0)
            }

        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取余额失败: {e}")
