from fastapi import FastAPI
from market_data_api import router as market_router
from trading_api import router as trading_router

app = FastAPI(
    title="Crypto Trading API",
    description="统一管理 Market Data + Trading 功能",
    version="1.0"
)

# 你可以根据需要给前缀
app.include_router(market_router, prefix="/market")
app.include_router(trading_router, prefix="/trade")

# 根路径可选
@app.get("/")
def read_root():
    return {"msg": "Welcome to Unified FastAPI Service!"}
