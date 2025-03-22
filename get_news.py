import yfinance as yf
import requests
import datetime
import json
import os
from constants import RankingTypeFactors

def load_api_key() -> str:
    try:
        with open('api_keys.json') as f:
            data = json.load(f)
            return data['news_api_key']
    except KeyError:
        raise KeyError("The key 'news_api_key' was not found in the 'api_key.json' file.")
    except FileNotFoundError:
        raise FileNotFoundError("The 'api_key.json' file was not found.")

def get_news(company: str, date: str, sortBy: RankingTypeFactors) -> list:
    stock = yf.Ticker(company)
    formatted_date = date.strftime('%Y-%m-%d')
    file_path = f'news/{sortBy.string}/{company}_News.json'

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Load existing news data if the file exists
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            all_news = json.load(f)
    else:
        all_news = {}

    # If news for the given date already exists, return it
    if formatted_date in all_news:
        print(f"News for {company} on {formatted_date} already exists in {file_path}.")
        return all_news.get(formatted_date, [])

    # Fetch news from the API
    print(f"Fetching news for {company} on {formatted_date}...")
    BASE_URL = 'https://newsapi.org/v2/everything?q=COMPANY&from=DATE&to=DATE&sortBy=SORT&apiKey=API_KEY'
    url = BASE_URL.replace('COMPANY', stock.info['longName'].split()[0])
    url = url.replace('DATE', formatted_date)
    url = url.replace('API_KEY', load_api_key())
    url = url.replace('SORT', sortBy.string)
    response = requests.get(url)
    news = response.json()

    # Extract the articles key
    articles = news.get('articles', [])

    # Save the news for the given date in the JSON file
    all_news[formatted_date] = articles
    with open(file_path, 'w') as f:
        json.dump(all_news, f, indent=4)

    print(f"News for {company} on {formatted_date} has been saved to {file_path}.")
    print(f"Type of Popularity News: {type(articles)}")
    print(f"Length of Popularity News: {len(articles) if isinstance(articles, list) else 'Not a list'}")
    return articles
