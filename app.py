try:
    from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
    import logging
    import sys
    import os
    import traceback
    import datetime
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    import config
    
    # Add the current directory to Python path to make imports work
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Import from the analysis directory directly
    from app.analysis import data_fetch, sentiment, llm
    from apscheduler.schedulers.background import BackgroundScheduler
    import atexit
    import time
    
    # Check if all required modules are available
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Error importing dependencies: {e}")
    print("Please ensure all required packages are installed.")
    print("Run: pip install -r requirements.txt")
    MODULES_AVAILABLE = False
    import sys
    sys.exit(1)

# Define the port - using 8080 instead of 5000 which is often used by AirPlay on macOS
PORT = 8086

app = Flask(__name__, 
            template_folder="app/templates",
            static_folder="app/static")
app.config.from_object(config)
app.secret_key = config.SECRET_KEY

# Add context processors and filters
@app.context_processor
def inject_now():
    """
    Add 'now' function to template context.
    This is a more robust approach than using a filter.
    """
    def now(format_string):
        return datetime.datetime.now().strftime(format_string)
    return {'now': now}

logging.basicConfig(
    level=logging.INFO,
    filename='app.log',
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Global cache for default stocks
cached_results = {}
last_refresh_time = None

# 1) SCHEDULER to refresh data every 30 minutes (or so).
scheduler = BackgroundScheduler()

def refresh_default_stocks():
    """
    Periodically refresh the default list so the page remains current.
    """
    global cached_results, last_refresh_time
    default_symbols = [
        "TSLA","NVDA","AAPL","GOOGL","AMZN","XRP",
        "MSFT","META","NFLX","BABA","BAC"
    ]
    try:
        print("Refreshing stock data...")
        
        data = data_fetch.analyze_stocks(default_symbols)
        for sym, info in data.items():
            # local sentiment
            scores = []
            for article in info["news"]:
                txt = f"{article['title']}. {article['summary'] or ''}"
                comp, lbl, _ = sentiment.analyze_sentiment(txt)
                article["local_sentiment"] = lbl
                article["local_compound"] = comp
                scores.append(comp)
            if scores:
                avg_c = sum(scores)/len(scores)
            else:
                avg_c = 0
            info["avg_sentiment"] = avg_c
            if avg_c > 0.05:
                info["sentiment_trend"] = "Bullish"
            elif avg_c < -0.05:
                info["sentiment_trend"] = "Bearish"
            else:
                info["sentiment_trend"] = "Neutral"
            # risk
            info["risk_level"] = sentiment.evaluate_risk(sym, info)
            
            # Debug output
            print(f"Symbol: {sym}, Price: {info['price']}, Change: {info['change_pct']}%, News: {len(info['news'])}")
            if len(info['news']) > 0:
                print(f"First news title: {info['news'][0]['title']}")
            
        cached_results = data
        last_refresh_time = time.time()
        logging.info("Default stock data refreshed.")
        print("Stock data refresh complete!")
        return True
    except Exception as e:
        logging.error(f"Error refreshing stock data: {e}")
        print(f"Error refreshing stock data: {e}")
        traceback.print_exc()
        return False

# Start APScheduler
scheduler.add_job(func=refresh_default_stocks, trigger="interval", minutes=30)
scheduler.start()

@atexit.register
def shutdown_scheduler():
    scheduler.shutdown()

# Force an initial refresh to make sure we have data on startup
print("Performing initial data refresh on startup...")
refresh_success = refresh_default_stocks()
if not refresh_success:
    print("Warning: Initial data refresh failed. The application will continue but data may be missing.")

# Add error handler
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {e}")
    traceback.print_exc()
    return safe_render_template('error.html', error=str(e)), 500

@app.route("/refresh")
def refresh_data():
    """
    Manual refresh endpoint
    """
    try:
        if refresh_default_stocks():
            return redirect(url_for('index'))
        else:
            return "Error refreshing data. Please check logs and try again."
    except Exception as e:
        logging.error(f"Exception in refresh route: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET","POST"])
