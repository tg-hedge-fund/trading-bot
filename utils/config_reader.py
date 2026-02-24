import yaml
import os
from utils.app_config import decrypt

class ConfigReader:
    def __init__(self):
        with open(f"config/{os.getenv('TGHF_ENV', 'dev')}.yaml", 'r') as file:
            self.config = yaml.safe_load(file)

    def get(self, key, default=None):
        if "." in key:
            keys = key.split(".")
            value = self.config
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    return default
                if value is None:
                    return default
        else:
            value = self.config.get(key, default)
        
        # Decrypt encrypted values
        if isinstance(value, str) and value.startswith("ENC(") and value.endswith(")"):
            decrypted = decrypt(value)
            return decrypted if decrypted else value
        
        return value