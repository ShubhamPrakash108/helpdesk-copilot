from helper_functions.docs_preprocessing_for_pinecone import create_pinecone_data_format
from pinecone import Pinecone
from pinecone import ServerlessSpec
from dotenv import load_dotenv
import os
import json
from tqdm import tqdm
load_dotenv()

if "pinecone_db_data.json" not in os.listdir("./preprocessed_data"):
    create_pinecone_data_format()

def sending_data_to_vector_db(index_name, metric = "cosine", dimension=384, cloud="aws", region="us-east-1"):
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    if not pc.list_indexes() or index_name not in pc.list_indexes():
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(cloud=cloud, region=region)
        )
        index = pc.Index(index_name)

        with open("./preprocessed_data/pinecone_db_data.json", "r") as f:
            items = json.load(f)

        batch_size = 100
        for i in tqdm(range(0, len(items), batch_size)):
            batch = items[i:i+batch_size]
            index.upsert(vectors=batch)
            #print(f"Uploaded batch {i//batch_size + 1}/{(len(items) + batch_size - 1)//batch_size}")
           
        print("Data uploaded successfully.")
        print(f"Index '{index_name}' created with dimension={dimension} and metric='{metric}'.")
    else:
        print(f"Index '{index_name}' already exists.")

    
    
sending_data_to_vector_db(os.getenv("PINECONE_INDEX_NAME"))