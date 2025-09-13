from sentence_transformers import SentenceTransformer
import os

model_dir = "./model/embedding_model"

os.makedirs(model_dir, exist_ok=True)

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', cache_folder=model_dir)

def embedding_model(text):
    embedding = model.encode([text])[0]
    return embedding

# print(embedding_model("Hello, world!"), len(embedding_model("Hello, world!")))
