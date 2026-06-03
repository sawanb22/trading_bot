"""
tests/test_orders.py
--------------------
Unit tests for bot/orders.py
"""

import unittest
from unittest.mock import MagicMock
from binance.exceptions import BinanceAPIException, BinanceRequestException
from requests.models import Response

from bot.orders import place_order


class TestOrders(unittest.TestCase):
    def setUp(self):
        # Create a mock client
        self.mock_client = MagicMock()

    def test_place_market_order_success(self):
        # Setup mock response
        mock_response = {
            "orderId": 12345,
            "symbol": "BTCUSDT",
            "status": "FILLED",
            "executedQty": "0.01",
            "avgPrice": "67000.0",
        }
        self.mock_client.futures_create_order.return_value = mock_response

        # Execute
        result = place_order(
            client=self.mock_client,
            symbol="BTCUSDT",
            side="BUY",
            order_type="MARKET",
            qty=0.01,
        )

        # Assertions
        self.assertEqual(result, mock_response)
        self.mock_client.futures_create_order.assert_called_once_with(
            symbol="BTCUSDT",
            side="BUY",
            type="MARKET",
            quantity=0.01,
        )

    def test_place_limit_order_success(self):
        # Setup mock response
        mock_response = {
            "orderId": 12346,
            "symbol": "ETHUSDT",
            "status": "NEW",
            "executedQty": "0.0",
            "avgPrice": "0.0",
        }
        self.mock_client.futures_create_order.return_value = mock_response

        # Execute
        result = place_order(
            client=self.mock_client,
            symbol="ETHUSDT",
            side="SELL",
            order_type="LIMIT",
            qty=0.1,
            price=3500.00,
        )

        # Assertions
        self.assertEqual(result, mock_response)
        self.mock_client.futures_create_order.assert_called_once_with(
            symbol="ETHUSDT",
            side="SELL",
            type="LIMIT",
            quantity=0.1,
            price=3500.00,
            timeInForce="GTC",
        )

    def test_place_order_binance_api_exception(self):
        # Create requests Response for the exception
        response = Response()
        response.status_code = 400
        response._content = b'{"code": -2010, "msg": "Account has insufficient balance for requested action."}'

        # Setup mock client to raise exception
        self.mock_client.futures_create_order.side_effect = BinanceAPIException(
            response=response,
            status_code=400,
            text=response.text,
        )

        # Execute and Assert
        with self.assertRaises(BinanceAPIException) as ctx:
            place_order(
                client=self.mock_client,
                symbol="BTCUSDT",
                side="BUY",
                order_type="MARKET",
                qty=0.01,
            )

        self.assertEqual(ctx.exception.code, -2010)
        self.assertEqual(ctx.exception.status_code, 400)

    def test_place_order_binance_request_exception(self):
        # Setup mock client to raise network exception
        self.mock_client.futures_create_order.side_effect = BinanceRequestException(
            "Connection timed out"
        )

        # Execute and Assert
        with self.assertRaises(BinanceRequestException) as ctx:
            place_order(
                client=self.mock_client,
                symbol="BTCUSDT",
                side="BUY",
                order_type="MARKET",
                qty=0.01,
            )

        self.assertIn("Network error communicating with Binance Testnet", str(ctx.exception))

    def test_place_order_unexpected_exception(self):
        # Setup mock client to raise a generic unexpected exception
        self.mock_client.futures_create_order.side_effect = ValueError("Some weird error")

        # Execute and Assert
        with self.assertRaises(RuntimeError) as ctx:
            place_order(
                client=self.mock_client,
                symbol="BTCUSDT",
                side="BUY",
                order_type="MARKET",
                qty=0.01,
            )

        self.assertIn("An unexpected error occurred: ValueError: Some weird error", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
