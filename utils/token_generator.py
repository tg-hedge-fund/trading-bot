import hashlib
import secrets
import time
from urllib.parse import parse_qs, urlparse

import requests
from fyers_apiv3 import fyersModel

from utils.app_config import read_fyers_credentials, write_fyers_credentials
from utils.constants import MESSAGE_TYPES
from utils.discord_bot import send_message_via_discord_bot

# https://myapi.fyers.in/docsv3#tag/Authentication-and-Login-Flow-User-Apps
FYERS_REFRESH_TOKEN_URL = "https://api-t1.fyers.in/api/v3/validate-refresh-token"


def _app_id_hash(client_id, secret_key):
    return hashlib.sha256(f"{client_id}:{secret_key}".encode()).hexdigest()


def login_with_auth_code():
    """
    Interactive login (run via generate_token.py). Needed once, and again whenever
    the refresh token expires (every 15 days).
    """
    creds = read_fyers_credentials()
    state = secrets.token_urlsafe(16)
    session = fyersModel.SessionModel(
        client_id=creds["client_id"],
        secret_key=creds["secret_key"],
        redirect_uri=creds["redirect_uri"],
        response_type="code",
        grant_type="authorization_code",
        state=state,
    )
    print("Open this URL, log in, and paste the URL you are redirected to (or just the auth_code):")
    print(session.generate_authcode())
    redirected = input("> ").strip()
    params = parse_qs(urlparse(redirected).query)
    auth_code = params.get("auth_code", [redirected])[0]
    # Fyers echoes state back on the redirect; reject it if it doesn't match what we sent
    if "state" in params and params["state"][0] != state:
        raise RuntimeError("State mismatch in Fyers redirect, aborting login")

    session.set_token(auth_code)
    response = session.generate_token()
    if response.get("s") != "ok" or "access_token" not in response:
        raise RuntimeError(f"Error generating access token from Fyers: {response}")

    creds["access_token"] = response["access_token"]
    creds["refresh_token"] = response["refresh_token"]
    write_fyers_credentials(creds)
    print("Fyers access and refresh tokens saved.")


def _refresh_access_token(creds):
    response = requests.post(
        FYERS_REFRESH_TOKEN_URL,
        json={
            "grant_type": "refresh_token",
            "appIdHash": _app_id_hash(creds["client_id"], creds["secret_key"]),
            "refresh_token": creds["refresh_token"],
            "pin": creds["pin"],
        },
        timeout=10,
    )
    body = response.json()
    if body.get("s") != "ok" or "access_token" not in body:
        raise RuntimeError(body)
    return body["access_token"]


def generate_token():
    """Daily headless refresh of the access token using the stored refresh token + PIN."""
    creds = read_fyers_credentials()
    access_token = ""
    try:
        access_token = _refresh_access_token(creds)
    except Exception:
        send_message_via_discord_bot("Error refreshing access token from Fyers, trying again!", MESSAGE_TYPES.LOGS)
        try:
            time.sleep(1)
            access_token = _refresh_access_token(creds)
        except Exception as e:
            send_message_via_discord_bot(
                f"Error refreshing access token from Fyers: {e}. "
                "Refresh token may have expired, run generate_token.py to log in again.",
                MESSAGE_TYPES.LOGS,
            )
    if access_token != "":
        creds["access_token"] = access_token
        write_fyers_credentials(creds)
        send_message_via_discord_bot("Fyers Access Token generated...", MESSAGE_TYPES.LOGS)


def get_fyers_client():
    creds = read_fyers_credentials()
    access_token = creds.get("access_token", "")
    fyers = fyersModel.FyersModel(client_id=creds["client_id"], token=access_token, is_async=False)
    return access_token, fyers
