import json
import numpy as np
from uuid import uuid4
from tqdm import tqdm
from helper_functions.embeddings_func import embedding_model
from langchain.text_splitter import RecursiveCharacterTextSplitter

with open("preprocessed_data/docs.atlan.com_preprocessed.json", "r", encoding="utf-8") as file:
    docs_atlan = json.load(file)

with open("preprocessed_data/developer.atlan.com_preprocessed.json", "r", encoding="utf-8") as file:
    docs_developer_atlan = json.load(file)

final_docs = docs_atlan + docs_developer_atlan

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

def pinecone_data_setup(documents):
    pinecone_vectors = []
    
    for doc in tqdm(documents, desc="Processing documents"):
        chunks = splitter.split_text(doc["text"])
        
        for chunk in tqdm(chunks, desc="Creating embeddings", leave=False):
            embedding = embedding_model(chunk)
            
            # Convert numpy array to Python list for JSON serialization
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()
            
            vector_data = {
                "id": uuid4().hex,
                "values": embedding,
                "metadata": {
                    "source": doc["url"],
                    "text": chunk
                }
            }
            pinecone_vectors.append(vector_data)
    
    return pinecone_vectors

def create_pinecone_data_format():
    pinecone_data = pinecone_data_setup(final_docs)

    with open("./preprocessed_data/pinecone_db_data.json", "w", encoding="utf-8") as file:
        json.dump(pinecone_data, file, indent=4)

    print(f"Generated {len(pinecone_data)} vectors for Pinecone")

# Alternative approach using custom JSON encoder
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return super().default(obj)

def create_pinecone_data_format():
    pinecone_data = pinecone_data_setup(final_docs)

    with open("./preprocessed_data/pinecone_db_data.json", "w", encoding="utf-8") as file:
        json.dump(pinecone_data, file, indent=4, cls=NumpyEncoder)

    print(f"Generated {len(pinecone_data)} vectors for Pinecone")

