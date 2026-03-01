import os

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException

from api.groww_api_handlers import get_historical_data, stream_live_data_by_quote
# from groww_api_handlers import get_historical_data, stream_live_data_by_quote

load_dotenv()

API_TOKEN = os.getenv("DATA_PROXY_TOKEN")

app = FastAPI(
    title="Groww Read-Only Data Proxy",
    description="Internal read-only proxy for Historical and Live data",
)

# Create a router with /api/v1 prefix
prefix_router = APIRouter(prefix="/api/v1")

# Change stock universe later
STOCK_UNIVERSE = [
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK",
    "SBIN",
    "ITC",
    "LT",
    "AXISBANK",
    "BAJFINANCE",
]

EXCHANGE = "NSE"
SEGMENT = "CASH"
CANDLE_INTERVAL = "1d"


def authorize(x_token: str):
    if x_token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


# Endpoints under /api/v1
@prefix_router.get("/health")
def health():
    return {"status": "200", "message": "Healthy"}


@prefix_router.get("/history")
def get_historical_data_proxy(
    exchange,
    groww_symbol,
    segment,
    candle_interval,
    start_time,
    end_time,
):
    # Validate exchange
    if exchange.upper() not in ["NSE", "BSE"]:
        return {"status": "400", "message": "Exchange must be NSE or BSE"}

    # Validate time format
    # try:
    #     start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    #     end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    # except ValueError:
    #     return {"status": "400", "message": "Time format must be %Y-%m-%d %H:%M:%S"}

    # Validate 150 day limit
    # time_diff = (end_dt - start_dt).days
    # if time_diff > 150:
    #     return {"status": "400", "message": "Time difference between start_time and end_time cannot exceed 150 days"}

    # if start_dt > end_dt:
    #     return {"status": "400", "message": "start_time must be before end_time"}

    try:
        historical_data = get_historical_data(start_time=start_time, end_time=end_time, groww_symbol=f"{exchange.upper()}-{groww_symbol.upper()}", exchange=exchange.upper(), segment=segment.upper(), candle_interval=candle_interval)
        return historical_data
        # return ""
    except Exception as e:
        return {"status": "500", "message": e}


@prefix_router.get("/live")
def get_live_data_proxy(exchange, segment, trading_symbol):
    try:
        live_data = stream_live_data_by_quote(exchange=exchange, segment=segment, trading_symbol=trading_symbol)
        return live_data
        # return ""
    except Exception as e:
        return {"status": "500", "message": e}


# Default endpoint for any unimplemented routes under /api/v1
@prefix_router.get("/{path:path}")
def api_v1_default(path: str):
    return {"status": "200", "message": "N/A"}

app.include_router(prefix_router)

# Default root endpoint
@app.get("/")
def root():
    return {"status": "200", "message": "Use /api/v1/health, /api/v1/history or /api/v1/live"}


# Catch-all for any other paths not under /api/v1
@app.get("/{path:path}")
def default_endpoint(path: str):
    return {"status": "200", "message": "Use /api/v1/health, /api/v1/history or /api/v1/live"}
