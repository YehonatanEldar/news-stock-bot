import yfinance as yf
import requests
import datetime
import json
import os

def load_api_key() -> str:
    try:
        with open('api_keys.json') as f:
            data = json.load(f)
            return data['news_api_key']
    except KeyError:
        raise KeyError("The key 'news_api_key' was not found in the 'api_key.json' file.")
    except FileNotFoundError:
        raise FileNotFoundError("The 'api_key.json' file was not found.")

def get_news(company: str, date: str) -> dict:
    stock = yf.Ticker(company)
    formatted_date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')
    file_path = f'news/{company}_News_{formatted_date}.json'
    
    # Check if the JSON file for the current company and date exists
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            news = json.load(f)
        return news
    
    BASE_URL = 'https://newsapi.org/v2/everything?q=COMPANY&from=DATE&sortBy=popularity&apiKey=API_KEY'
    url = BASE_URL.replace('COMPANY', stock.info['longName'].split()[0])
    url = url.replace('DATE', formatted_date)
    url = url.replace('API_KEY', load_api_key())
    print(url)
    response = requests.get(url)
    news = response.json()

    # Write the news to the JSON file
    with open(file_path, 'w') as f:
        json.dump(news, f, indent=4)
    
    return news