# this strategy is for short ema crossing over the longer ema line
# will be applied on nifty 500 trades (because of volume concerns)
# time frame: 1hour or 1day
# paper trading mode please
# golden cross is lagging indicator, move has already happened before this indicator spots it

import concurrent.futures as _cf
import time
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from api_utils.groww_api_handlers import get_historical_data, stream_live_data_by_quote
from trade_utils.ta_indicators import calculate_ema, calculate_ema_crossover
from utils.constants import INDICES_LIST, MESSAGE_TYPES
from utils.discord_bot import send_message_via_discord_bot
from utils.utils import logger

# NOTE:
# This module deliberately only sends Discord messages when one of:
#  - the EMAs have actually crossed (sign change between the last two diffs),
#  - the EMAs are within a small threshold (near convergence),
#  - the EMAs show a converging pattern over the recent points.
#
# All decisions are based on the last up-to-10 crossover points (configurable via LAST_N).

LAST_N = 10
DEFAULT_TIMEOUT_SECS = 20
DEFAULT_MAX_WORKERS = 5


class GoldenCross:
    def __init__(self, symbol: str, exchange: str, candle_interval: str, segment: str) -> None:
        self.GROWW_SYMBOL = symbol
        self.EXCHANGE = exchange
        self.CANDLE_INTERVAL = candle_interval
        self.SEGMENT = segment

    def get_historical_data_populated(self) -> Optional[List[float]]:
        # compute end_time as current time minus 1 hour to align with closed candle
        end_time = datetime.now() - timedelta(hours=1)
        end_time_formatted = end_time.strftime("%Y-%m-%d %H:%M:%S")
        start_time = end_time - timedelta(days=150) + timedelta(hours=1)
        start_time_formatted = start_time.strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f"{self.GROWW_SYMBOL}: loading historical candles from {start_time_formatted} to {end_time_formatted}")
        historical_data = get_historical_data(
            start_time=start_time_formatted,
            end_time=end_time_formatted,
            groww_symbol=f"{self.EXCHANGE}-{self.GROWW_SYMBOL}",
            exchange=self.EXCHANGE,
            segment=self.SEGMENT,
            candle_interval=self.CANDLE_INTERVAL,
        )

        if historical_data is None:
            logger.error(f"{self.GROWW_SYMBOL}: historical_data is None")
            return None

        try:
            # candles structure expected: [open, high, low, close, last_price?] but original code used index 4
            closing_prices_historical_data = [float(i[4]) for i in historical_data["candles"]]
            return closing_prices_historical_data
        except Exception as e:
            logger.error(f"{self.GROWW_SYMBOL}: error parsing historical candles: {e}", exc_info=True)
            return None

    def _analyze_last_n_and_maybe_alert(self, ema_short: List[float], ema_long: List[float], price_series: List[float]) -> None:
        """
        Analyze only the last LAST_N points of the EMA pair and send a message only when:
         - they have crossed (sign change),
         - they are near convergence (absolute diff <= threshold),
         - they are clearly converging (abs diffs decreasing over the last 3 points).
        """
        crossover = calculate_ema_crossover(ema_short, ema_long)
        total = len(crossover)
        if total == 0:
            logger.info(f"{self.GROWW_SYMBOL}: no crossover points available to analyze")
            return

        last_n = min(LAST_N, total)
        recent: List[Tuple[float, float]] = crossover[-last_n:]
        # diffs = short - long
        diffs = [s - l for s, l in recent]
        if not diffs:
            logger.info(f"{self.GROWW_SYMBOL}: insufficient diffs to analyze")
            return

        last_diff = diffs[-1]
        prev_diff = diffs[-2] if len(diffs) > 1 else None

        # Use last long EMA value as reference for threshold if available; fall back to last price
        last_long = recent[-1][1] if recent else 0.0
        last_price = float(price_series[-1]) if price_series else last_long if last_long else 1.0

        # Threshold: 0.1% of last_long (or last price) with a lower bound to avoid zero threshold
        abs_threshold = max(0.01, abs(last_long) * 0.001, abs(last_price) * 0.001)

        reason = None
        # 1) crossed: sign change between prev_diff and last_diff (and change magnitude not trivially tiny)
        if prev_diff is not None and (prev_diff * last_diff) < 0 and abs(last_diff) > (abs_threshold * 0.5):
            reason = "crossed"
        # 2) near convergence: the last diff is within threshold
        elif abs(last_diff) <= abs_threshold:
            reason = "near_convergence"
        else:
            # 3) converging pattern: abs diffs strictly decreasing over the last 3 points
            if len(diffs) >= 3 and abs(diffs[-3]) > abs(diffs[-2]) > abs(diffs[-1]):
                reason = "converging"

        # Only send messages for the three reasons listed above
        if not reason:
            logger.info(
                f"{self.GROWW_SYMBOL}: no signal (last_diff={last_diff:.6f}, threshold={abs_threshold:.6f}) on last {last_n} points"
            )
            return

        # Compose and send message depending on reason
        if reason == "crossed":
            direction = "ABOVE" if last_diff > 0 else "BELOW"
            send_message_via_discord_bot(
                f"50 EMA has crossed {direction} 100 EMA for {self.GROWW_SYMBOL} on {self.CANDLE_INTERVAL} chart (analyzed last {last_n} points)",
                MESSAGE_TYPES.INDICES,
            )
            logger.info(f"{self.GROWW_SYMBOL}: sent cross message ({direction})")
        elif reason == "near_convergence":
            send_message_via_discord_bot(
                f"50 EMA is NEAR convergence with 100 EMA for {self.GROWW_SYMBOL} on {self.CANDLE_INTERVAL} chart — diff={last_diff:.6f} (threshold={abs_threshold:.6f}) (analyzed last {last_n} points)",
                MESSAGE_TYPES.INDICES,
            )
            logger.info(f"{self.GROWW_SYMBOL}: sent near-convergence message (diff={last_diff:.6f})")
        else:  # converging
            send_message_via_discord_bot(
                f"50 EMA and 100 EMA are CONVERGING for {self.GROWW_SYMBOL} on {self.CANDLE_INTERVAL} chart — recent diffs decreasing (analyzed last {last_n} points)",
                MESSAGE_TYPES.INDICES,
            )
            logger.info(f"{self.GROWW_SYMBOL}: sent converging message")

    def get_live_quote_by_hour(self) -> Optional[List[float]]:
        """
        Fetch historical + a live quote, compute EMAs and analyze only the last LAST_N crossover points.
        Only sends messages when a meaningful event is detected (see _analyze_last_n_and_maybe_alert).
        """
        closing_prices_historical_data = self.get_historical_data_populated()
        if closing_prices_historical_data is None:
            logger.error(f"{self.GROWW_SYMBOL}: missing historical data, aborting")
            return None

        data = stream_live_data_by_quote(self.EXCHANGE, self.SEGMENT, self.GROWW_SYMBOL)
        if data is None:
            logger.error(f"{self.GROWW_SYMBOL}: live quote feed is none, skipping schedule")
            return None

        # Expect last_price in the quote response
        try:
            last_traded_price_data = float(data.get("last_price", closing_prices_historical_data[-1]))
        except Exception:
            # Fallback: use last historical closing price
            last_traded_price_data = float(closing_prices_historical_data[-1])

        closing_prices_historical_data.append(last_traded_price_data)
        ema_data = closing_prices_historical_data

        # Market timing info retained for context; messages will still be limited by analysis logic
        current_time = datetime.now().time()
        market_start = datetime.strptime("09:15", "%H:%M").time()
        market_end = datetime.strptime("15:30", "%H:%M").time()
        logger.info(f"{self.GROWW_SYMBOL}: Current Time: {current_time}, market_start: {market_start}, market_end: {market_end}")

        # Compute EMAs regardless of market hours: user requested analysis of last points
        ema_50 = calculate_ema(50, ema_data)
        ema_100 = calculate_ema(100, ema_data)

        if not ema_50 or not ema_100:
            logger.info(f"{self.GROWW_SYMBOL}: insufficient EMA length (ema_50={len(ema_50)}, ema_100={len(ema_100)})")
            return ema_data

        # Delegate analysis & messaging to helper that only looks at the last LAST_N points
        try:
            self._analyze_last_n_and_maybe_alert(ema_50, ema_100, ema_data)
        except Exception as e:
            logger.error(f"{self.GROWW_SYMBOL}: error during analysis/alerting: {e}", exc_info=True)

        return ema_data


