from helper_functions.llm_gemini import gemini_response
from helper_functions.llm_groq import groq_response
from prompts.prompt_topic_tags import SYSTEM_PROMPT_TOPIC_TAGS

def topic_tags_of_the_concern(text,llm_choice,groq_api_key, SYSTEM_PROMPT=SYSTEM_PROMPT_TOPIC_TAGS) -> str:
    if llm_choice == "gemini":
        return gemini_response(text, SYSTEM_PROMPT)
    elif llm_choice == "groq":
        return groq_response(text, SYSTEM_PROMPT, groq_api_key)
    else:
        return "Invalid LLM choice"
    
# print("Using Gemini")
# print(topic_tags_of_the_concern("I have a problem with my internet connection and my billing statement is incorrect.", "gemini"))
# print("Using Groq")
# print(topic_tags_of_the_concern("I have a problem with my internet connection and my billing statement is incorrect.", "groq"))