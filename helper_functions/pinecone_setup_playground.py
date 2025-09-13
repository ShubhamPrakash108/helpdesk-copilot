import json
import os
from pinecone import Pinecone, ServerlessSpec
from helper_functions.embeddings_func import embedding_model
from tqdm import tqdm
import time
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from typing import List, Tuple, Dict, Any

load_dotenv()

# Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "developer-atlan-docs"
DIMENSION = 384
BATCH_SIZE = 100
MAX_WORKERS = 8  # Number of threads for parallel processing
EMBEDDING_BATCH_SIZE = 10  # Number of documents to process per thread

# Thread-local storage for model instances
thread_local = threading.local()

def get_thread_embedding_model():
    """
    Get embedding model instance for current thread
    This ensures each thread has its own model instance
    """
    if not hasattr(thread_local, 'model'):
        thread_local.model = embedding_model
    return thread_local.model

def initialize_pinecone():
    """
    Initialize Pinecone client and create/connect to index
    """
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    if INDEX_NAME not in pc.list_indexes().names():
        print(f"Creating new index: {INDEX_NAME}")
        pc.create_index(
            name=INDEX_NAME,
            dimension=DIMENSION,
            metric="cosine",  
            spec=ServerlessSpec(
                cloud="aws",  
                region="us-east-1"  
            )
        )
        
        print("Waiting for index to be ready...")
        time.sleep(10)
    else:
        print(f"Using existing index: {INDEX_NAME}")
    
    index = pc.Index(INDEX_NAME)
    return index

