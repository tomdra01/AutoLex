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
            "temperature": 0.0,
            "seed": 42,
        }
    ]
}

BASE_STATIC_PDF_URL = "https://static.slov-lex.sk/pdf/SK/ZZ"
BASE_XML_URL = "https://static.slov-lex.sk/static/xml/SK/ZZ"
NAMESPACES = {'ml': 'http://www.metalex.eu/metalex/1.0'}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.100 Safari/537.36"
}