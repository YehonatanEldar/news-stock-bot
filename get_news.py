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
    formatted_date = date.strftime('%Y-%m-%d')
    file_path = f'news/{company}_News.json'

    # Load existing news data if the file exists
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            all_news = json.load(f)
    else:
        all_news = {}

    # If news for the given date already exists, return it
    if formatted_date in all_news:
        print(f"News for {company} on {formatted_date} already exists in {file_path}.")
        return all_news[formatted_date]

    # Fetch news from the API
    print(f"Fetching news for {company} on {formatted_date}...")
    BASE_URL = 'https://newsapi.org/v2/everything?q=COMPANY&from=DATE&to=DATE&sortBy=popularity&apiKey=API_KEY'
    url = BASE_URL.replace('COMPANY', stock.info['longName'].split()[0])
    url = url.replace('DATE', formatted_date)
    url = url.replace('API_KEY', load_api_key())
    response = requests.get(url)
    news = response.json()

    # Save the news for the given date in the JSON file
    all_news[formatted_date] = news.get('articles', [])
    with open(file_path, 'w') as f:
        json.dump(all_news, f, indent=4)

    print(f"News for {company} on {formatted_date} has been saved to {file_path}.")
    return all_news[formatted_date]