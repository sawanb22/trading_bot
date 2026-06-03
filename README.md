# Binance Futures Testnet Trading Bot 🤖

A robust, modular Python CLI application for placing **MARKET** and **LIMIT** orders on the **Binance USDT-M Futures Testnet**. Built as a Python Developer Intern assignment submission.

> ⚠️ **Testnet Only** — This bot is hard-coded to the Binance Futures Testnet. No real funds can be spent.

---

## ✨ Features

- 📊 **Market & Limit Orders** — Full support for both order types with `timeInForce: GTC` defaulted on LIMIT
- 🛡️ **Strict Input Validation** — Fails fast with clear error messages before any API call is made
- 🎨 **Rich Terminal UI** — Beautiful tables, semantic colors (green/red), and error panels powered by [`rich`](https://github.com/Textualize/rich)
- 📝 **Comprehensive Logging** — Every request and response is appended to [bot_execution.log](./bot_execution.log) for audit purposes
- 🔐 **Secure Credential Handling** — API keys loaded from `.env` (configured via [.env.example](./.env.example) and never committed to version control)
- 🏗️ **Modular Architecture** — CLI ([cli.py](./cli.py)) strictly separated from business logic ([bot/](./bot)) and tests ([tests/](./tests)) for testability and reusability

---

## 📁 Project Structure

```
trading_bot/
├── .env                    ← Your Testnet credentials (git-ignored)
├── .env.example            ← Committed template (no real values)
├── .gitignore
├── requirements.txt
├── cli.py                  ← Entry point (arg parsing + rich UI)
├── bot_execution.log       ← Generated at runtime (audit trail, committed)
├── bot/
│   ├── __init__.py
│   ├── client.py           ← Loads .env, creates Binance Testnet client
│   ├── mock_client.py      ← Mock client for local offline simulation
│   ├── orders.py           ← Builds payload, submits order, handles exceptions
│   ├── validators.py       ← Pure input validation functions
│   └── logging_config.py   ← Singleton file + console logger
└── tests/
    ├── test_cli.py         ← CLI integration tests
    ├── test_orders.py      ← Orders API mock tests
    └── test_validators.py  ← Pure validation unit tests
```

---

## 🔧 Prerequisites

- **Python 3.10+** (tested on 3.14.3)
- A [Binance](https://binance.com) or GitHub account (to log into the Testnet)
- Testnet account at **[testnet.binancefuture.com](https://testnet.binancefuture.com)**

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/sawanb22/trading_bot.git
cd trading_bot
```

### 2. Create and activate a virtual environment

```bash
# Create
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (macOS / Linux)
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your Testnet API credentials

```bash
# Copy the template
copy .env.example .env      # Windows
cp .env.example .env        # macOS / Linux
```

Then open `.env` and replace the placeholder values:

```dotenv
BINANCE_API_KEY=your_actual_testnet_api_key
BINANCE_API_SECRET=your_actual_testnet_api_secret
```

> **How to get Testnet keys:**
> 1. Visit [testnet.binancefuture.com](https://testnet.binancefuture.com)
> 2. Log in with your Binance or GitHub account
> 3. Go to **API Management** → Generate new key pair
> 4. Copy the **Secret Key immediately** — it is shown only once

> **Tip:** If your Testnet USDT balance is 0, use the faucet button on the Testnet dashboard to receive dummy funds.

---

## 🚀 Usage

### MARKET Order (Buy)

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.01
```

### LIMIT Order (Sell)

```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --qty 0.1 --price 3500.00
```

### Mock/Simulated Mode (No API keys required)
To run executions and generate logs without configured API credentials:
```bash
# Market order simulation
python cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.01 --mock

# Limit order simulation
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --qty 0.1 --price 3500.00 --mock
```

### Help

```bash
python cli.py --help
```

### Running Tests
To run the automated unit and integration tests:
```bash
python -m unittest discover -s tests
```

### All Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--symbol` | ✅ | Trading pair. Must end with `USDT` (e.g. `BTCUSDT`) |
| `--side` | ✅ | `BUY` or `SELL` |
| `--type` | ✅ | `MARKET` or `LIMIT` |
| `--qty` | ✅ | Quantity — must be > 0 (e.g. `0.01`) |
| `--price` | LIMIT only | Limit price — required for LIMIT, rejected for MARKET |
| `--mock` | ❌ | Run in simulated mode (no API connection or credentials needed) |

---

## 📺 Terminal Output Examples

### ✅ Successful Market Order

```
╭─────────────────────────────────────────────╮
│       📋  Order Summary  (Pre-Execution)    │
├────────────────┬────────────────────────────┤
│ Parameter      │ Value                       │
├────────────────┼────────────────────────────┤
│ Symbol         │ BTCUSDT                     │
│ Side           │ BUY                         │
│ Type           │ MARKET                      │
│ Quantity       │ 0.01                        │
│ Price          │ Market Price                │
│ TimeInForce    │ N/A                         │
╰────────────────┴────────────────────────────╯

⚡ Submitting order to Binance Futures Testnet...

╭──────────────────────────────────────────────╮
│    ✔  Execution Result — Order Accepted      │
├──────────────────┬───────────────────────────┤
│ Order ID         │ 8389765                   │
│ Symbol           │ BTCUSDT                   │
│ Side             │ BUY                       │
│ Status           │ FILLED                    │
│ Executed Qty     │ 0.01                      │
│ Avg Price        │ 67500.00                  │
╰──────────────────┴───────────────────────────╯

✔  Order placed successfully. Full details logged to bot_execution.log
```

### ❌ Validation Error (LIMIT without price)

```
╭──────────────────────────────────────────────╮
│              Validation Error                │
│                                              │
│  ✖  A valid price is required for LIMIT      │
│     orders. Use --price <value>              │
╰──────────────────────────────────────────────╯
```

---

## 📋 Logging

All activity is appended to [bot_execution.log](./bot_execution.log) in the project root:

```
[2026-06-02 14:30:01] [INFO    ] — Submitting BUY MARKET order | Symbol: BTCUSDT | Qty: 0.01
[2026-06-02 14:30:02] [DEBUG   ] — Preparing to submit order | Payload: {'symbol': 'BTCUSDT', 'side': 'BUY', 'type': 'MARKET', 'quantity': 0.01}
[2026-06-02 14:30:03] [INFO    ] — Order accepted by exchange | Raw response: {'orderId': 8389765, 'status': 'FILLED', ...}
```

Log levels used:
| Level | Content |
|-------|---------|
| `DEBUG` | Raw request payload |
| `INFO` | Order submissions and raw API responses |
| `ERROR` | API rejections, network errors, stack traces |

---

## 📐 Assumptions Made

| Assumption | Rationale |
|------------|-----------|
| `timeInForce` defaults to `GTC` | Good Till Cancelled is the most common use case for LIMIT orders |
| Only USDT-M Futures supported | Assignment specifies USDT-Margined only; Coin-M and Spot are blocked |
| Price rejected for MARKET orders | Prevents user confusion — MARKET executes at exchange best price |
| Symbol auto-uppercased | Reduces friction; exchange API requires uppercase |
| `testnet=True` is hard-coded | Safety measure — this binary cannot be accidentally pointed at live exchange |

---

## 🔒 Security Notes

- `.env` is listed in [.gitignore](./.gitignore) — it will **never** be committed
- Only [.env.example](./.env.example) (with placeholder values) is committed
- Testnet keys are functionally useless on the Mainnet (different URL, different signatures)

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `python-binance` | 1.0.19 | Binance API client with HMAC SHA256 signing |
| `python-dotenv` | 1.0.1 | Secure `.env` credential loading |
| `rich` | 13.7.1 | Terminal tables, panels, colors |

---

## 📬 Submission Checklist

- [x] Source code in public GitHub repository with clean commit history
- [x] [README.md](./README.md) fully documented with setup steps and run instructions
- [x] [requirements.txt](./requirements.txt) present with pinned versions
- [x] [bot_execution.log](./bot_execution.log) included with proof of MARKET + LIMIT orders
- [x] `.env` excluded from repository (only [.env.example](./.env.example) committed)
