# FinSum - Financial Insights Dashboard

A modern, AI-powered financial insights dashboard with a clean, glassy Apple Vision OS style UI. This application provides real-time stock data, sentiment analysis, and news summarization using OpenAI's GPT models to deliver actionable financial insights.

![FinSum Dashboard](https://i.imgur.com/hPKlNbD.png)

## Features

- **Real-time Stock Monitoring**: Track multiple stocks simultaneously with automatic data refresh
- **Multi-source Financial Data**: 
  - Primary data from Yahoo Finance with Alpha Vantage as fallback
  - Option to include NewsAPI as an additional news source
- **Sentiment Analysis**: 
  - Default VADER sentiment analysis for financial news
  - Optional FinBERT integration for more finance-specific sentiment analysis
- **AI-powered Insights**:
  - GPT-based news summarization with automatic caching to reduce token usage
  - Interactive Q&A for financial articles you paste in
- **Risk Assessment**: Smart risk scoring based on news sentiment, price changes, and market indicators
- **Modern UI**: Clean, glassy interface inspired by Apple Vision OS with responsive design
- **Automatic Updates**: Background scheduler refreshes data every 30 minutes

## Technical Overview

### Project Structure

```
finsum/
├── app/                        # Main application package
│   ├── analysis/               # Analysis modules
│   │   ├── data_fetch.py       # Stock data and news retrieval
│   │   ├── sentiment.py        # Sentiment analysis logic
│   │   ├── finbert_inference.py# Optional FinBERT integration
│   │   └── llm.py              # OpenAI GPT integration
│   ├── static/                 # CSS and static assets
│   └── templates/              # Jinja2 HTML templates
├── config.py                   # Configuration and API keys
├── app.py                      # Main Flask application
├── requirements.txt            # Full dependencies
├── requirements.txt.essential  # Minimal dependencies
├── run.sh                      # Helper script to run the app
├── setup_env.sh                # Environment variables setup
└── Dockerfile                  # Docker configuration
```

## Getting Started

### Prerequisites

- Python 3.10+
- API keys for:
  - OpenAI (for GPT integration)
  - Alpha Vantage (for financial data)
  - NewsAPI (optional, for additional news sources)

### Installation

1. Clone the repository and navigate to the project directory:
```bash
git clone https://github.com/martindemel/finsum.git
cd finsum
```

2. Run the setup script to configure environment variables:
```bash
./setup_env.sh
```
This will create a `.env` file with your API keys.

3. Run the application using the included helper script:
```bash
./run.sh
```
This script will:
- Create a Python virtual environment
- Install dependencies
- Download necessary NLTK data
- Start the application

4. Access the application at: http://localhost:8080

### Manual Installation

If you prefer to set up manually:

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export OPENAI_API_KEY="your_openai_key"
export ALPHAVANTAGE_API_KEY="your_alpha_vantage_key"
export NEWSAPI_KEY="your_newsapi_key"  # optional
```

4. Run the application:
```bash
python app.py
```

### Using Docker

To run the application using Docker:

```bash
# Build the Docker image
docker build -t finsum .

# Run the container
docker run -p 8080:5000 \
  -e OPENAI_API_KEY="your_openai_key" \
  -e ALPHAVANTAGE_API_KEY="your_alpha_vantage_key" \
  finsum
```

## Advanced Features

### Using FinBERT for Enhanced Sentiment Analysis

FinBERT is a pre-trained NLP model specifically tuned for financial text. To enable it:

1. Ensure you've installed all dependencies including `transformers` and `torch`
2. Edit `config.py` and set `USE_FINBERT = True`
3. Restart the application

Note that FinBERT requires more system resources than the default VADER sentiment analyzer.

### Adding NewsAPI as a Data Source

To incorporate additional news sources:

1. Ensure you have a valid NewsAPI key configured
2. In `app.py`, locate calls to `data_fetch.analyze_stocks()`
3. Change the `use_newsapi` parameter from `False` to `True`

### Customizing Stocks

The default list of stocks can be modified in the `refresh_default_stocks()` function in `app.py`. The current defaults are:

```python
default_symbols = [
    "TSLA","NVDA","AAPL","GOOGL","AMZN","XRP","AVGO",
    "MSFT","META","NFLX","BABA","BAC"
]
```

## Troubleshooting

### No News or Data Appearing

If you see "No recent news available" for all stocks:
1. Verify your Alpha Vantage API key is correct
2. Check if you've exceeded your API rate limits (free tier has limitations)
3. Try clicking the "Refresh Data" button
4. Check the application logs in `app.log` for specific error messages

### Error with OpenAI Integration

If summarization or Q&A features aren't working:
1. Verify your OpenAI API key is correct
2. Check your OpenAI account has available credits
3. The application supports both older and newer versions of the OpenAI API

## License

MIT License

## Acknowledgments

- [Alpha Vantage](https://www.alphavantage.co/) for financial data API
- [Yahoo Finance](https://finance.yahoo.com/) for stock data
- [OpenAI](https://openai.com/) for GPT API
- [NLTK](https://www.nltk.org/) for VADER sentiment analysis
- [FinBERT](https://github.com/ProsusAI/finBERT) for financial NLP
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Bootstrap](https://getbootstrap.com/) for UI components 