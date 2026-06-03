"""
tests/test_cli.py
-----------------
Unit tests for cli.py
"""

import unittest
from unittest.mock import patch, MagicMock
import sys

from cli import build_parser, main


class TestCLI(unittest.TestCase):
    def test_parser_valid_market_args(self):
        parser = build_parser()
        args = parser.parse_args(["--symbol", "BTCUSDT", "--side", "BUY", "--type", "MARKET", "--qty", "0.01"])
        self.assertEqual(args.symbol, "BTCUSDT")
        self.assertEqual(args.side, "BUY")
        self.assertEqual(args.order_type, "MARKET")
        self.assertEqual(args.qty, 0.01)
        self.assertIsNone(args.price)
        self.assertFalse(args.mock)

    def test_parser_valid_limit_args(self):
        parser = build_parser()
        args = parser.parse_args(["--symbol", "ETHUSDT", "--side", "SELL", "--type", "LIMIT", "--qty", "0.1", "--price", "3500.00", "--mock"])
        self.assertEqual(args.symbol, "ETHUSDT")
        self.assertEqual(args.side, "SELL")
        self.assertEqual(args.order_type, "LIMIT")
        self.assertEqual(args.qty, 0.1)
        self.assertEqual(args.price, 3500.00)
        self.assertTrue(args.mock)

    @patch("cli.place_order")
    @patch("cli.get_client")
    @patch("sys.argv", ["cli.py", "--symbol", "BTCUSDT", "--side", "BUY", "--type", "MARKET", "--qty", "0.01", "--mock"])
    def test_main_success_market(self, mock_get_client, mock_place_order):
        # Mock client and response
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_response = {
            "orderId": 7439002,
            "symbol": "BTCUSDT",
            "status": "FILLED",
            "executedQty": "0.01",
            "avgPrice": "67500.00",
        }
        mock_place_order.return_value = mock_response

        # Call main (should not raise SystemExit)
        main()

        mock_get_client.assert_called_once()
        mock_place_order.assert_called_once_with(
            client=mock_client,
            symbol="BTCUSDT",
            side="BUY",
            order_type="MARKET",
            qty=0.01,
            price=None,
        )

    @patch("sys.argv", ["cli.py", "--symbol", "BTCUSDT", "--side", "BUY", "--type", "LIMIT", "--qty", "0.01", "--mock"])
    def test_main_validation_error_limit_no_price(self):
        # Validation should fail because price is missing for LIMIT order
        with self.assertRaises(SystemExit) as ctx:
            main()

        # Should exit with code 1
        self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
