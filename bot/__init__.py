# bot/__init__.py
# Marks the bot/ directory as a Python package.
# Exposes the primary public interface for external imports.

from bot.client import get_client
from bot.orders import place_order
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
)

__all__ = [
    "get_client",
    "place_order",
    "validate_symbol",
    "validate_side",
    "validate_order_type",
    "validate_quantity",
    "validate_price",
]
