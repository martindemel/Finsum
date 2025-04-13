#!/bin/bash

# Set to exit on error
set -e

# Color setup
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Loading environment variables from .env file...${NC}"
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check if virtual env exists, create if not
echo -e "${GREEN}Setting up Python virtual environment in venv...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${GREEN}Installing dependencies in virtual environment...${NC}"
pip install --upgrade pip
pip install -r requirements.txt.essential

# Download NLTK data
echo -e "${GREEN}Attempting to download NLTK data...${NC}"
if python -c "import nltk" &> /dev/null; then
    # Create nltk_data directory if it doesn't exist
    mkdir -p ~/nltk_data/tokenizers/punkt
    mkdir -p ~/nltk_data/corpora/stopwords
    mkdir -p ~/nltk_data/sentiment/vader_lexicon
    
    if python -c "import nltk.data; nltk.data.find('tokenizers/punkt')" &> /dev/null; then
        echo "NLTK punkt tokenizer already downloaded."
    else
        echo "Downloading NLTK punkt tokenizer..."
        if python -c "import nltk; nltk.download('punkt')" &> /dev/null; then
            echo "Downloaded punkt tokenizer successfully."
        else
            echo "NLTK is not installed, skipping data download."
        fi
    fi
    
    if python -c "import nltk.data; nltk.data.find('corpora/stopwords')" &> /dev/null; then
        echo "NLTK stopwords already downloaded."
    else
        echo "Downloading NLTK stopwords..."
        if python -c "import nltk; nltk.download('stopwords')" &> /dev/null; then
            echo "Downloaded stopwords successfully."
        else
            echo "Error downloading stopwords."
        fi
    fi
    
    if python -c "import nltk.data; nltk.data.find('sentiment/vader_lexicon')" &> /dev/null; then
        echo "NLTK vader lexicon already downloaded."
    else
        echo "Downloading NLTK vader lexicon..."
        if python -c "import nltk; nltk.download('vader_lexicon')" &> /dev/null; then
            echo "Downloaded vader lexicon successfully."
        else
            echo "Error downloading vader lexicon."
        fi
    fi
else
    echo "NLTK is not installed, skipping data download."
fi

# Check if FinBERT is enabled in config
if grep -q "USE_FINBERT = True" config.py; then
    echo -e "${YELLOW}FinBERT is enabled. Make sure transformers is installed for sentiment analysis.${NC}"
    if ! pip show transformers > /dev/null 2>&1; then
        echo -e "${YELLOW}Disabling FinBERT in config.py since dependencies are not installed.${NC}"
        sed -i '' 's/USE_FINBERT = True/USE_FINBERT = False/g' config.py
    fi
else
    echo -e "${YELLOW}Disabled FinBERT in config.py since dependencies are not installed.${NC}"
fi

# Start the application
echo -e "${GREEN}Starting FinSum application...${NC}"
python app.py 