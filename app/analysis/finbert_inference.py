import sys
import os

# Ensure the parent directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import config

if config.USE_FINBERT:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch

    MODEL_NAME = "ProsusAI/finbert"

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()

def finbert_sentiment(text):
    """
    If config.USE_FINBERT is True, run local FinBERT inference 
    for more accurate finance sentiment.
    Returns label: Positive/Negative/Neutral and score.
    """
    if not config.USE_FINBERT:
        # fallback or raise
        return None, None
    
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    probs = torch.softmax(logits, dim=1).tolist()[0]
    # FinBERT labels: 0=negative, 1=neutral, 2=positive (for the ProsusAI/finbert)
    label_idx = probs.index(max(probs))
    if label_idx == 0:
        label = "Negative"
    elif label_idx == 1:
        label = "Neutral"
    else:
        label = "Positive"
    return label, max(probs) 