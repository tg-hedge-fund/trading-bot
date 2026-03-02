import logging
from threading import Thread

from utils.config_reader import ConfigReader

config = ConfigReader()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_in_thread(fn, *args, daemon=False):
    t = Thread(target=fn, args=args, daemon=daemon)
    t.start()
    return t
