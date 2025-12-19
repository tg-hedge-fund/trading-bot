import psycopg2
from utils.config_reader import ConfigReader
from utils.app_config import decrypt
class PGConnector:
    def __init__(self):
        self.config = ConfigReader()
        self.conn = None

    def get_db_conn_cursor(self):
        try:
            self.conn = psycopg2.connect(
                dbname=self.config.get("db.name"),
                user=self.config.get("db.username"),
                password=self.config.get("db.password"),
                host=self.config.get("db.host"),
                port=self.config.get("db.port")
            )
        except Exception as e:
            print(f"Database connection failed: {str(e)}")
        finally:
            if self.conn:
                return self.conn, self.conn.cursor()
            else:
                return None, None

    def close_db_conn(self):
        if self.conn:
            self.conn.close()

