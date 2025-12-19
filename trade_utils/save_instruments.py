import psycopg2
import pandas as pd
from utils.config_reader import ConfigReader
from utils.db_connector import PGConnector

config = ConfigReader()
db = PGConnector()
conn, cursor = db.get_db_conn_cursor()

instrument_eq = pd.read_csv("../instrument/instrument_eq.csv")

for i, instrument in instrument_eq.iterrows():
    #save the instrument along with their market_cap (get via api call)
    pass

