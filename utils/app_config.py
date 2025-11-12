from pathlib import Path

def extract_groww_keys():
  secret_file = Path.home() / ".growwSecretKey"

  API_KEY = ""
  SECRET = ""

  with open(secret_file, "r") as f:
    lines = f.readlines()
    API_KEY = lines[0].strip()
    SECRET = lines[1].strip()

  return API_KEY, SECRET

def write_keys(api_key, secret, access_token):
  secret_file = Path.home() / ".growwSecretKey"
  with open(secret_file, "w") as f:
    f.write(f"{api_key}\n{secret}\n{access_token}")
