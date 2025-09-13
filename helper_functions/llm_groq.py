import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

def groq_response(prompt: str, SYSTEM_PROMPT: str, groq_api_key: str) -> str:


    
    client = Groq(
        api_key=groq_api_key,
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gemma2-9b-it", 
        stream=False,
    )

    return chat_completion.choices[0].message.content

# print(groq_response("Who are you?", "You are a helpful assistant.", os.environ.get("GROQ_API_KEY")))