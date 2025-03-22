import json
import time

import numpy as np
import requests
from google import genai
from google.genai import types

from constants import RankingTypeFactors, TradeAction
from get_news import get_news


def load_api_key():
    try:
        with open('api_keys.json') as f:
            data = json.load(f)
            return data['AI_api_key']
    except KeyError:
        raise KeyError("The key 'news_api_key' was not found in the 'api_key.json' file.")
    except FileNotFoundError:
        raise FileNotFoundError("The 'api_key.json' file was not found.")


def analyze_article(input_text) -> int:
    while True:  # Retry loop
        try:
            client = genai.Client(
                api_key=load_api_key(),
            )

            model = "gemini-2.0-flash"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text="""I will provide the name of a company, the title of an article, its description, and a snippet of the content. Based on this information, determine whether the article signals something bad, good, or neutral for the company. Respond only with -1 (bad), 1 (good), or 0 (neutral)."""),
                        types.Part.from_text(text=input_text),
                    ],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                temperature=1,
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
                response_mime_type="text/plain",
            )

            # Collect all chunks and concatenate the text
            full_text = ""
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                full_text += chunk.text  # Append the chunk text to the full_text

            # Return the full concatenated text
            return int(full_text)

        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            return 0  # Default to neutral signal in case of an error

        except Exception as e:
            # Check if the error is a RESOURCE_EXHAUSTED error
            if isinstance(e, genai.errors.ClientError) and e.code == 429:
                print("API rate limit reached. Waiting before retrying...")
                time.sleep(10)  # Wait for 10 seconds before retrying
            else:
                print(f"Error during analysis: {e}")
                return 0  # Default to neutral signal in case of an error

def analyze_articles(articles: list, company: str) -> list:
    """
    Analyze a list of articles and return a list of AI signals (-1, 0, or 1).

    Args:
        articles (list): A list of articles, where each article is a dictionary containing 'title', 'description', and 'content'.
        company (str): The name of the company being analyzed.

    Returns:
        list: A list of AI signals (-1, 0, or 1) corresponding to the articles.
    """
    signals = []

    for article in articles:
        title = article.get('title', '')
        description = article.get('description', '')
        content = article.get('content', '')
        input_text = f"{company}\n{title}\n{description}\n{content}"

        try:
            signal = analyze_article(input_text)  # Call your existing AI function
            signals.append(signal)
        except Exception as e:
            print(f"Error analyzing article: {e}")
            signals.append(0)  # Default to neutral signal in case of an error

    return signals

def factorize_signals(popularity_rank: dict, relevancy_rank: dict) -> float:
    """
    Factorize signals based on popularity and relevancy rankings.

    Args:
        popularity_rank (dict): A list of articles ranked by popularity, each containing 'title', 'AI_signal', and 'ranking'.
        relevancy_rank (dict): A list of articles ranked by relevancy, each containing 'title', 'AI_signal', and 'ranking'.

    Returns:
        float: The final aggregated signal after applying ranking factors.
    """
    final_signals = []  # List to store the weighted signals for all articles

    # Process articles in the popularity rank
    for article in popularity_rank:
        # Check if the article also exists in the relevancy rank
        if article['title'] in [article['title'] for article in relevancy_rank]:
            # If the article exists in both rankings, apply the BOTH factor
            new_signal = (
                article['AI_signal'] * RankingTypeFactors.BOTH.factor *
                ((article['ranking'] - 1) / len(popularity_rank))  # Normalize ranking
            )
            final_signals.append(new_signal)
        else:
            # If the article exists only in the popularity rank, apply the POPULARITY factor
            final_signals.append(
                article['AI_signal'] * RankingTypeFactors.POPULARITY.factor *
                ((article['ranking'] - 1) / len(popularity_rank))  # Normalize ranking
            )

    # Process articles in the relevancy rank
    for article in relevancy_rank:
        # Check if the article does NOT exist in the popularity rank
        if article['title'] not in [article['title'] for article in popularity_rank]:
            # If the article exists only in the relevancy rank, apply the RELEVANCY factor
            new_signal = (
                article['AI_signal'] * RankingTypeFactors.RELEVANCY.factor *
                ((article['ranking'] - 1) / len(relevancy_rank))  # Normalize ranking
            )
            final_signals.append(new_signal)

    print('Final Signals:', final_signals)

    # Sum up all the weighted signals to get the final aggregated signal
    return sum(final_signals)


def get_signal(company, date):
    """
    Get the trading signal for a company based on news articles.

    Args:
        company (str): The company ticker symbol.
        date (datetime): The date for which to fetch and analyze news.

    Returns:
        tuple: A tuple containing the AI signal (BUY, SELL, or NOTHING) and the quantity to trade.
    """
    # Fetch news articles for popularity and relevancy rankings
    popularity_news = get_news(company, date, RankingTypeFactors.POPULARITY)
    relevancy_news = get_news(company, date, RankingTypeFactors.RELEVANCY)

    num_top_articles = 5

    # Analyze only the top articles
    top_popularity_articles = popularity_news[:num_top_articles]
    top_relevancy_articles = relevancy_news[:num_top_articles]

    # Analyze articles and get AI signals
    popularity_signals = analyze_articles(top_popularity_articles, company)
    relevancy_signals = analyze_articles(top_relevancy_articles, company)

    # Combine signals into rankings
    popularity_rank = [
        {'title': article.get('title', ''), 'AI_signal': signal, 'ranking': idx + 1}
        for idx, (article, signal) in enumerate(zip(top_popularity_articles, popularity_signals))
    ]

    relevancy_rank = [
        {'title': article.get('title', ''), 'AI_signal': signal, 'ranking': idx + 1}
        for idx, (article, signal) in enumerate(zip(top_relevancy_articles, relevancy_signals))
    ]

    # Factorize the signals based on rankings
    if not popularity_rank and not relevancy_rank:
        print(f"No valid signals found for {company} on {date}. Returning neutral signal.")
        return TradeAction.NOTHING, 0

    signal = factorize_signals(popularity_rank, relevancy_rank)
    print('Final Signal:', signal)
    signal = 1 if signal > 0 else -1 if signal < 0 else 0
    return TradeAction(signal), 1  # Return a quantity of 1 for simplicity