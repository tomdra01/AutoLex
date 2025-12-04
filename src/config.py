import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

if not api_key:
    print("Error: MISTRAL_API_KEY not found.")
    exit(1)

llm_config = {
    "config_list": [
        {
            "model": "open-mistral-nemo",
            "api_key": api_key,
            "api_type": "mistral",
            "api_rate_limit": 0.25,
            "repeat_penalty": 1.1,
            "temperature": 0.5,
            "seed": 42,
        }
    ]
}