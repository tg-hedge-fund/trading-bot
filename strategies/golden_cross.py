# this strategy is for short ema crossing over the longer ema line
# will be applied on nifty 500 trades (because of volume concerns)
# time frame: 1hour or 1day
# paper trading mode please
# golden cross is lagging indicator, move has already happened before this indicator spots it

import asyncio
import time
from datetime import datetime, timedelta

import schedule

from api.historical_data import get_historical_data
from api.live_data import stream_live_data_by_quote
from trade_utils.ta_indicators import calculate_ema, calculate_ema_crossover
from utils.discord_bot import send_message_via_discord_bot

ema_50 = []
ema_100 = []

list_of_stocks = ["NIFTY"]
GROWW_SYMBOL = "NSE-NIFTY"
EXCHANGE = "NSE"
CANDLE_INTERVAL = "1hour"
SEGMENT = "CASH"

historical_data = []
data = []
ema_data = []

def get_historical_data_populated():
    global historical_data
    # get the end_time, which is the current_time, and the start_time, which will be 150 days previous to the current_time
    end_time = datetime.now()
    end_time_formatted = end_time.strftime("%Y-%m-%d %H:%M:%S")
    start_time = end_time - timedelta(150)
    start_time_formatted = start_time.strftime("%Y-%m-%d %H:%M:%S")
    historical_data = get_historical_data(start_time_formatted, end_time_formatted, GROWW_SYMBOL, EXCHANGE, SEGMENT, CANDLE_INTERVAL)
    closing_prices_historical_data = [i[4] for i in historical_data["candles"]]
    return closing_prices_historical_data

async def get_live_quote_by_hour():
    global data, ema_data
    data = stream_live_data_by_quote(EXCHANGE, SEGMENT, GROWW_SYMBOL)
    last_traded_price_data = data["last_price"]
    get_historical_data_populated()
    #set ema data here
    ema_data = [historical_data + last_traded_price_data]
    return ema_data

def calculate_crossover_every_hour():
    for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
        schedule.every().__getattribute__(day).at("09:15").do(get_live_quote_by_hour)
        schedule.every().__getattribute__(day).at("10:15").do(get_live_quote_by_hour)
        schedule.every().__getattribute__(day).at("11:15").do(get_live_quote_by_hour)
        schedule.every().__getattribute__(day).at("12:15").do(get_live_quote_by_hour)
        schedule.every().__getattribute__(day).at("13:15").do(get_live_quote_by_hour)
        schedule.every().__getattribute__(day).at("14:15").do(get_live_quote_by_hour)
        schedule.every().__getattribute__(day).at("15:15").do(get_live_quote_by_hour)
        # schedule.every().__getattribute__(day).at("16:15").do(get_live_quote_by_hour)

    while True:
        schedule.run_pending()

        current_time = datetime.now().time()
        market_start = datetime.strptime("09:15", "%H:%M").time()
        market_end = datetime.strptime("15:30", "%H:%M").time()

        if market_start <= current_time <= market_end and ema_data:
            ema_50 = calculate_ema(50, ema_data)
            ema_100 = calculate_ema(100, ema_data)

            crossover_50_100 = calculate_ema_crossover(ema_50, ema_100)

            for i in range(len(crossover_50_100)):
                if crossover_50_100[i][0] > crossover_50_100[i][1]:
                    send_message_via_discord_bot("50 ema has crossed 100 ema for NIFTY")
                else:
                    send_message_via_discord_bot("50 ema has broken below 100 ema for NIFTY")

        time.sleep(60)
