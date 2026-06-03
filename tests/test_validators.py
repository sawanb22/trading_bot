"""
tests/test_validators.py
-------------------------
Unit tests for bot/validators.py
"""

import unittest
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
)


class TestValidators(unittest.TestCase):
    def test_validate_symbol_success(self):
        self.assertEqual(validate_symbol("BTCUSDT"), "BTCUSDT")
        self.assertEqual(validate_symbol("ethusdt"), "ETHUSDT")
        self.assertEqual(validate_symbol("  solusdt  "), "SOLUSDT")

    def test_validate_symbol_failure(self):
        with self.assertRaises(ValueError) as ctx:
            validate_symbol("")
        self.assertIn("Symbol must be a non-empty string", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            validate_symbol("BTCBTC")
        self.assertIn("Only USDT-Margined (USDT-M) Futures are supported", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            validate_symbol(123)
        self.assertIn("Symbol must be a non-empty string", str(ctx.exception))

    def test_validate_side_success(self):
        self.assertEqual(validate_side("BUY"), "BUY")
        self.assertEqual(validate_side("sell"), "SELL")
        self.assertEqual(validate_side("  buy  "), "BUY")

    def test_validate_side_failure(self):
        with self.assertRaises(ValueError) as ctx:
            validate_side("HOLD")
        self.assertIn("Invalid side", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            validate_side("")
        self.assertIn("Side must be a non-empty string", str(ctx.exception))

    def test_validate_order_type_success(self):
        self.assertEqual(validate_order_type("MARKET"), "MARKET")
        self.assertEqual(validate_order_type("limit"), "LIMIT")
        self.assertEqual(validate_order_type("  Market  "), "MARKET")

    def test_validate_order_type_failure(self):
        with self.assertRaises(ValueError) as ctx:
            validate_order_type("STOP_LOSS")
        self.assertIn("Invalid order type", str(ctx.exception))

    def test_validate_quantity_success(self):
        self.assertEqual(validate_quantity(0.01), 0.01)
        self.assertEqual(validate_quantity("0.1"), 0.1)

    def test_validate_quantity_failure(self):
        with self.assertRaises(ValueError) as ctx:
            validate_quantity(0)
        self.assertIn("Quantity must be greater than 0", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            validate_quantity(-1.5)
        self.assertIn("Quantity must be greater than 0", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            validate_quantity("not_a_number")
        self.assertIn("is not a valid number", str(ctx.exception))

    def test_validate_price_market_success(self):
        self.assertIsNone(validate_price(None, "MARKET"))

    def test_validate_price_market_failure(self):
        with self.assertRaises(ValueError) as ctx:
            validate_price(100.0, "MARKET")
        self.assertIn("MARKET orders execute at the current best available price", str(ctx.exception))

    def test_validate_price_limit_success(self):
        self.assertEqual(validate_price(60000.0, "LIMIT"), 60000.0)
        self.assertEqual(validate_price("3500.50", "LIMIT"), 3500.50)

    def test_validate_price_limit_failure(self):
        with self.assertRaises(ValueError) as ctx:
            validate_price(None, "LIMIT")
        self.assertIn("A valid price is required for LIMIT orders", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            validate_price(0, "LIMIT")
        self.assertIn("Price must be greater than 0 for LIMIT orders", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            validate_price(-50.0, "LIMIT")
        self.assertIn("Price must be greater than 0 for LIMIT orders", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            validate_price("abc", "LIMIT")
        self.assertIn("is not a valid number", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
