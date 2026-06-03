# Binance Futures Testnet Trading Bot 🤖

A robust, modular, and fully tested Python CLI application for placing **MARKET** and **LIMIT** orders on the **Binance USDT-M Futures Testnet**. Built as an assignment submission for the Python Developer Intern role at Primetrade.ai.

---

## 💡 Project Understanding & Implementation

This application implements a complete Binance Futures testnet client that strictly separates concerns (CLI representation, validation logic, API wrappers, and structured logging). 

### 📋 Requirements & Evaluation Criteria Mapping

| Category | Hiring Assignment Requirement | Implementation details & Anchors | Status |
| :--- | :--- | :--- | :---: |
| **Core Functions** | Place MARKET & LIMIT orders (USDT-M) | Managed in [bot/orders.py](./bot/orders.py) via `python-binance`. | ✅ |
| **Core Functions** | Support both BUY and SELL sides | Checked and handled for all types in [bot/orders.py](./bot/orders.py). | ✅ |
| **CLI Input** | Accept symbol, side, type, qty, price | Fully implemented using `argparse` in [cli.py](./cli.py). | ✅ |
| **Input Validation** | Validate quantity > 0, price for LIMIT, symbol ends with USDT | Pure validation rules implemented in [bot/validators.py](./bot/validators.py). | ✅ |
| **User Interface** | Print order request summary & response details | Rich styled tables for summary and execution results in [cli.py](./cli.py). | ✅ |
| **Exception Handling** | Catch validation, API, and network errors | Structured try-except blocks and clean exit codes in [cli.py](./cli.py). | ✅ |
| **Logging** | Audit API requests, responses, and errors | Logs structured dynamically in [bot_execution.log](./bot_execution.log). | ✅ |
| **Architecture** | Structured CLI, client, API, and logging layers | Decoupled modular design under the [bot/](./bot) package. | ✅ |
| **Deliverables** | Source code, `requirements.txt`, logs, and `README.md` | All files structured and pushed to the repository. | ✅ |

### 🌟 Bonus Features Implemented

* **Enhanced CLI UX (UX & Design)**:
  - Interactive CLI outputs featuring stylized error panels, pre-execution summary tables, and color-coded (green/red) execution tables powered by [`rich`](https://github.com/Textualize/rich).
* **Local Simulation Mode (Offline/Mock Mode)**:
  - Added a `--mock` flag and [bot/mock_client.py](./bot/mock_client.py) which simulates the real Binance Futures API responses locally. This allows running orders, verifying log output, and executing the app without needing active Testnet API keys.

---

## 📁 Project Structure

* [cli.py](./cli.py) — CLI entry point handling argument parsing and console UI presentation.
* [requirements.txt](./requirements.txt) — Pinned library dependencies (`python-binance`, `python-dotenv`, `rich`).
* [bot_execution.log](./bot_execution.log) — Generated audit trail containing logged requests, responses, and error traces.
* [.gitignore](./.gitignore) — Configured to ignore caches and virtual envs while preserving the required `bot_execution.log`.
* [.env.example](./.env.example) — Configured template for local credentials.
* **[bot/](./bot)**:
  * [bot/client.py](./bot/client.py) — Authenticates credentials and instantiates the Binance API client.
  * [bot/mock_client.py](./bot/mock_client.py) — Implements local offline simulation of orders.
  * [bot/orders.py](./bot/orders.py) — Constructs order payloads and interacts with the client interface.
  * [bot/validators.py](./bot/validators.py) — Contains pure validation functions for inputs.
  * [bot/logging_config.py](./bot/logging_config.py) — Configures logs rotation and levels.
* **[tests/](./tests)**:
  * [tests/test_cli.py](./tests/test_cli.py) — Integration tests for CLI arguments, mock pathways, and exit codes.
  * [tests/test_orders.py](./tests/test_orders.py) — Mock API tests verifying payloads, exceptions, and order routing.
  * [tests/test_validators.py](./tests/test_validators.py) — Unit tests covering input constraints, edge cases, and bounds.

---

## 🔧 Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/sawanb22/trading_bot.git
cd trading_bot
```

### 2. Set up virtual environment
```bash
# Create environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration (For live Testnet API keys)
Rename the template and configure your keys:
```bash
copy .env.example .env
```
Inside `.env`:
```dotenv
BINANCE_API_KEY=your_actual_testnet_api_key
BINANCE_API_SECRET=your_actual_testnet_api_secret
BINANCE_FUTURES_URL=https://testnet.binancefuture.com
```

---

## 🚀 Execution & Usage Examples

### 1. Running in Mock/Simulated Mode (No API keys needed)
Use the `--mock` flag to run a simulated execution locally:
```bash
# Place a MARKET BUY order
python cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.01 --mock

# Place a LIMIT SELL order
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --qty 0.1 --price 3500.00 --mock
```

### 2. Running Live on Binance Futures Testnet
*(Ensure valid keys are set in your `.env`)*
```bash
# Live MARKET BUY order
python cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.005

# Live LIMIT SELL order
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --qty 0.05 --price 3650.00
```

### 3. Help Command
```bash
python cli.py --help
```

---

## 🧪 Running Automated Tests

Run the full automated unit and integration test suite:
```bash
python -m unittest discover -s tests
```

---

## 📝 Assumptions Made

1. **USDT-M Futures Only**: All trading symbols must end with `USDT` (e.g., `BTCUSDT`). Coin-Margined and Spot markets are explicitly rejected by validators.
2. **Default Time-in-Force**: LIMIT orders default to `timeInForce: GTC` (Good Till Cancelled).
3. **No Price for Market Orders**: Providing a price for MARKET orders is rejected during input validation to prevent user confusion.
4. **Hard-coded Safety**: Built-in endpoints default to paper trading hosts (`testnet.binancefuture.com` or `demo-fapi.binance.com`) to prevent accidental mainnet execution.
