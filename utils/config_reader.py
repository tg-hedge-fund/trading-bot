import yaml
from pathlib import Path
import os
from utils.app_config import decrypt

class ConfigReader:
    def __init__(self):
        with open(f"config/{os.getenv('HF_ENV', 'dev')}.yaml", 'r') as file:
            self.config = yaml.safe_load(file)

    def get(self, key, default=None):
        """Get value from config by key, supporting dot notation for nested keys.
        
        Examples:
            config.get("username")  # Returns top-level username
            config.get("db.username")  # Returns nested username under db
            config.get("db.password")  # Returns and decrypts encrypted password
        """
        # Handle dot notation for nested keys
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