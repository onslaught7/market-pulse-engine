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
    """
    Process a single ingestion task from Redis and index it into Qdrant.

    Extracts required fields from the payload, generates a semantic embedding
    using OpenAI, and upserts the vector with metadata into the configured
    Qdrant collection.

    The document_id acts as a deterministic UUID to ensure idempotent writes.
    Invalid payloads are skipped, and processing errors are logged without
    crashing the worker.
    """
    # Extract the Data contract fields as we receive from GO
    user_id = task_data.get("user_id")
    doc_id = task_data.get("document_id")
    content = task_data.get("content")
    metadata = task_data.get("metadata", {})

    if not content or not doc_id:
        print(" [!] Invalid payload received. Skipping.")
        return

    source_name = metadata.get("source", "unknown")
    print(f" [->] Processing: {source_name} | ID: {doc_id[:8]}...")

    start_time = time.time()
    
    # Convert the content into vector embeddings and add to Qdrant with metadata
    try:
        vector = embeddings.embed_query(content)

        qdrant_payload = {
            "page_content": content,
            **metadata
        }

        # Upsert handles both insert and update (save to qdrant)
        qdrant_client.upsert(
            collection_name=COLLECTION_WIRE,
            points=[
                models.PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload=qdrant_payload
                )
            ]
        )

        elapsed_time = time.time() - start_time
        print(f" [v] Indexed in {elapsed_time:.2f}s.")

    except Exception as e:
        print(f" [!] Failed to process vector for {doc_id}: {e}")