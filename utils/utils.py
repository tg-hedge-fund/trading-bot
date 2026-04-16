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

def run_thread(fn, name, daemon=False, *args):
    t = Thread(target=fn, name=name, daemon=daemon, *args)
    t.start()
    return t
