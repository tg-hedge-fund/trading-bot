import psycopg2
import pandas as pd
from utils.config_reader import ConfigReader
from utils.db_connector import PGConnector
from utils.token_generator import get_access_token

ACCESS_TOKEN, GROWW, FEED = get_access_token()

config = ConfigReader()
db = PGConnector()
conn, cursor = db.get_db_conn_cursor()

def save_instrument_eq():
    instrument_eq = pd.read_csv("../instrument/instrument_eq.csv")
    try:
        for i, instrument in instrument_eq.iterrows():
            #save the instrument along with their market_cap (get via api call)
            market_cap = GROWW.get_quote(
                exchange=GROWW.EXCHANGE_NSE,
                segment=GROWW.SEGMENT_CASH,
                trading_symbol=instrument["trading_symbol"]
            )["market_cap"]
            
            cursor.execute(
                """
                INSERT INTO instrument_eq (
                    exchange, exchange_token, trading_symbol, groww_symbol, name, 
                    instrument_type, segment, series, isin, underlying_symbol, 
                    underlying_exchange_token, expiry_date, strike_price, lot_size, 
                    tick_size, freeze_quantity, is_reserved, buy_allowed, sell_allowed, 
                    internal_trading_symbol, is_intraday, market_cap
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (exchange_token, trading_symbol) 
                DO UPDATE SET
                    exchange = EXCLUDED.exchange,
                    groww_symbol = EXCLUDED.groww_symbol,
                    name = EXCLUDED.name,
                    instrument_type = EXCLUDED.instrument_type,
                    segment = EXCLUDED.segment,
                    series = EXCLUDED.series,
                    isin = EXCLUDED.isin,
                    underlying_symbol = EXCLUDED.underlying_symbol,
                    underlying_exchange_token = EXCLUDED.underlying_exchange_token,
                    expiry_date = EXCLUDED.expiry_date,
                    strike_price = EXCLUDED.strike_price,
                    lot_size = EXCLUDED.lot_size,
                    tick_size = EXCLUDED.tick_size,
                    freeze_quantity = EXCLUDED.freeze_quantity,
                    is_reserved = EXCLUDED.is_reserved,
                    buy_allowed = EXCLUDED.buy_allowed,
                    sell_allowed = EXCLUDED.sell_allowed,
                    internal_trading_symbol = EXCLUDED.internal_trading_symbol,
                    is_intraday = EXCLUDED.is_intraday,
                    market_cap = EXCLUDED.market_cap
                """,
                (
                    instrument["exchange"],
                    instrument["exchange_token"],
                    instrument["trading_symbol"],
                    instrument["groww_symbol"],
                    instrument["name"],
                    instrument["instrument_type"],
                    instrument["segment"],
                    instrument["series"],
                    instrument["isin"],
                    instrument["underlying_symbol"],
                    instrument["underlying_exchange_token"],
                    instrument["expiry_date"],
                    instrument["strike_price"],
                    instrument["lot_size"],
                    instrument["tick_size"],
                    instrument["freeze_quantity"],
                    instrument["is_reserved"],
                    instrument["buy_allowed"],
                    instrument["sell_allowed"],
                    instrument["internal_trading_symbol"],
                    instrument["is_intraday"],
                    instrument["market_cap"]
                )
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error saving instruments: {str(e)}")

def save_instrument_idx():
    instrument_idx = pd.read_csv("../instrument/instrument_idx.csv")
    try:
        for i, instrument in instrument_idx.iterrows():
            #save the instrument along with their market_cap (get via api call)
            cursor.execute(
                """
                INSERT INTO instrument_idx (
                    exchange, exchange_token, trading_symbol, groww_symbol, name, 
                    instrument_type, segment, series, isin, underlying_symbol, 
                    underlying_exchange_token, expiry_date, strike_price, lot_size, 
                    tick_size, freeze_quantity, is_reserved, buy_allowed, sell_allowed, 
                    internal_trading_symbol, is_intraday
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (exchange_token, trading_symbol) 
                DO UPDATE SET
                    exchange = EXCLUDED.exchange,
                    groww_symbol = EXCLUDED.groww_symbol,
                    name = EXCLUDED.name,
                    instrument_type = EXCLUDED.instrument_type,
                    segment = EXCLUDED.segment,
                    series = EXCLUDED.series,
                    isin = EXCLUDED.isin,
                    underlying_symbol = EXCLUDED.underlying_symbol,
                    underlying_exchange_token = EXCLUDED.underlying_exchange_token,
                    expiry_date = EXCLUDED.expiry_date,
                    strike_price = EXCLUDED.strike_price,
                    lot_size = EXCLUDED.lot_size,
                    tick_size = EXCLUDED.tick_size,
                    freeze_quantity = EXCLUDED.freeze_quantity,
                    is_reserved = EXCLUDED.is_reserved,
                    buy_allowed = EXCLUDED.buy_allowed,
                    sell_allowed = EXCLUDED.sell_allowed,
                    internal_trading_symbol = EXCLUDED.internal_trading_symbol,
                    is_intraday = EXCLUDED.is_intraday,
                """,
                (
                    instrument["exchange"],
                    instrument["exchange_token"],
                    instrument["trading_symbol"],
                    instrument["groww_symbol"],
                    instrument["name"],
                    instrument["instrument_type"],
                    instrument["segment"],
                    instrument["series"],
                    instrument["isin"],
                    instrument["underlying_symbol"],
                    instrument["underlying_exchange_token"],
                    instrument["expiry_date"],
                    instrument["strike_price"],
                    instrument["lot_size"],
                    instrument["tick_size"],
                    instrument["freeze_quantity"],
                    instrument["is_reserved"],
                    instrument["buy_allowed"],
                    instrument["sell_allowed"],
                    instrument["internal_trading_symbol"],
                    instrument["is_intraday"]
                )
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error saving instruments: {str(e)}")