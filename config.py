import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "kisan_saathi_default_secret_key_123!")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
