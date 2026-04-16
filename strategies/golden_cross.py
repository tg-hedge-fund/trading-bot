# this strategy is for short ema crossing over the longer ema line
# will be applied on nifty 500 trades (because of volume concerns)
# time frame: 1hour or 1day
# paper trading mode please
# golden cross is lagging indicator, move has already happened before this indicator spots it

import concurrent.futures as _cf
import time
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime, timedelta

from api.groww_api_handlers import get_historical_data, stream_live_data_by_quote
from trade_utils.ta_indicators import calculate_ema, calculate_ema_crossover
from utils.constants import INDICES_LIST, MESSAGE_TYPES
from utils.discord_bot import send_message_via_discord_bot
from utils.utils import logger, run_thread

ema_50 = []
ema_100 = []

# historical_data = []
# data = []
# ema_data = []

class GoldenCross:
    def __init__(self, symbol, exchange, candle_interval, segment):
        self.GROWW_SYMBOL = symbol
        self.EXCHANGE = exchange
        self.CANDLE_INTERVAL = candle_interval
        self.SEGMENT = segment

    def get_historical_data_populated(self):
        # global historical_data
        # get the end_time, which is the current_time, and the start_time, which will be 150 days previous to the current_time
        end_time = datetime.now() - timedelta(hours=1)
        end_time_formatted = end_time.strftime("%Y-%m-%d %H:%M:%S")
        start_time = end_time - timedelta(days=150) + timedelta(hours=1)
        start_time_formatted = start_time.strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"start_time: {start_time_formatted}, end_time: {end_time_formatted}")
        historical_data = get_historical_data(start_time_formatted, end_time_formatted, f"{self.EXCHANGE}-{self.GROWW_SYMBOL}", self.EXCHANGE, self.SEGMENT, self.CANDLE_INTERVAL)

        if historical_data is not None:
            # add closing prices to the array, which will be returned for ema calculation
            closing_prices_historical_data = [i[4] for i in historical_data["candles"]]
            return closing_prices_historical_data
        else:
            logger.error("historical_data is none, skipping the schedule")
            return None

    def get_live_quote_by_hour(self):
        closing_prices_historical_data = self.get_historical_data_populated()
        data = stream_live_data_by_quote(self.EXCHANGE, self.SEGMENT, self.GROWW_SYMBOL)
        if data is not None and closing_prices_historical_data is not None:
            last_traded_price_data = data["last_price"]
            closing_prices_historical_data.append(last_traded_price_data)
        else:
            logger.error("live quote feed is none, skipping schedule")
            return

        ema_data = closing_prices_historical_data

        current_time = datetime.now().time()
        market_start = datetime.strptime("09:15", "%H:%M").time()
        market_end = datetime.strptime("15:30", "%H:%M").time()
        logger.info(f"Current Time: {current_time}, market_start: {market_start}, market_end: {market_end}")

        if ema_data:
            ema_50 = calculate_ema(50, ema_data)
            ema_100 = calculate_ema(100, ema_data)
            logger.info("Calculating ema crossover")
            crossover_50_100 = calculate_ema_crossover(ema_50, ema_100)
            total_crossover_points = len(crossover_50_100)

            if crossover_50_100[total_crossover_points-1][0] > crossover_50_100[total_crossover_points-1][1]:
                send_message_via_discord_bot(f"50 ema has crossed above 100 ema for {self.GROWW_SYMBOL} on {self.CANDLE_INTERVAL} chart", MESSAGE_TYPES.INDICES)
            else:
                send_message_via_discord_bot(f"50 ema has broken below 100 ema for {self.GROWW_SYMBOL} on {self.CANDLE_INTERVAL} chart", MESSAGE_TYPES.INDICES)
        return ema_data


def get_crossover_for_all_indices():
    def get_crossover_by_thread(symbol):
        logger.info(f"Calculating crossover for {symbol} - start")
        try:
            # Use the same interval format used elsewhere ("1h")
            gc_strategy = GoldenCross(symbol=symbol, exchange="NSE", candle_interval="1hour", segment="CASH")
            time.sleep(0.5)
            return gc_strategy.get_live_quote_by_hour()
        except Exception as e:
            logger.error(f"Unhandled error while processing {symbol}: {e}", exc_info=True)
            return None

    symbols = list(INDICES_LIST)
    logger.info(f"Starting golden cross processing for symbols: {symbols}")

    if not symbols:
        logger.info("No symbols configured in INDICES_LIST, nothing to do")
        return

    TIMEOUT_SECS = 20
    max_workers = 5

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit each symbol as a separate future so we can apply per-task timeouts and error handling
        futures = {executor.submit(get_crossover_by_thread, s): s for s in symbols}

        for fut in _cf.as_completed(futures.keys(), timeout=None):
            symbol = futures.get(fut)
            try:
                result = fut.result(timeout=0)  # result is ready because as_completed yielded it
                logger.info(f"Completed {symbol}. Result present: {bool(result)}")
            except _cf.TimeoutError:
                # This branch is unlikely since as_completed yields finished futures, but kept for completeness
                logger.error(f"Timeout while waiting for result for {symbol}")
            except Exception as e:
                logger.error(f"Error while computing crossover for {symbol}: {e}", exc_info=True)

        # After handling completed futures, check for any that might still be running and apply timeout
        for fut, symbol in list(futures.items()):
            if not fut.done():
                try:
                    fut.result(timeout=TIMEOUT_SECS)
                    logger.info(f"Finished {symbol} after waiting additional {TIMEOUT_SECS}s")
                except _cf.TimeoutError:
                    logger.error(f"get_live_quote_by_hour timed out for {symbol} after {TIMEOUT_SECS}s")
                except Exception as e:
                    logger.error(f"Error in delayed result for {symbol}: {e}", exc_info=True)

    logger.info("Finished processing all configured indices")
