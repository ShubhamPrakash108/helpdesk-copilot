import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

base_directory = "./model"
model_name = "joeddav/distilbert-base-uncased-go-emotions-student"
model_folder_name = "go_emotions_student"
save_directory = os.path.join(base_directory, model_folder_name)
os.makedirs(save_directory, exist_ok=True)

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

tokenizer.save_pretrained(save_directory)
model.save_pretrained(save_directory)

local_tokenizer = AutoTokenizer.from_pretrained(save_directory)
local_model = AutoModelForSequenceClassification.from_pretrained(save_directory)

classifier = pipeline(
        "text-classification",
        model=local_model,
        tokenizer=local_tokenizer,
        top_k=None
    )

def sentiment_analysis(text):
    results = classifier(text)
    # print(results[0][0]['label'])
    return results[0][0]['label']

# print(sentiment_analysis("I love my laptop!"))