from time import sleep
import pandas as pd
from datetime import datetime
from utils.db_connector import PGConnector
from utils.token_generator import get_access_token

ACCESS_TOKEN, GROWW, FEED = get_access_token()

db = PGConnector()
conn, cursor = db.get_db_conn_cursor()

def _cast_value(value, data_type):
    """Cast and handle NaN/None values for database insertion"""
    if pd.isna(value) or value == 'NaN':
        return None
    
    if data_type == 'date':
        try:
            if isinstance(value, str):
                return datetime.strptime(value, '%Y-%m-%d').date() if value else None
            else:
                return value
        except:
            return None
    elif data_type in ('bigint', 'int'):
        try:
            return int(value) if pd.notna(value) and value != 'NaN' else None
        except:
            return None
    elif data_type == 'float':
        try:
            return float(value) if pd.notna(value) and value != 'NaN' else None
        except:
            return None
    else:  # varchar
        return str(value) if pd.notna(value) and value != 'NaN' else None

def save_instrument_eq():
    instrument_eq = pd.read_csv("~/work/quant-trading/trading-bot/instrument/instrument_eq.csv")
    for i, instrument in instrument_eq.iterrows():
        try:
            market_cap = GROWW.get_quote(
                exchange=GROWW.EXCHANGE_NSE,
                segment=GROWW.SEGMENT_CASH,
                trading_symbol=str(instrument["trading_symbol"])
            )["market_cap"]
        except Exception as e:
            market_cap = None
        
        sleep(0.1)
        try:  
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
                    _cast_value(instrument["exchange"], 'varchar'),
                    _cast_value(instrument["exchange_token"], 'varchar'),
                    _cast_value(instrument["trading_symbol"], 'varchar'),
                    _cast_value(instrument["groww_symbol"], 'varchar'),
                    _cast_value(instrument["name"], 'varchar'),
                    _cast_value(instrument["instrument_type"], 'varchar'),
                    _cast_value(instrument["segment"], 'varchar'),
                    _cast_value(instrument["series"], 'varchar'),
                    _cast_value(instrument["isin"], 'varchar'),
                    _cast_value(instrument["underlying_symbol"], 'varchar'),
                    _cast_value(instrument["underlying_exchange_token"], 'bigint'),
                    _cast_value(instrument["expiry_date"], 'date'),
                    _cast_value(instrument["strike_price"], 'float'),
                    _cast_value(instrument["lot_size"], 'bigint'),
                    _cast_value(instrument["tick_size"], 'float'),
                    _cast_value(instrument["freeze_quantity"], 'bigint'),
                    _cast_value(instrument["is_reserved"], 'int'),
                    _cast_value(instrument["buy_allowed"], 'int'),
                    _cast_value(instrument["sell_allowed"], 'int'),
                    _cast_value(instrument["internal_trading_symbol"], 'varchar'),
                    _cast_value(instrument["is_intraday"], 'int'),
                    _cast_value(market_cap, 'bigint')
                )
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error saving instrument at row {i}: {str(e)}")

def save_instrument_idx():
    instrument_idx = pd.read_csv("~/work/quant-trading/trading-bot/instrument/instrument_idx.csv")
    for i, instrument in instrument_idx.iterrows():
        try:
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
                    is_intraday = EXCLUDED.is_intraday
                """,
                (
                    _cast_value(instrument["exchange"], 'varchar'),
                    _cast_value(instrument["exchange_token"], 'varchar'),
                    _cast_value(instrument["trading_symbol"], 'varchar'),
                    _cast_value(instrument["groww_symbol"], 'varchar'),
                    _cast_value(instrument["name"], 'varchar'),
                    _cast_value(instrument["instrument_type"], 'varchar'),
                    _cast_value(instrument["segment"], 'varchar'),
                    _cast_value(instrument["series"], 'varchar'),
                    _cast_value(instrument["isin"], 'varchar'),
                    _cast_value(instrument["underlying_symbol"], 'varchar'),
                    _cast_value(instrument["underlying_exchange_token"], 'bigint'),
                    _cast_value(instrument["expiry_date"], 'date'),
                    _cast_value(instrument["strike_price"], 'float'),
                    _cast_value(instrument["lot_size"], 'bigint'),
                    _cast_value(instrument["tick_size"], 'float'),
                    _cast_value(instrument["freeze_quantity"], 'bigint'),
                    _cast_value(instrument["is_reserved"], 'int'),
                    _cast_value(instrument["buy_allowed"], 'int'),
                    _cast_value(instrument["sell_allowed"], 'int'),
                    _cast_value(instrument["internal_trading_symbol"], 'varchar'),
                    _cast_value(instrument["is_intraday"], 'int')
                )
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error saving instrument at row {i}: {str(e)}")