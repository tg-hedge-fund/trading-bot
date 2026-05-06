# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

```bash
# Full application (all threads)
python main.py

# Strategy only
python -m strategies.golden_cross

# Generate Groww API token
python generate_token.py

# Install dependencies
pip install -r requirements.txt
```

Environment is selected via `TGHF_ENV` env var (`dev` or `prod`), which loads the corresponding `.env.{env}` and `config/{env}.yaml` files.

## Architecture Overview

A multi-threaded Python trading assistant that monitors Indian stock indices (NIFTY, BANKNIFTY, etc.) for EMA crossovers and alerts via Discord.

### Thread Model (`main.py`)

`main.py` starts four concurrent subsystems:
1. **Wrapper API** — FastAPI read-only proxy to the Groww API (Basic Auth, Argon2-verified)
2. **Scheduler** — Instrument sync (Sundays), token refresh (daily 07:00/07:01), Golden Cross analysis (Mon–Fri at each hour 09–15)
3. **Discord Bot** — Async event loop with an async message queue; routes messages to different channels by type (INDICES, PORTFOLIO, LOGS, HEARTBEAT)
4. **Heartbeat** — Pings Discord every 5 minutes

### Strategy Engine (`strategies/golden_cross.py`)

`GoldenCross` computes 50-period vs 100-period EMA for each index. Sends Discord alerts only when:
- EMAs **cross** (sign change in consecutive diff)
- EMAs **converge** (diff within 0.1% of price)
- EMAs show a **converging pattern** (abs diff strictly decreasing over 3 points)

Uses `ThreadPoolExecutor` (default 5 workers) with a 20-second per-future timeout.

### Configuration & Secrets (`utils/`)

- `config_reader.py` loads YAML from `config/{env}.yaml`; encrypted values are decrypted with AES-CBC + PBKDF2 via `app_config.py`
- Encryption key is derived from an env var; never stored in plaintext
- YAML flags `instrument_and_eq_schedule` and `golden_cross_schedule` enable/disable those subsystems

### API Layer (`api_utils/`)

- `groww_api_handlers.py` — historical candles, live quotes, portfolio calls to Groww
- `wrapper_api.py` — FastAPI proxy exposing `/api/v1/health`, `/api/v1/history`, `/api/v1/live`
- `auth.py` — `BasicAuthHandler` using Argon2

### Technical Analysis (`trade_utils/`)

- `ta_indicators.py` — EMA (smoothing factor 2), SMA, RSI, crossover detection
- Price series = historical candles + live quote stitched together

### Database (PostgreSQL)

Schema in `sql/`: `users`, `instrument_eq`, `instrument_idx`, `portfolio`. Connection managed in `utils/db_connector.py`.

### Discord Channels

Four channels configured via `.env.*` vars: `DISCORD_INDICES_CHANNEL_ID`, `DISCORD_HEARTBEAT_CHANNEL_ID`, `DISCORD_PORTFOLIO_CHANNEL_ID`, `DISCORD_LOGS_CHANNEL_ID`.

## Key Configuration Knobs

| Location | Key | Effect |
|---|---|---|
| `config/{env}.yaml` | `golden_cross_schedule` | Enable/disable strategy runs |
| `config/{env}.yaml` | `instrument_and_eq_schedule` | Enable/disable Sunday instrument sync |
| `strategies/golden_cross.py` | `max_workers` | Thread pool size for index analysis |
| `strategies/golden_cross.py` | convergence threshold | `0.001` (0.1% of price) |
| `main.py` | schedule times | Hardcoded hourly slots 09–15 Mon–Fri |
