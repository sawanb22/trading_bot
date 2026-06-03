"""
bot/mock_client.py
------------------
Mock Binance Futures client for local execution and offline testing.
"""

import time
import random
from bot.logging_config import get_logger

logger = get_logger()


class MockClient:
    """Simulates binance.client.Client for USDT-M Futures."""

    def __init__(self, api_key: str = "MOCK_KEY", api_secret: str = "MOCK_SECRET"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.FUTURES_TESTNET_URL = "https://mock-fapi.binance.com/fapi"

    def futures_create_order(self, **kwargs) -> dict:
        """
        Simulate creating a futures order.
        Returns a dictionary structure matching the Binance Futures API response.
        """
        symbol = kwargs.get("symbol", "BTCUSDT")
        side = kwargs.get("side", "BUY")
        order_type = kwargs.get("type", "MARKET")
        quantity = kwargs.get("quantity", 0.01)
        price = kwargs.get("price")

        # Mock values based on the order type
        order_id = random.randint(1000000, 9999999)
        timestamp = int(time.time() * 1000)

        logger.info(
            "[MOCK] Processing order simulation | Symbol: %s, Side: %s, Type: %s, Qty: %s",
            symbol,
            side,
            order_type,
            quantity,
        )

        if order_type == "MARKET":
            # Simulate a filled market order
            # Estimate a reasonable average price based on the symbol
            base_prices = {"BTCUSDT": 67500.0, "ETHUSDT": 3500.0}
            base_price = base_prices.get(symbol, 100.0)
            avg_price = round(base_price + random.uniform(-10, 10), 2)
            cum_quote = round(avg_price * float(quantity), 2)

            return {
                "orderId": order_id,
                "symbol": symbol,
                "status": "FILLED",
                "clientOrderId": f"mock_{order_id}",
                "price": "0.00",
                "avgPrice": str(avg_price),
                "origQty": str(quantity),
                "executedQty": str(quantity),
                "cumQty": str(quantity),
                "cumQuote": str(cum_quote),
                "timeInForce": "GTC",
                "type": "MARKET",
                "reduceOnly": False,
                "closePosition": False,
                "side": side,
                "positionSide": "BOTH",
                "stopPrice": "0.00",
                "workingType": "CONTRACT_PRICE",
                "priceProtect": False,
                "origType": "MARKET",
                "updateTime": timestamp,
            }

        elif order_type == "LIMIT":
            # Simulate a new/pending limit order
            return {
                "orderId": order_id,
                "symbol": symbol,
                "status": "NEW",
                "clientOrderId": f"mock_{order_id}",
                "price": f"{price:.2f}" if price is not None else "0.00",
                "avgPrice": "0.00",
                "origQty": str(quantity),
                "executedQty": "0.0",
                "cumQty": "0.0",
                "cumQuote": "0.00",
                "timeInForce": kwargs.get("timeInForce", "GTC"),
                "type": "LIMIT",
                "reduceOnly": False,
                "closePosition": False,
                "side": side,
                "positionSide": "BOTH",
                "stopPrice": "0.00",
                "workingType": "CONTRACT_PRICE",
                "priceProtect": False,
                "origType": "LIMIT",
                "updateTime": timestamp,
            }

        else:
            raise ValueError(f"Mock client does not support order type: {order_type}")
