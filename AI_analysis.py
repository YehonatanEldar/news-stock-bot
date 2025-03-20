import base64
import os
from google import genai
from google.genai import types
import json
from get_news import get_news
import time
import requests

def load_api_key():
    try:
        with open('api_keys.json') as f:
            data = json.load(f)
            return data['AI_api_key']
    except KeyError:
        raise KeyError("The key 'news_api_key' was not found in the 'api_key.json' file.")
    except FileNotFoundError:
        raise FileNotFoundError("The 'api_key.json' file was not found.")


def analyze_article(input_text) -> str:
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
        return full_text

    except requests.exceptions.RequestException as e:
        if e == {'error': {'code': 429, 'message': 'Resource has been exhausted (e.g. check quota).', 'status': 'RESOURCE_EXHAUSTED'}}:
            print("API rate limit reached. Please try again later.")
        print(f"Network error: {e}")
        return "0"  # Default to neutral signal in case of an error
    except Exception as e:
        print(f"Error during analysis: {e}")
        return "0"  # Default to neutral signal in case of an error


def get_signal(company, date):
    news = get_news(company, date)  # This now returns a list of articles for the given date
    signal = 0
    
    # Analyze only the top 5 articles
    top_articles = news[:5]  # Get the first 5 articles

    for idx, article in enumerate(top_articles):  # Iterate over the top 5 articles
        time.sleep(1)  # Sleep for 1 second to avoid rate limiting
        title = article.get('title', '')
        description = article.get('description', '')
        content = article.get('content', '')
        input_text = f"{company}\n{title}\n{description}\n{content}"
        
        result = analyze_article(input_text)
        signal += int(result)
        print()

    # Determine the overall signal
    signal = 1 if signal > 0 else -1 if signal < 0 else 0
    return signal