def index():
    try:
        if request.method == "POST":
            selected_stocks = request.form.getlist("stocks")
            article_text = request.form.get("article","").strip()
            user_question = request.form.get("user_question","").strip()

            final = {"stocks": None, "article": None}

            # If user selected stocks, fetch fresh data
            if selected_stocks:
                try:
                    print(f"Analyzing selected stocks: {selected_stocks}")
                    raw_data = data_fetch.analyze_stocks(selected_stocks)
                    for sym, info in raw_data.items():
                        sc = []
                        for art in info["news"]:
                            text = f"{art['title']}. {art.get('summary','')}"
                            comp, lbl, _ = sentiment.analyze_sentiment(text)
                            art["local_sentiment"] = lbl
                            art["local_compound"] = comp
                            sc.append(comp)
                        if sc:
                            avg_comp = sum(sc)/len(sc)
                        else:
                            avg_comp = 0
                        info["avg_sentiment"] = avg_comp
                        if avg_comp > 0.05:
                            info["sentiment_trend"] = "Bullish"
                        elif avg_comp < -0.05:
                            info["sentiment_trend"] = "Bearish"
                        else:
                            info["sentiment_trend"] = "Neutral"
                        # risk
                        info["risk_level"] = sentiment.evaluate_risk(sym, info)
                    final["stocks"] = raw_data
                except Exception as e:
                    logging.error(f"Error analyzing stocks: {e}")
                    print(f"Error analyzing stocks: {e}")
                    traceback.print_exc()

            # If user pasted an article
            if article_text:
                try:
                    # Q&A
                    if user_question:
                        article_res = llm.analyze_text(article_text)
                        ans = llm.answer_question(article_text, user_question)
                        article_res["answer"] = ans
                        article_res["question"] = user_question
                        final["article"] = article_res
                    else:
                        # summary only
                        article_res = llm.analyze_text(article_text)
                        final["article"] = article_res
                except Exception as e:
                    logging.error(f"Error analyzing article: {e}")
                    print(f"Error analyzing article: {e}")
                    traceback.print_exc()

            return safe_render_template("index.html", results=final)

        # GET request => show default
        # Check if we need a refresh (cached_results empty or more than 30 minutes old)
        if not cached_results or (last_refresh_time and time.time() - last_refresh_time > 1800):
            print("Cache is empty or stale, refreshing data...")
            refresh_default_stocks()
        
        return safe_render_template("index.html", results={
            "stocks": cached_results,
            "article": None
        })
    except Exception as e:
        logging.error(f"Exception in index route: {e}")
        traceback.print_exc()
        # Return a simplified response to avoid template errors
        return f"""
        <html>
            <body style="font-family: sans-serif; padding: 20px;">
                <h1>Error</h1>
                <p>An error occurred while rendering the page: {str(e)}</p>
                <p><a href="/">Reload</a></p>
            </body>
        </html>
        """

# Add root favicon.ico route to prevent 404 errors
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

# Add static file routes
@app.route('/static/<path:filename>')
def static_files(filename):
    return app.send_static_file(filename)

# OPTIONAL: Example route for Robinhood
@app.route("/robinhood-portfolio")
def robinhood_portfolio():
    # Placeholder - see the note below for official/unofficial API usage
    return "Robinhood Integration Not Implemented"

def safe_render_template(template_name_or_list, **context):
    """
    A safer version of render_template that handles errors during template rendering
    and falls back to a simple HTML response.
    """
    try:
        return render_template(template_name_or_list, **context)
    except Exception as e:
        app.logger.error(f"Error rendering template {template_name_or_list}: {e}")
        error_message = str(e)
        traceback.print_exc()
        return f"""
        <html>
            <body style="font-family: sans-serif; padding: 20px;">
                <h1>Error</h1>
                <p>An error occurred while rendering the page: {error_message}</p>
                <p><a href="javascript:location.reload()">Reload</a> | <a href="/">Home</a></p>
                <hr>
                <p><small>© {datetime.datetime.now().strftime('%Y')} FinSum</small></p>
            </body>
        </html>
        """

if __name__ == "__main__":
    print(f"Starting FinSum on port {PORT}...")
    print(f"Access the application at http://localhost:{PORT}")
    app.run(debug=config.DEBUG, host="0.0.0.0", port=PORT) 