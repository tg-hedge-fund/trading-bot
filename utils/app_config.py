import yaml
from pathlib import Path
import logging
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os

logger = logging.getLogger(__name__)

class AppConfig:
    """Handles encryption and decryption using PBE with AES."""
    
    SECRET_KEY_PATH = os.path.expanduser("~/.secretKey")
    SEPARATOR = ":"
    ENCRYPTED_TEXT_PREFIX = "ENC("
    ENCRYPTED_TEXT_SUFFIX = ")"
    
    def __init__(self):
        self.password = None
        self.salt = None
        self.cipher_algorithm = None
        self.encryption_algorithm = None
        self.number_generation_algorithm = None
        self.iterations = None
        self.enc_bits = None
        self.pbe_cipher = None
        self.secret_key = None
        
        self._read_secret_key_file()
    
    def _read_secret_key_file(self):
        """Read secret key configuration from file."""
        try:
            with open(self.SECRET_KEY_PATH, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                self.password = lines[0].strip()
                self.salt = lines[1].strip()
                self.cipher_algorithm = lines[2].strip()
                self.encryption_algorithm = lines[3].strip()
                self.number_generation_algorithm = lines[4].strip()
                self.iterations = int(lines[5].strip())
                self.enc_bits = int(lines[6].strip())
        except FileNotFoundError:
            logger.error(f"Secret Key File Not Found at path {self.SECRET_KEY_PATH}")
        except IOError as e:
            logger.error(f"IOException when reading the secret key file: {str(e)}")
        
        self.secret_key = self._create_secret_key()
    
    def encrypt(self, plain_text):
        """Encrypt plain text using PBE with AES."""
        try:
            # Generate random IV
            iv = os.urandom(16)
            
            # Derive key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.salt.encode('utf-8'),
                iterations=self.iterations,
                backend=default_backend()
            )
            key = kdf.derive(self.password.encode('utf-8'))
            
            # Encrypt
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Apply PKCS7 padding
            plaintext_bytes = plain_text.encode('utf-8')
            block_size = 16
            padding_length = block_size - (len(plaintext_bytes) % block_size)
            padded_plaintext = plaintext_bytes + bytes([padding_length] * padding_length)
            
            ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
            
            return self._encode(iv) + self.SEPARATOR + self._encode(ciphertext)
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            return None
    
    def decrypt(self, encrypted_message):
        """Decrypt encrypted message."""
        try:
            # Guard against null/empty input
            if not encrypted_message:
                return ""
            
            # Remove ENC(...) if present
            if encrypted_message.startswith(self.ENCRYPTED_TEXT_PREFIX) and \
               encrypted_message.endswith(self.ENCRYPTED_TEXT_SUFFIX):
                encrypted_message = encrypted_message[
                    len(self.ENCRYPTED_TEXT_PREFIX):-len(self.ENCRYPTED_TEXT_SUFFIX)
                ]
            
            # Split IV and ciphertext
            parts = encrypted_message.split(self.SEPARATOR)
            iv = self._decode(parts[0])
            ciphertext = self._decode(parts[1])
            
            # Derive key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.salt.encode('utf-8'),
                iterations=self.iterations,
                backend=default_backend()
            )
            key = kdf.derive(self.password.encode('utf-8'))
            
            # Decrypt
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Remove PKCS7 padding
            padding_length = padded_plaintext[-1]
            plaintext = padded_plaintext[:-padding_length]
            
            return plaintext.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            return None
    
    def _create_secret_key(self):
        """Create secret key from password and salt."""
        try:
            # Derive key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=self.enc_bits // 8,
                salt=self.salt.encode('utf-8'),
                iterations=self.iterations,
                backend=default_backend()
            )
            secret_key = kdf.derive(self.password.encode('utf-8'))
            return secret_key
        except Exception as e:
            raise RuntimeError(f"Failed to create secret key: {str(e)}")
    
    @staticmethod
    def _encode(data):
        """Encode bytes to base64 string."""
        return base64.b64encode(data).decode('utf-8')
    
    @staticmethod
    def _decode(data):
        """Decode base64 string to bytes."""
        return base64.b64decode(data)


# Module-level instance for convenience
_app_config = None

def _get_app_config():
    """Get or create the AppConfig instance."""
    global _app_config
    if _app_config is None:
        _app_config = AppConfig()
    return _app_config

def encrypt(plain_text):
    """Encrypt plain text using the default AppConfig instance."""
    return _get_app_config().encrypt(plain_text)

def decrypt(encrypted_message):
    """Decrypt encrypted message using the default AppConfig instance."""
    return _get_app_config().decrypt(encrypted_message)

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


