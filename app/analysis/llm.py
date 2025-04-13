import hashlib
import sys
import os

# Ensure the parent directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import config

# Handle both older and newer versions of OpenAI API
try:
    import openai
    # Check if this is the new version with Client
    if hasattr(openai, 'OpenAI'):
        # New version
        client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        openai_new_version = True
    else:
        # Old version
        openai.api_key = config.OPENAI_API_KEY
        openai_new_version = False
except ImportError:
    print("Failed to import openai. Please install with: pip install openai")
    openai_new_version = False

MODEL = "gpt-3.5-turbo"

# A simple in-memory cache to store GPT summaries so we don't re-call for the same article
summary_cache = {}

def _hash_text(title, content):
    """
    Create a short hash key from (title, content).
    """
    text = f"{title}_{content}"
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def summarize_article(title, content):
    """
    Summarize with GPT. We'll do a cache check first.
    """
    if not content.strip():
        return "(No content to summarize.)"

    cache_key = _hash_text(title, content)
    if cache_key in summary_cache:
        return summary_cache[cache_key]

    prompt = f"""You are an expert financial analyst. 
Read the following news article about a company and provide a concise summary in bullet points. 
Focus on key facts, any stock impact, sentiment, and risks mentioned.

Title: {title}
Article: {content}

Summary (bullet points):"""

    messages = [
        {"role": "system", "content": "You are a helpful financial analysis assistant."},
        {"role": "user", "content": prompt}
    ]
    try:
        if openai_new_version:
            # New OpenAI API
            resp = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.2
            )
            out = resp.choices[0].message.content.strip()
        else:
            # Old OpenAI API
            resp = openai.ChatCompletion.create(
                model=MODEL,
                messages=messages,
                temperature=0.2
            )
            out = resp["choices"][0]["message"]["content"].strip()
        
        summary_cache[cache_key] = out  # store in cache
        return out
    except Exception as e:
        return f"*(Error summarizing: {e})*"

def answer_question(article_text, question):
    """
    Q&A with GPT. No caching here since Q's can vary widely.
    """
    system_msg = (
        "You are a financial analyst assistant. You have been provided with an article's content. "
        "Answer the user's question based ONLY on the information in the article. "
        "If the answer is not in the article, say you do not know. "
        "Think step-by-step and provide a clear, concise answer."
    )
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "assistant", "content": f"Article:\n{article_text}"},
        {"role": "user", "content": question}
    ]
    try:
        if openai_new_version:
            # New OpenAI API
            resp = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0
            )
            ans = resp.choices[0].message.content.strip()
        else:
            # Old OpenAI API
            resp = openai.ChatCompletion.create(
                model=MODEL,
                messages=messages,
                temperature=0
            )
            ans = resp["choices"][0]["message"]["content"].strip()
        
        return ans
    except Exception as e:
        return f"*(Error in Q&A: {e})*"

def analyze_text(article_text):
    """
    For a pasted article, we generate a summary immediately.
    """
    summ = summarize_article("User provided text", article_text)
    return {"summary": summ} 