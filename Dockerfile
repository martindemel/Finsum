FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential wget curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Download NLTK data (vader lexicon)
RUN python -c "import nltk; nltk.download('vader_lexicon')"

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"] 