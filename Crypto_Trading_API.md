
# CryptoCom Trading API Documentation

## Overview

This document outlines the REST API endpoints for the **Crypto Trading Service**, built with **FastAPI** and **CCXT**, using **Crypto.com** (`cryptocom`) as the default exchange.

The service includes:

1. **Market Data**
   - Get real-time price ticker
   - Get historical OHLCV (candlestick) data

2. **Trading**
   - Place limit orders
   - Place market orders
   - Cancel an open order
   - Fetch a single order status
   - Fetch a list of orders
   - Fetch account balance

---

## 1. Market Data Endpoints

### 1.1 Get Price

**Purpose:** Get the latest ticker for a symbol.

**Endpoint:** `/market/price`

**Method:** `GET`

**Query Parameters:**
- `exchange` (string, required): Always `cryptocom`
- `base` (string, required): e.g., `BTC`
- `quote` (string, required): e.g., `USDT`

**Example:**

```
GET /market/price?exchange=cryptocom&base=BTC&quote=USDT
```

**Response:**

```json
{
    "exchange": "cryptocom",
    "symbol": "BTC/USDT",
    "last": 107268.99,
    "bid": 107268.99,
    "ask": 107269.0,
    "high": 107576.86,
    "low": 107108.86,
    "volume": 463.8971
}
```

---

### 1.2 Get OHLCV

**Purpose:** Get historical OHLCV (candlestick) data.

**Endpoint:** `/market/ohlcv`

**Method:** `GET`

**Query Parameters:**
- `exchange` (string, required): Always `cryptocom`
- `base` (string, required)
- `quote` (string, required)
- `timeframe` (string, optional, default: `1m`)
- `limit` (int, optional, default: `10`)

**Example:**

```
GET /market/ohlcv?exchange=cryptocom&base=BTC&quote=USDT&timeframe=5m&limit=5
```

**Response:**

```json
[
  {
    "timestamp": 1687573800000,
    "open": 28950.00,
    "high": 29000.00,
    "low": 28900.00,
    "close": 28980.00,
    "volume": 12.34
  }
]
```

---

## 2. Trading Endpoints

_All trading endpoints require a valid `user_id` to securely look up API keys._

---

### 2.1 Place Limit Order

**Purpose:** Place a limit buy or sell order.

**Endpoint:** `/trade/order/limit`

**Method:** `POST`

**Request Body:**

```json
{
  "exchange": "cryptocom",
  "user_id": "testuser",
  "symbol": "BTC/USDT",
  "side": "buy",
  "amount": 0.01,
  "price": 28000.00
}
```

**Response:**

```json
{
  "id": "123456789",
  "symbol": "BTC/USDT",
  "type": "limit",
  "side": "buy",
  "price": 28000.00,
  "amount": 0.01,
  "status": "open"
}
```

---

### 2.2 Place Market Order

**Purpose:** Place a market buy or sell order.

**Endpoint:** `/trade/order/market`

**Method:** `POST`

**Request Body:**

```json
{
  "exchange": "cryptocom",
  "user_id": "testuser",
  "symbol": "BTC/USDT",
  "side": "sell",
  "amount": 0.02
}
```

**Response:**

```json
{
  "id": "987654321",
  "symbol": "BTC/USDT",
  "type": "market",
  "side": "sell",
  "filled": 0.02,
  "status": "closed"
}
```

---

### 2.3 Cancel Order

**Purpose:** Cancel an open order.

**Endpoint:** `/trade/order/cancel`

**Method:** `POST`

**Request Body:**

```json
{
  "exchange": "cryptocom",
  "user_id": "testuser",
  "symbol": "BTC/USDT",
  "order_id": "123456789"
}
```

**Response:**

```json
{
  "id": "123456789",
  "status": "canceled"
}
```

---

### 2.4 Get Single Order

**Purpose:** Get the status of a single order.

**Endpoint:** `/trade/order`

**Method:** `GET`

**Query Parameters:**
- `exchange` (required): `cryptocom`
- `symbol` (required): e.g., `BTC/USDT`
- `order_id` (required): Order ID
- `user_id` (required)

**Example:**

```
GET /trade/order?exchange=cryptocom&symbol=BTC/USDT&order_id=123456789&user_id=testuser
```

**Response:**

```json
{
  "id": "123456789",
  "symbol": "BTC/USDT",
  "type": "limit",
  "side": "buy",
  "price": 28000.00,
  "amount": 0.01,
  "filled": 0.00,
  "status": "open"
}
```

---

### 2.5 Get Orders List

**Purpose:** Get a list of orders for a trading pair.

**Endpoint:** `/trade/orders`

**Method:** `GET`

**Query Parameters:**
- `exchange` (required): `cryptocom`
- `base` (required): e.g., `BTC`
- `quote` (required): e.g., `USDT`
- `user_id` (required)
- `limit` (optional, default: 20)

**Example:**

```
GET /trade/orders?exchange=cryptocom&base=BTC&quote=USDT&user_id=testuser&limit=5
```

**Response:**

```json
[
  {
    "id": "123456789",
    "symbol": "BTC/USDT",
    "side": "buy",
    "type": "limit",
    "price": 28000.00,
    "amount": 0.01,
    "status": "open"
  }
]
```

---

### 2.6 Get Balance

**Purpose:** Get account balance for Crypto.com.

**Endpoint:** `/trade/balance`

**Method:** `POST`

**Request Body:**

```json
{
  "exchange": "cryptocom",
  "user_id": "testuser"
}
```

**Response:**

```json
{
    "BTC": {
        "free": 0,
        "used": 0,
        "total": 0
    },
    "USDT": {
        "free": 0,
        "used": 0,
        "total": 0
    },
    "ETH": {
        "free": 0,
        "used": 0,
        "total": 0
    }
}
```
