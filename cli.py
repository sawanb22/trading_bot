"""
cli.py
------
Entry point for the Binance Futures Testnet Trading Bot.

Architecture (strict separation of concerns):
  cli.py  →  handles ONLY argument parsing and terminal presentation
  bot/    →  handles ONLY business logic, API calls, and validation

Flow:
  1. Parse CLI arguments via argparse
  2. Validate all inputs via bot.validators (fails fast, prints rich error)
  3. Print pre-execution summary table (rich)
  4. Get Binance Testnet client (bot.client)
  5. Place order (bot.orders)
  6. Print result table (rich) — green for success, red for error

Usage:
  python cli.py --symbol BTCUSDT --side BUY  --type MARKET --qty 0.01
  python cli.py --symbol ETHUSDT --side SELL --type LIMIT  --qty 0.1 --price 3500.00
"""

import argparse
import io
import sys

from binance.exceptions import BinanceAPIException, BinanceRequestException
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from bot.client import get_client
from bot.logging_config import get_logger
from bot.orders import place_order
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
)

# ── Console & Logger ─────────────────────────────────────────────────────────
# Force UTF-8 output on Windows (PowerShell defaults to cp1252)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

console = Console(force_terminal=True, highlight=False)
logger = get_logger()


# ── Argument Parser ──────────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description=(
            "Binance Futures Testnet Trading Bot\n"
            "Places MARKET and LIMIT orders on USDT-M Futures (Testnet only).\n"
            "No real funds are ever used."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python cli.py --symbol BTCUSDT --side BUY  --type MARKET --qty 0.01\n"
            "  python cli.py --symbol ETHUSDT --side SELL --type LIMIT  --qty 0.1 --price 3500.00\n"
        ),
    )

    parser.add_argument(
        "--symbol",
        required=True,
        metavar="SYMBOL",
        help="Trading pair symbol. Must be a USDT-M future (e.g. BTCUSDT, ETHUSDT).",
    )
    parser.add_argument(
        "--side",
        required=True,
        metavar="SIDE",
        help="Order direction. Accepted values: BUY, SELL.",
    )
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        metavar="TYPE",
        help="Order type. Accepted values: MARKET, LIMIT.",
    )
    parser.add_argument(
        "--qty",
        required=True,
        type=float,
        metavar="QTY",
        help="Order quantity (must be > 0). Example: 0.01 for 0.01 BTC.",
    )
    parser.add_argument(
        "--price",
        required=False,
        type=float,
        default=None,
        metavar="PRICE",
        help=(
            "Limit price (required for LIMIT orders, must NOT be set for MARKET). "
            "Example: --price 3500.00"
        ),
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run the bot in mock/simulated mode (does not hit the real API).",
    )

    return parser


# ── UI Helpers ───────────────────────────────────────────────────────────────
def print_validation_error(message: str) -> None:
    """Print a styled error panel and exit with code 1."""
    panel = Panel(
        Text(f"[ERROR]  {message}", style="bold red"),
        title="[bold red]Validation Error[/bold red]",
        border_style="red",
        padding=(1, 2),
    )
    console.print(panel)


def print_pre_execution_summary(
    symbol: str,
    side: str,
    order_type: str,
    qty: float,
    price: float | None,
) -> None:
    """Print a clean pre-execution summary table before the order is sent."""
    table = Table(
        title="[bold cyan]Order Summary (Pre-Execution)[/bold cyan]",
        box=box.ROUNDED,
        border_style="cyan",
        title_style="bold cyan",
        show_header=True,
        header_style="bold white on #1a1a2e",
        min_width=45,
    )

    table.add_column("Parameter", style="bold white", min_width=14)
    table.add_column("Value", style="bright_cyan", min_width=25)

    side_color = "green" if side == "BUY" else "red"

    table.add_row("Symbol", f"[bold]{symbol}[/bold]")
    table.add_row("Side", f"[bold {side_color}]{side}[/bold {side_color}]")
    table.add_row("Type", order_type)
    table.add_row("Quantity", str(qty))
    table.add_row(
        "Price",
        f"{price:.8f}".rstrip("0").rstrip(".") if price is not None else "[dim]Market Price[/dim]",
    )
    table.add_row("TimeInForce", "GTC" if order_type == "LIMIT" else "[dim]N/A[/dim]")

    console.print()
    console.print(table)
    console.print()


