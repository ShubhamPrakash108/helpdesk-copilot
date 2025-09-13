from helper_functions.embeddings_func import embedding_model
from helper_functions.preprocess_text import preprocess_text_from_web
import json

with open("./scraped_data/docs.atlan.com.json", "r", encoding="utf-8") as f:
    docs_atlan_content = json.load(f)

with open("./scraped_data/developer.atlan.com.json", "r", encoding="utf-8") as f:
    dev_atlan_content = json.load(f)

docs_atlan_content_preprocessed = [{"url": item['url'], "text": preprocess_text_from_web(item['content'])} for item in docs_atlan_content]
dev_atlan_content_preprocessed = [{"url": item['url'], "text": preprocess_text_from_web(item['content'])} for item in dev_atlan_content]

with open("./preprocessed_data/docs.atlan.com_preprocessed.json", "w", encoding="utf-8") as f:
    json.dump(docs_atlan_content_preprocessed, f, ensure_ascii=False, indent=2)

with open("./preprocessed_data/developer.atlan.com_preprocessed.json", "w", encoding="utf-8") as f:
    json.dump(dev_atlan_content_preprocessed, f, ensure_ascii=False, indent=2)


