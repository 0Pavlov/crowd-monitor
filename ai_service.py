import os
from dotenv import load_dotenv
import requests
import json

test_prompt: str = "This is the test, just reply with the short success message (3-4 words at max)"
test_system_prompt: str = "You are a helpful assistant. Provide only the final user-facing answer directly, without including any internal reasoning, commentary, or thought process."

def ai_get_answer(prompt: str, system_prompt: str) -> str | bool:
    try:
        load_dotenv()
    except Exception as e:
        print(f"Error {e} occured during the loading dotenv.")
        return False

    try:
        api_key: str = os.getenv("OPENROUTER_API_KEY")
    except Exception as e:
        print(f"Error {e} occured during the extracting the api key.")
        return False

    try:
        response = requests.post(
          url="https://openrouter.ai/api/v1/chat/completions",
          headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
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
        if response.status_code != 200:
            print(f"API Error: {response.status_code} - {response.text}")
            return False
            
        answer: str = response.json()['choices'][0]['message']['content']
        return answer
    except Exception as e:
        print(f"Error {e} occured during the requesting the API")
        return False

if __name__ == "__main__":
    answer: str | bool = ai_get_answer(test_prompt, test_system_prompt)
    if not answer:
        print("Failed to request the ai")
    elif answer == "":
        print("Ai has returned an empty answer")
    else:
        print(answer)
