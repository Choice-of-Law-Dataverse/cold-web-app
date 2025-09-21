import logging
import os

import jwt
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

SECRET: str = os.getenv("JWT_SECRET", "MYSECRET")

payload = {"sub": "some-fixed-user", "role": "admin"}  # Example payload
token = jwt.encode(payload, SECRET, algorithm="HS256")

logger.debug("Generated token: %s", token.strip())
