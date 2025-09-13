import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def gemini_response(prompt: str, SYSTEM_PROMPT: str) -> str:
        
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT
    )

    response = model.generate_content(prompt)
    # print(response.text)
    return response.text

# gemini_response("It is urgent .")