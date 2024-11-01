# user_service_auth - app/settings.py

from starlette.config import Config
from starlette.datastructures import Secret
from datetime import timedelta

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()  

# Database configuration
DATABASE_URL = config("DATABASE_URL", cast=Secret)

# JWT settings
ALGORITHM = config.get("ALGORITHM")
SECRET_KEY = config.get("SECRET_KEY")

ACCESS_TOKEN_EXPIRE_MINUTES= timedelta(days=int(config.get("ACCESS_TOKEN_EXPIRE_MINUTES")))
REFRESH_TOKEN_EXPIRE_MINUTES = config("REFRESH_TOKEN_EXPIRE_MINUTES", cast=int, default=1440)



