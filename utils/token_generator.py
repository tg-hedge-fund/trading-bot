from growwapi import GrowwAPI
from pathlib import Path

import pyotp

from utils.app_config import extract_groww_keys

def generate_token():
  api_key, secret = extract_groww_keys()
  totp = pyotp.TOTP(secret).now()

  access_token = GrowwAPI.get_access_token(api_key, totp)
  return api_key, secret, access_token


def get_access_token():
  secret_file = Path.home() / ".growwSecretKey"
  ACCESS_TOKEN=""
  with open(secret_file, "r") as f:
    lines = f.readlines()
    ACCESS_TOKEN = lines[2].strip()

  GROWW = GrowwAPI(ACCESS_TOKEN)

  return ACCESS_TOKEN, GROWW
