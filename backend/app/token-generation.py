import os

import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET: str = os.getenv("JWT_SECRET", "MYSECRET")

payload = {"sub": "some-fixed-user", "role": "admin"}  # Example payload
token = jwt.encode(payload, SECRET, algorithm="HS256")

print(token)
