# Trading Bot — Golden Cross Strategy

## Project Summary

A lightweight trading assistant that monitors major indices and sends Discord alerts when the 50-period EMA approaches, converges, or crosses the 100-period EMA. The bot fetches historical candles, adds a live quote, computes EMAs, and intelligently filters alerts to avoid noise.

## Key Features

- **EMA Monitoring**: Calculates 50-period and 100-period exponential moving averages.
- **Smart Alerts**: Sends Discord messages only for meaningful events:
  - Actual crossover (sign change between EMAs)
  - Near convergence (EMAs within a small threshold)
  - Converging pattern (absolute differences decreasing)
- **Concurrent Execution**: Runs checks for all configured indices concurrently with bounded workers and timeouts.
- **Rate-Limit Friendly**: Includes per-thread delays and configurable concurrency to avoid API rate limits.
- **Configurable**: Tunable thresholds, analysis window (last N points), and scheduling times.

## Quick Start

### Prerequisites

- Python 3.9+
- Groww API access and credentials configured
- Discord bot configured (see `utils/discord_bot.py`)

### Installation

1. From the project root, install dependencies:

```
pip install -r requirements.txt
```

2. Verify your Groww credentials and Discord bot configuration.

### Running

**Run a single strategy module** (recommended for testing):

```
python -m strategies.golden_cross
```

**Run the full application** (scheduler + Discord bot):

```
python main.py
```

**From outside the project root**, set `PYTHONPATH`:

```
PYTHONPATH=/path/to/trading-bot python -m strategies.golden_cross
```

### Configuration

- **Indices to monitor**: Edit `utils/constants.py` and update `INDICES_LIST`.
- **Scheduling**: Adjust job times in `main.py` under `run_golden_cross_schedule()`.
- **Thresholds & sensitivity**: Tune constants in `strategies/golden_cross.py`:
  - `LAST_N`: Number of recent points to analyze (default: 10)
  - `abs_threshold` multiplier: Currently 0.1% of price
- **Concurrency**: Adjust `max_workers` in `get_crossover_for_all_indices()` to control concurrent API calls.

### Troubleshooting

- **Rate-limit errors (429)**: Reduce `max_workers` or add delays between API calls.
- **Missing historical data**: Check Groww API credentials and network connectivity.
- **No alerts**: Review logs to see if the analysis detected any signals (check threshold sensitivity).

