from helper_functions.llm_gemini import gemini_response
from helper_functions.llm_groq import groq_response
from prompts.prompt_priority import SYSTEM_PROMPT_PRIORITY
import os
from dotenv import load_dotenv
load_dotenv()

def priority_of_the_concern(text,llm_choice,groq_api_key, SYSTEM_PROMPT=SYSTEM_PROMPT_PRIORITY) -> str:
    """
    Get the priority of the concern using rule based method or using LLM
    """
    high_priority = ["Urgent","Immediate", "As soon as possible", "Critical", "Important", "Priority", "Emergency", "ASAP", "Serious"]
    medium_priority = ["Soon", "In a few days", "Within a week", "Moderate", "Normal", "Standard", "Regular", "Usual", "Average", "Typical"]
    low_priority = ["Later", "In the future", "Not urgent", "Trivial", "Minor", "Negligible", "Low", "Non-urgent", "Whenever", "At your convenience", "No rush", "Eventually"]

    text_lower = text.lower()

    if any(word.lower() in text_lower for word in high_priority):
        return "High_Priority"
    elif any(word.lower() in text_lower for word in medium_priority):
        return "Medium_Priority"
    elif any(word.lower() in text_lower for word in low_priority):
        return "Low_Priority"
    else:
        # print("Using LLM to determine priority...")
        llm_response = ""
        if llm_choice == "gemini":
            llm_response = gemini_response(text, SYSTEM_PROMPT)
        elif llm_choice == "groq":
            llm_response = groq_response(text, SYSTEM_PROMPT, groq_api_key)
        else:
            return "Invalid LLM choice"

        if llm_response not in ["High_Priority", "Medium_Priority", "Low_Priority"]:
            if llm_choice == "gemini":
                llm_response = gemini_response(text, SYSTEM_PROMPT)
            elif llm_choice == "groq":
                llm_response = groq_response(text, SYSTEM_PROMPT, groq_api_key)
            else:
                return "Invalid LLM choice"

    return llm_response


# print(priority_of_the_concern("It is not urg353ent", "groq", groq_api_key=os.environ.get("GROQ_API_KEY")))
