"""
bot/orders.py
─────────────
Order construction and execution against the Binance Futures Testnet.

Responsibilities:
  1. Build the exact API payload for MARKET and LIMIT orders
  2. Log the request payload (DEBUG) before sending
  3. Execute via client.futures_create_order()
  4. Log the full raw JSON response (INFO)
  5. Handle exchange-side errors (BinanceAPIException) and network errors
     (BinanceRequestException) with structured logging and clean re-raises

Payload Rules (Binance Futures API):
  MARKET: {symbol, side, type, quantity}
  LIMIT:  {symbol, side, type, quantity, price, timeInForce: "GTC"}
"""

from __future__ import annotations

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.logging_config import get_logger
from bot.mock_client import MockClient

logger = get_logger()

# Default timeInForce for LIMIT orders (Good Till Cancelled)
_DEFAULT_TIME_IN_FORCE = "GTC"


def place_order(
    client: Client | MockClient,
    symbol: str,
    side: str,
    order_type: str,
    qty: float,
    price: float | None = None,
) -> dict:
    """
    Construct and submit a futures order to the Binance Testnet.

    Args:
        client:     Authenticated Binance Testnet client (from bot.client).
        symbol:     Trading pair, e.g. 'BTCUSDT'.
        side:       'BUY' or 'SELL'.
        order_type: 'MARKET' or 'LIMIT'.
        qty:        Quantity to trade (strictly > 0).
        price:      Limit price (required for LIMIT, must be None for MARKET).

    Returns:
        Raw response dict from the Binance API, e.g.:
        {
            "orderId": 123456,
            "symbol": "BTCUSDT",
            "status": "FILLED",
            "executedQty": "0.01",
            "avgPrice": "67500.00",
            ...
        }

    Raises:
        BinanceAPIException:     Exchange rejected the order (e.g. insufficient margin).
        BinanceRequestException: Network/connection failure.
        RuntimeError:            Any unexpected error (stack trace logged).
    """
    # ── Build Payload ────────────────────────────────────────────────────────
    payload: dict = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": qty,
    }

    if order_type == "LIMIT":
        payload["price"] = price
        payload["timeInForce"] = _DEFAULT_TIME_IN_FORCE

    logger.debug(
        "Preparing to submit order | Payload: %s",
        payload,
    )

    # ── Submit Order ─────────────────────────────────────────────────────────
    try:
        logger.info(
            "Submitting %s %s order | Symbol: %s | Qty: %s%s",
            side,
            order_type,
            symbol,
            qty,
            f" | Price: {price}" if price is not None else "",
        )

        response = client.futures_create_order(**payload)

        logger.info(
            "Order accepted by exchange | Raw response: %s",
            response,
        )

        return response

    except BinanceAPIException as exc:
        # Exchange-side rejection: insufficient margin, invalid symbol, etc.
        logger.error(
            "BinanceAPIException | HTTP Status: %s | Error Code: %s | Message: %s",
            exc.status_code,
            exc.code,
            exc.message,
        )
        raise BinanceAPIException(
            exc.response,
            exc.status_code,
            exc.response.text if hasattr(exc, "response") else str(exc),
        ) from exc

    except BinanceRequestException as exc:
        # Network-level failure: timeout, DNS failure, etc.
        logger.error(
            "BinanceRequestException (network error) | %s",
            str(exc),
        )
        raise BinanceRequestException(
            f"Network error communicating with Binance Testnet: {exc}"
        ) from exc

    except Exception as exc:
        # Unexpected catch-all — log full stack trace
        logger.exception(
            "Unexpected error during order placement | %s: %s",
            type(exc).__name__,
            exc,
        )
        raise RuntimeError(
            f"An unexpected error occurred: {type(exc).__name__}: {exc}"
        ) from exc
