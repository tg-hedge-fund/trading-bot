from datetime import datetime, timedelta

from utils.constants import MESSAGE_TYPES
from utils.discord_bot import send_message_via_discord_bot
from utils.token_generator import get_fyers_client

ACCESS_TOKEN, FYERS = get_fyers_client()

# Fyers caps a single history request at 100 days for intraday resolutions, 366 for daily
INTRADAY_MAX_DAYS = 100
DAILY_MAX_DAYS = 366


def refresh_fyers_credentials():
    global ACCESS_TOKEN, FYERS
    try:
        ACCESS_TOKEN, FYERS = get_fyers_client()
    except Exception as e:
        send_message_via_discord_bot(f"Error refreshing FYERS credentials: {e}", MESSAGE_TYPES.LOGS)
        raise


def _check_response(response):
    if not isinstance(response, dict) or response.get("s") != "ok":
        raise RuntimeError(response)
    return response


# https://myapi.fyers.in/docsv3#tag/Data-Api/paths/~1DataApi/post
def get_historical_data(symbol, resolution, range_from: datetime, range_to: datetime):
    """
    symbol: Fyers symbol, e.g. 'NSE:NIFTY50-INDEX' or 'NSE:SBIN-EQ'
    resolution: '1', '5', '15', '60', '1D', ...
    Returns {"candles": [[epoch, open, high, low, close, volume], ...]} or None on error.
    """
    max_days = DAILY_MAX_DAYS if resolution.upper() in ("D", "1D") else INTRADAY_MAX_DAYS
    try:
        candles = {}
        chunk_start = range_from
        while chunk_start < range_to:
            chunk_end = min(chunk_start + timedelta(days=max_days), range_to)
            response = _check_response(FYERS.history(data={
                "symbol": symbol,
                "resolution": resolution,
                "date_format": "0",
                "range_from": str(int(chunk_start.timestamp())),
                "range_to": str(int(chunk_end.timestamp())),
                "cont_flag": "1",
            }))
            for candle in response.get("candles", []):
                candles[candle[0]] = candle
            chunk_start = chunk_end

        return {"candles": [candles[ts] for ts in sorted(candles)]}
    except Exception as e:
        send_message_via_discord_bot(f"Error in fetching historical data from FYERS API: {e}", MESSAGE_TYPES.LOGS)
        return None


def get_quote(symbol):
    """Returns the quote values dict for a symbol (last price under 'lp') or None on error."""
    try:
        response = _check_response(FYERS.quotes(data={"symbols": symbol}))
        quote = response["d"][0]
        if quote.get("s") != "ok":
            raise RuntimeError(quote)
        return quote["v"]
    except Exception as e:
        send_message_via_discord_bot(f"Error in fetching live quote from FYERS API: {e}", MESSAGE_TYPES.LOGS)
        return None


def get_portfolio():
    """Returns {"holdings": [...], "overall": {...}} or None on error."""
    try:
        return _check_response(FYERS.holdings())
    except Exception as e:
        send_message_via_discord_bot(f"Error in fetching portfolio from FYERS API: {e}", MESSAGE_TYPES.LOGS)
        return None
