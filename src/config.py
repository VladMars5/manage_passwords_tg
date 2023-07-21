import os
import string

from dotenv import load_dotenv

load_dotenv()

TOKEN_BOT = os.environ.get("TOKEN_BOT")

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

LIVE_POOL_DB_CONNECTIONS = int(os.environ.get("LIVE_POOL_DB_CONNECTIONS"))
COUNT_MAX_CONNECTIONS_DB = int(os.environ.get("COUNT_MAX_CONNECTIONS_DB"))
COUNT_OVERFLOW_POOL = int(os.environ.get("COUNT_OVERFLOW_POOL"))

ENCRYPTION_KEY_LOGIN: bytes = os.environ.get('ENCRYPTION_KEY_LOGIN').encode('utf-8')
ENCRYPTION_KEY_PASSWORD: bytes = os.environ.get('ENCRYPTION_KEY_PASSWORD').encode('utf-8')

alphabet_password = string.ascii_letters + string.digits + string.punctuation
