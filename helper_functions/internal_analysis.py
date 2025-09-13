from helper_functions.sentiment_analysis import sentiment_analysis
from helper_functions.emoji import emotion_to_emoji
from helper_functions.topic_tags import topic_tags_of_the_concern
from helper_functions.priority import priority_of_the_concern
from dotenv import load_dotenv
import os
import random


load_dotenv()


def internal_analysis(body):
    sentiment = sentiment_analysis(body)
    # print("Sentiment:", sentiment)
    emoji = emotion_to_emoji(sentiment)
    # print("Emoji:", emoji)
    groq_api_keys = [os.getenv("GROQ_API_KEY"),os.getenv("GROQ_API_KEY_2")]
    topics = topic_tags_of_the_concern(body,"groq",random.choice(groq_api_keys))
    # print("Topics:", topics)
    priority = priority_of_the_concern(body,"groq",random.choice(groq_api_keys))
    # print("Priority:", priority)

    return {
        "sentiment": sentiment,
        "emoji": emoji,
        "topics": topics,
        "priority": priority
    }

internal_analysis("I am very happy with the service provided. The team was prompt and efficient.")