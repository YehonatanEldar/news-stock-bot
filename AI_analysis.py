import base64
import os
from google import genai
from google.genai import types
import json

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
    client = genai.Client(
        api_key=os.environ.get(load_api_key()),
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

    

def get_signal():
    pass