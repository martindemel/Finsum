import os

# OpenAI for GPT calls
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Optional Robinhood credentials
RH_USERNAME = os.environ.get("RH_USERNAME", "")
RH_PASSWORD = os.environ.get("RH_PASSWORD", "")

# Enable debug mode?
DEBUG = False

# Secret key for Flask sessions
SECRET_KEY = os.environ.get("SECRET_KEY", "some-secret-key")

# For advanced features
USE_FINBERT = False  # set True if you want to try local FinBERT 