def print_order_result(response: dict, side: str) -> None:
    """Parse and display the Binance API response as a styled result table."""
    status = response.get("status", "UNKNOWN")
    order_id = response.get("orderId", "N/A")
    executed_qty = response.get("executedQty", "0")
    avg_price = response.get("avgPrice", "0")
    symbol = response.get("symbol", "N/A")

    # Determine colour semantics
    if status in ("FILLED", "PARTIALLY_FILLED", "NEW"):
        status_color = "green"
        panel_color = "green"
        icon = "[OK]"
        result_label = "Order Accepted"
    else:
        status_color = "red"
        panel_color = "red"
        icon = "[FAIL]"
        result_label = "Order Rejected / Failed"

    table = Table(
        title=f"{icon}  Execution Result - {result_label}",
        box=box.ROUNDED,
        border_style=panel_color,
        title_style=f"bold {panel_color}",
        show_header=True,
        header_style="bold white on #1a1a2e",
        min_width=45,
    )

    table.add_column("Field", style="bold white", min_width=16)
    table.add_column("Value", style="bright_white", min_width=28)

    side_color = "green" if side == "BUY" else "red"

    table.add_row("Order ID", f"[bold]{order_id}[/bold]")
    table.add_row("Symbol", symbol)
    table.add_row("Side", f"[bold {side_color}]{side}[/bold {side_color}]")
    table.add_row("Status", f"[bold {status_color}]{status}[/bold {status_color}]")
    table.add_row("Executed Qty", executed_qty)
    table.add_row(
        "Avg Price",
        avg_price if float(avg_price) > 0 else "[dim]Pending (Order on Book)[/dim]",
    )

    console.print()
    console.print(table)
    console.print()


def print_api_error(exc: BinanceAPIException) -> None:
    """Display a structured API error without an ugly Python traceback."""
    error_text = Text()
    error_text.append(f"Exchange Error Code: {exc.code}\n", style="bold red")
    error_text.append(f"HTTP Status:         {exc.status_code}\n", style="red")
    error_text.append(f"Message:             {exc.message}", style="red")

    panel = Panel(
        error_text,
        title="[bold red]Binance API Error[/bold red]",
        border_style="red",
        padding=(1, 2),
    )
    console.print(panel)


# ── Main ─────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.mock:
        import os
        os.environ["USE_MOCK"] = "True"

    logger.info(
        "CLI invoked | symbol=%s side=%s type=%s qty=%s price=%s mock=%s",
        args.symbol,
        args.side,
        args.order_type,
        args.qty,
        args.price,
        args.mock,
    )

    # ── Step 1: Validate All Inputs ──────────────────────────────────────────
    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        qty = validate_quantity(args.qty)
        price = validate_price(args.price, order_type)

    except ValueError as exc:
        logger.error("Input validation failed: %s", exc)
        print_validation_error(str(exc))
        sys.exit(1)

    # ── Step 2: Pre-Execution Summary ────────────────────────────────────────
    print_pre_execution_summary(symbol, side, order_type, qty, price)

    # ── Step 3: Get Binance Testnet Client ───────────────────────────────────
    try:
        client = get_client()
    except EnvironmentError as exc:
        logger.error("Client initialisation failed: %s", exc)
        print_validation_error(str(exc))
        sys.exit(1)

    # ── Step 4: Place Order ──────────────────────────────────────────────────
    try:
        console.print("[bold cyan]>> Submitting order to Binance Futures Testnet...[/bold cyan]")
        response = place_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            qty=qty,
            price=price,
        )

    except BinanceAPIException as exc:
        print_api_error(exc)
        console.print("[bold red][FAILED]  Order failed. See bot_execution.log for full details.[/bold red]\n")
        sys.exit(1)

    except BinanceRequestException as exc:
        logger.error("Network error: %s", exc)
        print_validation_error(
            f"Network error communicating with Binance Testnet.\n{exc}\n"
            "Check your internet connection and try again."
        )
        sys.exit(1)

    except RuntimeError as exc:
        logger.error("Unexpected runtime error: %s", exc)
        print_validation_error(str(exc))
        sys.exit(1)

    # ── Step 5: Display Result ───────────────────────────────────────────────
    print_order_result(response, side)

    status = response.get("status", "")
    if status in ("FILLED", "PARTIALLY_FILLED", "NEW"):
        console.print(
            "[bold green][SUCCESS]  Order placed successfully. Full details logged to bot_execution.log[/bold green]\n"
        )
    else:
        console.print(
            f"[bold yellow][WARNING]  Order status: {status}. Check bot_execution.log for details.[/bold yellow]\n"
        )


if __name__ == "__main__":
    main()
