from enum import Enum

INDICES_LIST = [
  "NIFTY",
  # "SENSEX",
  "NIFTY100",
  "NIFTYMIDCAP",
  "BANKNIFTY",
  "NIFTYMETAL",
  "NIFTYPHARMA",
  "NIFTYAUTO",
  "NIFTYFMCG",
  "NIFTYPSUBANK",
  "NIFTYPVTBANK",
  "FINNIFTY",
  "NIFTYREALTY",
  "NIFTYMEDIA"
]

EQUITY = [

]


class MESSAGE_TYPES(Enum):
  PORTFOLIO = "portfolio"
  INDICES = "indices"
  EQUITY = "equity"
  LOGS = "logs"
  HEARTBEAT = "heartbeat"
