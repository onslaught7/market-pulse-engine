from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_openai import OpenAIEmbeddings
from config import settings # Reuse your config!

# Connect
client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=settings.OPENAI_API_KEY)

# The Test Query
query = "How does compounding work in stock market?"
print(f"[*] Querying: '{query}'")

# Embed
vector = embeddings.embed_query(query)

# SEARCH 1: Ask "The Global Wisdom" (Psychology of Money)
print("\n--- Search 1: Global Context ---")
results_global = client.query_points(
    collection_name=settings.COLLECTION_WISDOM,
    query=vector,
    limit=1,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(key="region", match=models.MatchValue(value="global"))
        ]
    )
)
for hit in results_global.points:
    print(f"Source: {hit.payload['title']}")
    print(f"Snippet: {hit.payload['page_content'][:150]}...\n")

# SEARCH 2: Ask "The Indian Context" (Stocks to Riches)
print("--- Search 2: Indian Context ---")
results_india = client.query_points(
    collection_name=settings.COLLECTION_WISDOM,
    query=vector,
    limit=1,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(key="region", match=models.MatchValue(value="india"))
        ]
    )
)
for hit in results_india.points:
    print(f"Source: {hit.payload['title']}")
    print(f"Snippet: {hit.payload['page_content'][:150]}...")