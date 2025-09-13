def emotion_to_emoji(emotion):
    emoji_map = {
        'excitement': '🤩',
        'pride': '🏅',
        'joy': '😊',
        'approval': '👍',
        'admiration': '👏',
        'desire': '😍',
        'love': '❤️',
        'optimism': '🌈',
        'amusement': '😂',
        'caring': '🤗',
        'realization': '💡',
        'gratitude': '🙏',
        'curiosity': '🤔',
        'relief': '😌',
        'surprise': '😮',
        'neutral': '😐',
        'nervousness': '😬',
        'confusion': '😕',
        'remorse': '😔',
        'anger': '😡',
        'annoyance': '😒',
        'grief': '😭',
        'fear': '😨',
        'embarrassment': '😳',
        'disapproval': '👎',
        'disgust': '🤢',
        'disappointment': '😞',
        'sadness': '😢'
    }
    return emoji_map.get(emotion.lower(), '🤷')

# print(emotion_to_emoji("joy"))