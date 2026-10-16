from dotenv import load_dotenv
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, status

from api_utils.auth import BasicAuthHandler
from datetime import datetime

from api_utils.fyers_api_handlers import get_historical_data, get_quote

load_dotenv()

app = FastAPI(
    title="Fyers Read-Only Data Proxy",
    description="Internal read-only proxy for Historical and Live data",
)

# Create a router with /api/v1 prefix
prefix_router = APIRouter(prefix="/api/v1")

def verify_auth(authorization = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Basic"},
        )

    auth_handler = BasicAuthHandler()
    try:
        return auth_handler.verify_credentials(authorization)
    except HTTPException:
        raise


# Public endpoint - no auth required
@prefix_router.get("/health")
def health():
    return {"status": "200", "message": "Healthy"}


# Protected endpoints - require basic auth
@prefix_router.get("/history")
def get_historical_data_proxy(
    symbol,
    resolution,
    start_time,
    end_time,
    # user = Depends(verify_auth),
):
    # Validate exchange (Fyers symbols look like NSE:SBIN-EQ)
    if symbol.split(":")[0].upper() not in ["NSE", "BSE"]:
        return {"status": "400", "message": "Symbol must be prefixed with NSE: or BSE:"}

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
        return {"status": "200", "message": "Under development"}
        historical_data = get_historical_data(
            symbol=symbol.upper(),
            resolution=resolution,
            range_from=datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S"),
            range_to=datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S"),
        )
        return historical_data
    except Exception as e:
        return {"status": "500", "message": str(e)}


@prefix_router.get("/live")
def get_live_data_proxy(
    symbol,
    # user = Depends(verify_auth),
):
    try:
        return {"status": "200", "message": "Under development"}
        live_data = get_quote(symbol.upper())
        return live_data
    except Exception as e:
        return {"status": "500", "message": str(e)}


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
def default_endpoint(path):
    return {"status": "200", "message": "Use /api/v1/health, /api/v1/history or /api/v1/live"}
