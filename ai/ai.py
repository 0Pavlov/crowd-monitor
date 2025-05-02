import os
from dotenv import load_dotenv
import requests
import json


# Define the test prompts
test_prompt: str = "This is the test, just reply with the short success message (3-4 words at max)"
test_system_prompt: str = "You are a helpful assistant. Provide only the final user-facing answer directly, without including any internal reasoning, commentary, or thought process."


def ai_get_answer(prompt: str, system_prompt: str) -> str | bool:
    """Gets answer from an ai
    
    Args:
        prompt (str): Regular prompt, main question.
        system_prompt (str): System prompt, which regulates how the ai is answering (e.g. format, length).

    Returns:
        False (bool): Status code in case of an error.
        answer (str): Answer from a model (can sometimes be an empty str, which is should be handeled by the caller).
    """
    try:
        # Load env vars from .env file
        load_dotenv()
    except Exception as e:
        print(f"Error {e} occured during the loading dotenv.")
        return False

    try:
        # Extract the API key
        api_key: str = os.getenv("OPENROUTER_API_KEY")
    except Exception as e:
        print(f"Error {e} occured during the extracting the api key.")
        return False

    try:
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
                "content": system_prompt
              },
              {
                "role": "user",
                "content": prompt
              }
            ],
            
          })
        )
    except Exception as e:
        print(f"Error {e} occured during the requesting the API")
        return False

    # Extract the answer
    answer: str = response.json()['choices'][0]['message']['content']

    return answer


if __name__ == "__main__":
    answer: str | bool = ai_get_answer(test_prompt, test_system_prompt)
    if not answer:
        print("Failed to request the ai")
    elif answer == "":
        print("Ai has returned an empty answer")
    else:
        print(answer)
