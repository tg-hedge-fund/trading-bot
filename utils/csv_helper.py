import pandas as pd

all_equities = pd.read_csv("../instrument-eq.csv")
instrument_exchange_token = all_equities["exchange_token"].tolist()
eq_symbols = all_equities["groww_symbol"].tolist()