import base64

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError
from fastapi import HTTPException, status

from utils.db_connector import PGConnector
from utils.utils import config, logger


class AuthenticationError(HTTPException):
    def __init__(self, detail = "Invalid credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Basic"},
        )


class BasicAuthHandler:
    def __init__(self):
        self.time_cost = config.get("auth.argon2.time_cost", 2)
        self.memory_cost = config.get("auth.argon2.memory_cost", 65536)
        self.parallelism = config.get("auth.argon2.parallelism", 4)
        self.hash_len = config.get("auth.argon2.hash_len", 16)
        self.salt_len = config.get("auth.argon2.salt_len", 16)

        self.hasher = PasswordHasher(
            time_cost=int(str(self.time_cost)),
            memory_cost=int(str(self.memory_cost)),
            parallelism=int(str(self.parallelism)),
            hash_len=int(str(self.hash_len)),
            salt_len=int(str(self.salt_len)),
        )
        self.db = PGConnector()

        logger.info(
            f"BasicAuthHandler initialized with Argon2 parameters: "
            f"time_cost={self.time_cost}, memory_cost={self.memory_cost}, "
            f"parallelism={self.parallelism}, hash_len={self.hash_len}, salt_len={self.salt_len}"
        )

    def verify_credentials(self, auth_header) -> dict:
        if not auth_header:
            raise AuthenticationError("Missing authorization header")

        try:
            # Extract the base64 encoded credentials
            if not auth_header.startswith("Basic "):
                raise AuthenticationError("Invalid authorization header format")

            encoded_credentials = auth_header[6:]  # Remove "Basic " prefix
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
            username, password = decoded_credentials.split(":", 1)

        except (ValueError, UnicodeDecodeError) as e:
            logger.error(f"Failed to decode authorization header: {str(e)}")
            raise AuthenticationError("Invalid authorization header format")

        # Query the database for the user
        try:
            conn, cursor = self.db.get_db_conn_cursor()
            if conn is None or cursor is None:
                logger.error("Failed to establish database connection")
                raise AuthenticationError("Authentication service unavailable")

            cursor.execute(
                'SELECT id, username, password_hash FROM users WHERE username = %s',
                (username,)
            )
            user = cursor.fetchone()
            self.db.close_db_conn()

            if not user:
                logger.warning(f"Authentication failed: user '{username}' not found")
                raise AuthenticationError("Invalid username or password")

            user_id, username, password_hash = user

            # Verify the password using argon2
            try:
                self.hasher.verify(password_hash, password)
            except VerifyMismatchError:
                logger.warning(f"Authentication failed: invalid password for user '{username}'")
                raise AuthenticationError("Invalid username or password")
            except InvalidHash:
                logger.error(f"Invalid password hash format for user '{username}'")
                raise AuthenticationError("Authentication service error")

            logger.info(f"Authentication successful for user '{username}'")
            return {
                "id": user_id,
                "username": username,
            }

        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
            raise AuthenticationError("Authentication service error")


def get_current_user(auth_header = None) -> dict:
    if not auth_header:
        raise AuthenticationError("Missing authorization header")

    auth_handler = BasicAuthHandler()
    return auth_handler.verify_credentials(auth_header)
