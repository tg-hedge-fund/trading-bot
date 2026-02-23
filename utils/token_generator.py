from pathlib import Path

import pyotp
from growwapi import GrowwAPI, GrowwFeed

from utils.app_config import extract_groww_keys, write_keys
from utils.discord_bot import send_message_via_discord_bot
from utils.utils import logger


def generate_token():
  api_key, secret = extract_groww_keys()
  totp = pyotp.TOTP(secret).now()
  access_token = ""
  try:
      access_token = GrowwAPI.get_access_token(api_key, totp)
  except Exception:
      send_message_via_discord_bot("Error generating access token from Groww, trying again!")
      RuntimeError("Error generating access token from Groww, trying again!")
      try:
          access_token = GrowwAPI.get_access_token(api_key, totp)
      except Exception:
          send_message_via_discord_bot("Error generating access token from Groww")
          RuntimeError("Error generating access token from Groww")
  write_keys(api_key, secret, access_token)
  logger.info("Groww Access Token generated...")
  return api_key, secret, access_token


def get_access_token():
  secret_file = Path.home() / ".growwSecretKey"
  ACCESS_TOKEN=""
  with open(secret_file, "r") as f:
    lines = f.readlines()
    ACCESS_TOKEN = lines[2].strip()

  GROWW = GrowwAPI(ACCESS_TOKEN)
  # FEED = GrowwFeed(ACCESS_TOKEN)
  FEED = None

  return ACCESS_TOKEN, GROWW, FEED
