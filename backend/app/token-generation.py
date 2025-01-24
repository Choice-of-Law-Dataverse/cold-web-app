import jwt

SECRET = "youcannotpassbalrog"  # Must match your real secret
payload = {"sub": "some-fixed-user", "role": "admin"}  # Example payload
token = jwt.encode(payload, SECRET, algorithm="HS256")

print(token)
