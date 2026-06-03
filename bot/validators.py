"""
bot/validators.py
─────────────────
Pure validation functions — no side effects, no I/O, fully testable.
Each function raises ValueError with a clear human-readable message on failure.

Business Rules (from Project Execution Plan §3.1):
  • Only USDT-Margined futures are supported (symbol must end with USDT)
  • Supported sides:  BUY | SELL
  • Supported types:  MARKET | LIMIT
  • Quantity must be strictly > 0
  • LIMIT orders require a price > 0
  • MARKET orders must NOT receive a price (prevents user confusion)
"""

from __future__ import annotations

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


def validate_symbol(symbol: str) -> str:
    """
    Normalise and validate a trading symbol.

    Rules:
        - Converted to uppercase automatically
        - Must end with 'USDT' (USDT-Margined futures only)

    Returns:
        Uppercased, validated symbol string.

    Raises:
        ValueError: If symbol does not end with 'USDT'.
    """
    if not isinstance(symbol, str) or not symbol.strip():
        raise ValueError("Symbol must be a non-empty string (e.g. BTCUSDT).")

    symbol = symbol.strip().upper()

    if not symbol.endswith("USDT"):
        raise ValueError(
            f"Invalid symbol '{symbol}'. "
            "Only USDT-Margined (USDT-M) Futures are supported. "
            "Symbol must end with 'USDT' (e.g. BTCUSDT, ETHUSDT)."
        )

    return symbol


def validate_side(side: str) -> str:
    """
    Validate order direction.

    Returns:
        Uppercased side string ('BUY' or 'SELL').

    Raises:
        ValueError: If side is not 'BUY' or 'SELL'.
    """
    if not isinstance(side, str) or not side.strip():
        raise ValueError("Side must be a non-empty string.")

    side = side.strip().upper()

    if side not in VALID_SIDES:
        raise ValueError(
            f"Invalid side '{side}'. "
            f"Accepted values: {', '.join(sorted(VALID_SIDES))}."
        )

    return side


def validate_order_type(order_type: str) -> str:
    """
    Validate order type.

    Returns:
        Uppercased order type string ('MARKET' or 'LIMIT').

    Raises:
        ValueError: If order_type is not 'MARKET' or 'LIMIT'.
    """
    if not isinstance(order_type, str) or not order_type.strip():
        raise ValueError("Order type must be a non-empty string.")

    order_type = order_type.strip().upper()

    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. "
            f"Accepted values: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )

    return order_type


def validate_quantity(qty: float | str) -> float:
    """
    Validate order quantity.

    Rules:
        - Must be numeric
        - Must be strictly greater than 0

    Returns:
        Validated quantity as a float.

    Raises:
        ValueError: If quantity is not a positive number.
    """
    try:
        qty = float(qty)
    except (TypeError, ValueError):
        raise ValueError(
            f"Quantity '{qty}' is not a valid number. "
            "Provide a positive numeric value (e.g. --qty 0.01)."
        )

    if qty <= 0:
        raise ValueError(
            f"Quantity must be greater than 0. Received: {qty}."
        )

    return qty


def validate_price(price: float | str | None, order_type: str) -> float | None:
    """
    Validate price against order type constraints.

    Rules:
        - LIMIT orders:  price is REQUIRED and must be > 0
        - MARKET orders: price must be None / not provided (exchange decides)

    Args:
        price:      The price value from CLI args (may be None).
        order_type: Already-validated order type string ('MARKET' or 'LIMIT').

    Returns:
        Validated price as float (for LIMIT), or None (for MARKET).

    Raises:
        ValueError:
            - LIMIT with no price
            - LIMIT with price <= 0
            - MARKET with any price provided
    """
    order_type = order_type.upper()

    if order_type == "LIMIT":
        if price is None:
            raise ValueError(
                "A valid price is required for LIMIT orders. "
                "Use --price <value> (e.g. --price 3500.00)."
            )
        try:
            price = float(price)
        except (TypeError, ValueError):
            raise ValueError(
                f"Price '{price}' is not a valid number. "
                "Provide a positive numeric value (e.g. --price 3500.00)."
            )
        if price <= 0:
            raise ValueError(
                f"Price must be greater than 0 for LIMIT orders. Received: {price}."
            )
        return price

    elif order_type == "MARKET":
        if price is not None:
            raise ValueError(
                "MARKET orders execute at the current best available price — "
                "do not provide --price. Remove the --price argument and retry."
            )
        return None

    # Fallback (should never reach here if validate_order_type ran first)
    raise ValueError(f"Unknown order type '{order_type}' in price validation.")