def get_crossover_for_all_indices(timeout_seconds: int = DEFAULT_TIMEOUT_SECS, max_workers: int = DEFAULT_MAX_WORKERS) -> None:
    """
    Run GoldenCross.get_live_quote_by_hour for all configured indices concurrently, but ensure that
    a single blocked call cannot hang the whole scheduler by using a thread pool and per-future time waits.

    This function only triggers Discord messages when the analysis logic (last LAST_N points) detects
    crossing/near-convergence/converging patterns.
    """
    def _run_for_symbol(symbol: str):
        logger.info(f"Starting GoldenCross for {symbol}")
        try:
            gc = GoldenCross(symbol=symbol, exchange="NSE", candle_interval="1h", segment="CASH")
            return gc.get_live_quote_by_hour()
        except Exception:
            logger.exception(f"Unhandled exception while running GoldenCross for {symbol}")
            return None

    symbols = list(INDICES_LIST)
    if not symbols:
        logger.info("INDICES_LIST is empty; nothing to process")
        return

    # Bound workers to a reasonable number
    workers = min(max_workers, max(1, len(symbols)))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_symbol = {executor.submit(_run_for_symbol, s): s for s in symbols}

        # Wait for futures to complete; use as_completed to process results as they arrive.
        for fut in _cf.as_completed(future_to_symbol.keys(), timeout=None):
            sym = future_to_symbol[fut]
            try:
                res = fut.result(timeout=0)  # already completed
                logger.info(f"{sym}: task finished (result present: {bool(res)})")
            except Exception:
                logger.exception(f"{sym}: error while retrieving result")

        # For any futures still running, wait a bounded amount of time to avoid indefinite hang
        for fut, sym in list(future_to_symbol.items()):
            if not fut.done():
                try:
                    fut.result(timeout=timeout_seconds)
                    logger.info(f"{sym}: finished after waiting extra {timeout_seconds}s")
                except _cf.TimeoutError:
                    logger.error(f"{sym}: get_live_quote_by_hour timed out after {timeout_seconds}s")
                except Exception:
                    logger.exception(f"{sym}: error while waiting for delayed result")

    # small pause to avoid hammering apis when this function is scheduled frequently
    time.sleep(0.25)
    logger.info("Completed get_crossover_for_all_indices run")
