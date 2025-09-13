from pinecone.grpc import PineconeGRPC as Pinecone
from helper_functions.embeddings_func import embedding_model
from helper_functions.llm_gemini import gemini_response
from helper_functions.llm_groq import groq_response
import os
from dotenv import load_dotenv
import time
import random
load_dotenv()


pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

# query = "Explain me about AzureEventHub"
# query_embedding = embedding_model(query)
t1 = time.perf_counter()

results = ""

def show_metadata(query):
    query_embedding = embedding_model(query)
    results = index.query(query_embedding, top_k=10, include_values=True, include_metadata=True)
    for match in results['matches']:
        print(match['metadata'])
    documents = [match['metadata']['text'] for match in results['matches']]
    context = "\n\n".join(documents)
    source_urls_string = ""
    source_urls = [match['metadata']['source'] for match in results['matches']]
    source_urls_string = "\n".join(source_urls)
    print("Source URLs: ", source_urls_string)
    return results, context, source_urls

results, context, source_urls = show_metadata("Explain me about AzureEventHub")

print(f"Time taken for Pinecone query: {time.perf_counter() - t1} seconds")
# documents = [match['metadata']['text'] for match in results['matches']]
# context = "\n\n".join(documents)

# print(context) 


def llm_generation(prompt, context, llm = "groq"):
    context = context[:1000]
    SYSTEM_PROMPT = f"""You are a helpful AI assistant. Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer. Just tell "I don't know" and refering the concern to concerned authority.  Nothing else.
    Context: {context} 
    Question: {prompt} 
    Answer in detail:"""
    t1 = time.perf_counter()
    llm_response = ""
    groq_apis = [os.getenv("GROQ_API_KEY"),os.getenv("GROQ_API_KEY_2")]
    if llm == "gemini":
        print("Using Gemini LLM")
        llm_response = gemini_response(prompt, SYSTEM_PROMPT)
    elif llm == "groq":
        print("Using Groq LLM")
        llm_response = groq_response(prompt, SYSTEM_PROMPT,random.choice(groq_apis))
    print(f"Time taken for LLM response: {time.perf_counter() - t1} seconds")
    return llm_response 


# gemini_response = llm_generation("Explain me about AzureEventHub", context, llm="gemini")
# groq_response = llm_generation("Explain me about AzureEventHub", context, llm="groq")

# print("Gemini Response: ", gemini_response)
# print("Groq Response: ", groq_response)