import os

def get_access_token(target):
    return f"Bearer {os.getenv("ACCESS_TOKEN")/target}" if os.getenv(target) else ""