import psycopg2

from utils.discord_bot import (
    send_message_via_discord_bot,
)
from utils.utils import config, logger


class PGConnector:
    def __init__(self):
        self.conn = None

    def get_db_conn_cursor(self):
        try:
            self.conn = psycopg2.connect(
                dbname=config.get("db.name"),
                user=config.get("db.username"),
                password=config.get("db.password"),
                host=config.get("db.host"),
                port=config.get("db.port")
            )
            return self.conn, self.conn.cursor()
        except Exception as e:
            send_message_via_discord_bot(f"Database connection failed: {str(e)}")
            logger.error(f"Database connection failed: {str(e)}")
            return None, None

    def close_db_conn(self):
        if self.conn:
            self.conn.close()
