"""
bot/client.py
-------------
Binance Futures client factory.

Supports two modes (set via BINANCE_FUTURES_URL in .env):
  1. Binance Demo Trading  (demo.binance.com keys)
     BINANCE_FUTURES_URL=https://demo-fapi.binance.com
  2. Classic Futures Testnet (testnet.binancefuture.com keys)
     BINANCE_FUTURES_URL=https://testnet.binancefuture.com

Responsibilities:
  1. Load BINANCE_API_KEY, BINANCE_API_SECRET, BINANCE_FUTURES_URL from .env
  2. Instantiate binance.client.Client with testnet=True (for HMAC signing)
  3. Override FUTURES_TESTNET_URL to route to the correct demo/testnet host
  4. Raise clear EnvironmentError if credentials are missing

Usage:
    from bot.client import get_client
    client = get_client()
"""

import os
from pathlib import Path

from binance.client import Client
from dotenv import load_dotenv

from bot.logging_config import get_logger

# Resolve the .env path relative to this file (works regardless of cwd)
_DOTENV_PATH = Path(__file__).parent.parent / ".env"

# Default: Binance Demo Trading endpoint
# Override in .env with BINANCE_FUTURES_URL=https://testnet.binancefuture.com
# for the classic Futures Testnet instead.
_DEFAULT_FUTURES_URL = "https://demo-fapi.binance.com"

logger = get_logger()


def get_client() -> Client:
    """
    Load credentials from .env and return a Binance Futures client.
    Routes to Binance Demo Trading (demo-fapi.binance.com) by default,
    or to the classic Futures Testnet if BINANCE_FUTURES_URL is set.

    Returns:
        binance.client.Client configured for Futures paper trading.

    Raises:
        EnvironmentError: If API key or secret is missing from .env.
    """
    # Load .env — override=False means real env vars take precedence if set
    load_dotenv(dotenv_path=_DOTENV_PATH, override=False)

    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    # Detect placeholder values (user hasn't filled .env yet)
    _PLACEHOLDER = "your_testnet_api_key_here"
    _PLACEHOLDER_SECRET = "your_testnet_api_secret_here"

    if not api_key or api_key == _PLACEHOLDER:
        logger.error("BINANCE_API_KEY is not set in .env")
        raise EnvironmentError(
            "BINANCE_API_KEY is missing or still set to the placeholder value.\n"
            "Edit .env and add your API key from demo.binance.com (Demo Trading) "
            "or testnet.binancefuture.com (Futures Testnet)."
        )

    if not api_secret or api_secret == _PLACEHOLDER_SECRET:
        logger.error("BINANCE_API_SECRET is not set in .env")
        raise EnvironmentError(
            "BINANCE_API_SECRET is missing or still set to the placeholder value.\n"
            "Edit .env and add your API secret from demo.binance.com (Demo Trading) "
            "or testnet.binancefuture.com (Futures Testnet)."
        )

    # Determine which Futures endpoint to use
    futures_url = os.getenv("BINANCE_FUTURES_URL", _DEFAULT_FUTURES_URL).rstrip("/")
    logger.info("Futures endpoint: %s", futures_url)

    # testnet=True keeps HMAC signing active (required for demo-fapi too)
    # We then override FUTURES_TESTNET_URL to point to the correct host
    client = Client(api_key=api_key, api_secret=api_secret, testnet=True)

    # Route futures calls to the correct endpoint
    # python-binance uses FUTURES_TESTNET_URL when testnet=True
    client.FUTURES_TESTNET_URL = futures_url + "/fapi"
    logger.info("Futures URL set to: %s/fapi", futures_url)

    logger.info("Binance client initialised successfully.")
    return client
