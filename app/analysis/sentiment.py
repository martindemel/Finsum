import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import sys
import os

# Ensure the parent directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import config

try:
    _ = SentimentIntensityAnalyzer()
except:
    nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()

# If we have finbert
if config.USE_FINBERT:
    from .finbert_inference import finbert_sentiment

def clean_text(txt):
    return re.sub(r"\s+", " ", txt).strip()

def analyze_sentiment(text):
    """
    If config.USE_FINBERT => use finbert_inference, else use VADER.
    Returns (compound, label, raw_dict or confidence).
    """
    ctext = clean_text(text)

    if config.USE_FINBERT:
        label, prob = finbert_sentiment(ctext)
        # We'll simulate compound from prob for consistency
        if label == "Positive":
            compound = prob  # e.g. 0.8 => strong positivity
        elif label == "Negative":
            compound = -prob
        else:
            compound = 0.0
        return compound, label, {"confidence": prob}
    else:
        scores = sia.polarity_scores(ctext)
        compound = scores["compound"]
        if compound >= 0.05:
            label = "Positive"
        elif compound <= -0.05:
            label = "Negative"
        else:
            label = "Neutral"
        return compound, label, scores

def evaluate_risk(symbol, stock_info):
    """
    Enhanced heuristic risk:
    - negative articles
    - large price drop
    - average sentiment
    - optional: high volume or implied volatility (not shown here)
    """
    risk_points = 0

    # negative articles
    neg_count = 0
    for art in stock_info["news"]:
        if art.get("local_sentiment") == "Negative":
            neg_count += 1
    risk_points += neg_count * 20

    # Price drop more than 2%
    chg = stock_info.get("change_pct", 0)
    if chg < -2:
        risk_points += 40

    # average sentiment below -0.2 => add 30
    avg_s = stock_info.get("avg_sentiment", 0)
    if avg_s < -0.2:
        risk_points += 30

    # Example extension: if volume or volatility is high, risk_points += 20

    if risk_points >= 70:
        return "High"
    elif risk_points >= 30:
        return "Medium"
    else:
        return "Low" 