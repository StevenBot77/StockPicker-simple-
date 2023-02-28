import requests

api_key = '4CVWNO7MQFK2QE81'
symbol = 'MSFT'

url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"

response = requests.get(url)
data = response.json()

current_price = data['Global Quote']['05. price']

print (f"The current price of {symbol} is ${current_price}")