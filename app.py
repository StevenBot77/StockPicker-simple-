import os
from flask import Flask, render_template, request
import requests
import json
from werkzeug.exceptions import HTTPException
from requests.exceptions import Timeout, ConnectionError
from flask_caching import Cache
import logging
import redis

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': os.environ.get('REDIS_URL')})
logging.basicConfig(level=logging.INFO)

ALPHAVANTAGE_ENDPOINT = "https://www.alphavantage.co/query"
ALPHAVANTAGE_API_KEY = os.environ.get('ALPHAVANTAGE_API_KEY')

redis_client = redis.Redis.from_url(os.environ.get('REDIS_URL'))

@app.route('/')
def home():
    return render_template('home.html')

@cache.memoize(timeout=300)
def get_stock_data(symbol):
    try:
        url = f"{ALPHAVANTAGE_ENDPOINT}?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()

        if "Global Quote" in data:
            return data['Global Quote']
        else:
            raise HTTPException(f"Sorry, we couldn't find the stock symbol {symbol}.")
    except Timeout as e:
        logging.error(f"Request timed out: {e}")
        raise HTTPException(f"Request timed out: {e}")
    except ConnectionError as e:
        logging.error(f"Connection error: {e}")
        raise HTTPException(f"Connection error: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        raise HTTPException(f"JSON decode error: {e}")
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(f"An error occurred: {e}")

@app.route('/get_stock_info', methods=['POST'])
def get_stock_info():
    symbol = request.form['symbol']

    try:
        stock_data = get_stock_data(symbol)
        current_price = stock_data['05. price']
        open_price = stock_data['02. open']
        high_price = stock_data['03. high']
        low_price = stock_data['04. low']
        volume = stock_data['06. volume']
        return render_template('stock_info.html', symbol=symbol, current_price=current_price, open_price=open_price,
                               high_price=high_price, low_price=low_price, volume=volume)
    except HTTPException as e:
        logging.error(f"Error: {e}")
        return f"Error: {e}"

@cache.memoize(timeout=300)
def get_historical_data(symbol):
    try:
        url = f"{ALPHAVANTAGE_ENDPOINT}?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()

        if "Time Series (Daily)" in data:
            return data['Time Series (Daily)']
        else:
            raise HTTPException(f"Sorry, we couldn't find the historical stock data for symbol {symbol}.")
    except Timeout as e:
        logging.error(f"Request timed out: {e}")
        raise HTTPException(f"Request timed out: {e}")
    except ConnectionError as e:
        logging.error(f"Connection error: {e}")
        raise HTTPException(f"Connection error: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error  {e}")
        raise HTTPException(f"JSON decode error: {e}")
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(f"An error occurred: {e}")

@app.route('/get_historical_data', methods=['POST'])
def get_historical_data_info():
    symbol = request.form['historical_symbol']

    try:
        historical_data = get_historical_data(symbol)
        return render_template('historical_data.html', symbol=symbol, historical_data=historical_data)
    except HTTPException as e:
        logging.error(f"Error: {e}")
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(debug=True)