def load_json_data(file_path: str) -> List[Dict]:
    """
    Load and parse the JSON file containing the preprocessed data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"Loaded {len(data)} documents from {file_path}")
            return data
    except FileNotFoundError:
        print(f"Error: File {file_path} not found!")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

def process_single_document(doc_data: Tuple[int, Dict]) -> Tuple[str, List[float], Dict]:
    """
    Process a single document to create embedding
    Returns tuple of (doc_id, embedding, metadata)
    """
    doc_idx, doc = doc_data
    
    try:
        url = doc.get('url', '')
        content = doc.get('text', '')
        
        # Skip documents with empty content
        if not content.strip():
            return None
        
        # Get thread-local embedding model
        embedding_func = get_thread_embedding_model()
        embedding = embedding_func(content)
        
        doc_id = f"doc_{doc_idx}"
        
        metadata = {
            "url": url,
            "content_length": len(content),
            "content_preview": content[:200]
        }
        
        return (doc_id, embedding.tolist(), metadata)
        
    except Exception as e:
        print(f"Error processing document {doc_idx}: {e}")
        return None

def create_embeddings_parallel(documents: List[Dict], start_idx: int = 0) -> List[Tuple]:
    """
    Create embeddings for documents using multithreading
    Returns list of tuples (id, embedding, metadata)
    """
    vectors = []
    
    # Prepare data with indices for processing
    doc_data = [(start_idx + i, doc) for i, doc in enumerate(documents)]
    
    # Create progress bar for embedding generation
    with tqdm(total=len(documents), desc="Creating embeddings", unit="docs") as pbar:
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submit all tasks
            future_to_doc = {
                executor.submit(process_single_document, data): data[0] 
                for data in doc_data
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_doc):
                doc_idx = future_to_doc[future]
                try:
                    result = future.result()
                    if result is not None:
                        vectors.append(result)
                    pbar.update(1)
                except Exception as e:
                    print(f"Error in thread for document {doc_idx}: {e}")
                    pbar.update(1)
    
    return vectors

def upload_to_pinecone_with_progress(index, vectors: List[Tuple]) -> None:
    """
    Upload vectors to Pinecone in batches with progress bar
    """
    total_vectors = len(vectors)
    
    # Create progress bar for uploading
    with tqdm(total=total_vectors, desc="Uploading to Pinecone", unit="vectors") as pbar:
        
        for i in range(0, total_vectors, BATCH_SIZE):
            batch = vectors[i:i + BATCH_SIZE]
            
            try:
                # Upsert batch to Pinecone
                index.upsert(vectors=batch)
                
                # Update progress bar
                pbar.update(len(batch))
                
                # Small delay to respect rate limits
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error uploading batch starting at {i}: {e}")
                pbar.update(len(batch))
                continue

def process_documents_in_chunks(documents: List[Dict]) -> List[Tuple]:
    """
    Process all documents in chunks with multithreading
    """
    all_vectors = []
    chunk_size = 100  # Larger chunks for better efficiency
    
    # Create overall progress for chunk processing
    total_chunks = (len(documents) + chunk_size - 1) // chunk_size
    
    with tqdm(total=total_chunks, desc="Processing chunks", unit="chunks") as chunk_pbar:
        
        for i in range(0, len(documents), chunk_size):
            chunk = documents[i:i + chunk_size]
            
            print(f"\nProcessing chunk {i//chunk_size + 1}/{total_chunks}")
            print(f"Documents {i} to {min(i + chunk_size - 1, len(documents) - 1)}")
            
            # Process chunk with multithreading
            vectors = create_embeddings_parallel(chunk, start_idx=i)
            all_vectors.extend(vectors)
            
            chunk_pbar.update(1)
            
            # Optional: Small delay between chunks to prevent overwhelming the system
            time.sleep(1)
    
    return all_vectors

def main():
    """
    Main function to orchestrate the entire process
    """
    print("🚀 Starting Pinecone Vector Database Upload Process")
    print("="*60)
    
    # Check API key
    if not PINECONE_API_KEY:
        print("❌ Error: Please set PINECONE_API_KEY environment variable")
        print("You can set it by running: export PINECONE_API_KEY='your-api-key-here'")
        return
    
    json_file_path = "./preprocessed_data/docs.atlan.com_preprocessed.json"
    
    # Step 1: Load JSON data
    print("\n📁 Step 1: Loading JSON data...")
    documents = load_json_data(json_file_path)
    if not documents:
        return
    
    # Step 2: Initialize Pinecone
    print("\n🔧 Step 2: Initializing Pinecone...")
    try:
        index = initialize_pinecone()
        print(f"✅ Connected to Pinecone index: {INDEX_NAME}")
    except Exception as e:
        print(f"❌ Error initializing Pinecone: {e}")
        return
    
    # Step 3: Create embeddings with multithreading
    print(f"\n🧠 Step 3: Creating embeddings with {MAX_WORKERS} threads...")
    print(f"Processing {len(documents)} documents in parallel...")
    
    start_time = time.time()
    all_vectors = process_documents_in_chunks(documents)
    embedding_time = time.time() - start_time
    
    print(f"\n✅ Embedding generation completed!")
    print(f"📊 Created {len(all_vectors)} embeddings in {embedding_time:.2f} seconds")
    print(f"⚡ Average: {len(all_vectors)/embedding_time:.2f} embeddings/second")
    
    # Step 4: Upload to Pinecone
    print(f"\n☁️ Step 4: Uploading {len(all_vectors)} vectors to Pinecone...")
    if all_vectors:
        upload_start = time.time()
        upload_to_pinecone_with_progress(index, all_vectors)
        upload_time = time.time() - upload_start
        
        # Verify upload
        stats = index.describe_index_stats()
        
        print(f"\n🎉 Upload completed successfully!")
        print("="*50)
        print(f"📈 Statistics:")
        print(f"   • Total vectors in index: {stats['total_vector_count']}")
        print(f"   • Embedding time: {embedding_time:.2f}s")
        print(f"   • Upload time: {upload_time:.2f}s")
        print(f"   • Total time: {(embedding_time + upload_time):.2f}s")
        print(f"   • Processing speed: {len(all_vectors)/(embedding_time + upload_time):.2f} docs/second")
        
    else:
        print("❌ No vectors to upload.")

if __name__ == "__main__":
    main()