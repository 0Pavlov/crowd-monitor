import os
from dotenv import load_dotenv
import requests
import json


# Define the test prompts
test_prompt: str = "Hello, this is the test, just reply something short (3-4 words at max)"
test_system_promt: str = "You are a helpful assistant. Provide only the final user-facing answer directly, without including any internal reasoning, commentary, or thought process."


def ai_get_answer(prompt: str, system_promt: str):
    # Load env vars from .env file
    load_dotenv()

    # Extract the API key
    api_key: str = os.getenv("OPENROUTER_API_KEY")

    response = requests.post(
      url="https://openrouter.ai/api/v1/chat/completions",
      headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
      },
      data=json.dumps({
        "model": "deepseek/deepseek-r1:free",
        "messages": [
          {
            "role": "system",
            "content": system_promt
          },
          {
            "role": "user",
            "content": prompt
          }
        ],
        
      })
    )

    return response.json()['choices'][0]['message']['content']


if __name__ == "__main__":
    print(ai_get_answer(test_prompt, test_system_promt))
