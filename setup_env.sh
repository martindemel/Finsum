#!/bin/bash

echo "FinSum Environment Setup"
echo "========================"
echo "This script will help you set up the required environment variables for FinSum."
echo ""

# Create .env file
echo "# FinSum Environment Variables" > .env

# Prompt for OpenAI API key
echo -n "Enter your OpenAI API key: "
read openai_key
echo "OPENAI_API_KEY=\"$openai_key\"" >> .env

# Prompt for Alpha Vantage API key
echo -n "Enter your Alpha Vantage API key: "
read alphavantage_key
echo "ALPHAVANTAGE_API_KEY=\"$alphavantage_key\"" >> .env

# Prompt for NewsAPI key (optional)
echo -n "Would you like to configure NewsAPI for additional news sources? (y/n): "
read use_newsapi
if [[ "$use_newsapi" == "y" || "$use_newsapi" == "Y" ]]; then
  echo -n "Enter your NewsAPI key: "
  read newsapi_key
  echo "NEWSAPI_KEY=\"$newsapi_key\"" >> .env
fi

# Set Flask secret key (generate random or use static key if Python is not available)
if command -v python3 &> /dev/null; then
  flask_secret=$(python3 -c 'import secrets; print(secrets.token_hex(16))')
else
  # Fallback if Python is not available
  flask_secret="abcdef0123456789abcdef0123456789"
  echo "Warning: Python3 not found, using default secret key."
fi

echo "SECRET_KEY=\"$flask_secret\"" >> .env

echo ""
echo "Environment variables have been saved to .env file."
echo ""
echo "To load these variables, run:"
echo "  source .env"
echo ""
echo "Setup complete! You can now run FinSum with:"
echo "  ./run.sh" 