import json
import time
import redis
from qdrant_client import QdrantClient
from qdrant_client.models import models
from langchain_openai import OpenAIEmbeddings

from config import settings

print("[*] Initializing AI Brain (The Worker)...")


# Initialize connections
try:
    r = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True
    )
    r.ping()
    print(" [v] Connected to Redis Buffer.")
except Exception as e:
    raise ConnectionError("Failed to connect to Redis: {e}")


# Initialize Qdrant
try:
    qdrant_client = QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,

    )
except Exception as e:
    raise ConnectionError("Failed to connect to Qdrant: {e}")


# Initialize OpenAI Embeddings
try:
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=settings.OPENAI_API_KEY
    )
except Exception as e:
    raise ConnectionError("Failed to connect to OpenAI: {e}")


# Ensure the Qdrant connection exists
COLLECTION_WIRE = settings.COLLECTION_WIRE
if not qdrant_client.collection_exists(COLLECTION_WIRE):
    print(f" [!] Collection '{COLLECTION_WIRE}' not found. Creating...")
    qdrant.create_collection(
        collection_name=COLLECTION_WIRE,
        vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE)
    )
    print(f" [v] Collection '{COLLECTION_WIRE}' initialized.")


def process_task(task_data):
    pass