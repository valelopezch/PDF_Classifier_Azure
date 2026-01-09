import os

subscription_key = os.getenv("subscription_key")
endpoint = os.getenv("endpoint")
api_version = os.getenv("api_version")

if not subscription_key or not endpoint:
    raise RuntimeError(
        "Azure OpenAI credentials not found. "
    )
