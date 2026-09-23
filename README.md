# Stock Repo Search

**New to Python or the terminal?** Start with [BEGINNERS.md](BEGINNERS.md).

Search GitHub for repositories that analyze stocks — and for source code that actually imports the libraries those analyses use.

The app has three pieces:

- **Streamlit UI** (`app.py`) — browse repo results and library usage
- **CLI** (`stock_repo_search.py`) — same searches from a terminal
- **Code search** — find repos that call `yfinance` *and* TA-Lib, not just repos whose README says “stock analysis”

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

CLI, no extra packages required:

```bash
python stock_repo_search.py --preset quant --min-stars 200
python stock_repo_search.py --mode code --code-preset yfinance-talib
```

## GitHub token

Put a personal access token in `GITHUB_TOKEN` or paste it in the sidebar.

- Repo search works unauthenticated, but the limit is 60 requests/hour
- Code search almost always needs a token
- Classic token with `public_repo` is enough

## Repository presets

| Preset | Looks for |
|---|---|
| `analysis` | General stock / equity analysis |
| `quant` | Quantitative finance |
| `backtest` | Strategy backtesting |
| `technical` | Technical indicators |
| `fundamental` | Fundamentals / value investing |
| `sentiment` | News and social sentiment |
| `ml` | Machine-learning forecasts |
| `screener` | Screeners |
| `portfolio` | Portfolio optimization |
| `us` | US equities / yfinance |
| `ashares` | A-share / China-market tools |

## Code-search presets

These look *inside files*, then keep repositories that contain every term:

| Preset | Terms |
|---|---|
| `yfinance-talib` | `import yfinance` + `import talib` |
| `yfinance-pandas-ta` | `import yfinance` + `import pandas_ta` |
| `yfinance-backtrader` | `import yfinance` + `import backtrader` |
| `yfinance-vectorbt` | `import yfinance` + `import vectorbt` |
| `alpaca-trading` | `import alpaca` |
| `ccxt-freqtrade` | `import ccxt` |

Intersection uses the first page of each term (default 40 hits). It is a practical filter, not a complete census of GitHub.

```bash
python stock_repo_search.py --mode code --term "import yfinance" --term "import talib" --limit 50
```

## Notes

- Stars measure popularity, not strategy quality
- Many “98% accurate LSTM” repos are overfit demos
- This is not financial advice
