import time
from opentelemetry import trace
from config import settings
from qdrant_client import models

tracer = trace.get_tracer(__name__)


def process_task(task_data, embeddings, qdrant_client):
    """
    Process a single ingestion task from Redis and index it into Qdrant.

    Extracts required fields from the payload, generates a semantic embedding
    using OpenAI, and upserts the vector with metadata into the configured
    Qdrant collection.

    The document_id acts as a deterministic UUID to ensure idempotent writes.
    Invalid payloads are skipped, and processing errors are logged without
    crashing the worker.

    OpenTelemetry spans are used to measure embedding latency and
    Qdrant indexing performance.
    """
    user_id = task_data.get("user_id")
    doc_id = task_data.get("document_id")
    content = task_data.get("content")
    metadata = task_data.get("metadata", {})

    if not content or not doc_id or not user_id:
        print(" [!] Invalid payload received. Skipping.")
        return

    source_name = metadata.get("source", "unknown")

    print(f" [->] Processing: {source_name} | ID: {doc_id[:8]}...")

    start_time = time.time()

    try:

        with tracer.start_as_current_span("openai.embedding"):
            vector = embeddings.embed_query(content)

        qdrant_payload = {
            "page_content": content,
            **metadata
        }

        with tracer.start_as_current_span("qdrant.upsert"):
            qdrant_client.upsert(
                collection_name=settings.COLLECTION_WIRE,
                points=[
                    models.PointStruct(
                        id=doc_id,
                        vector=vector,
                        payload=qdrant_payload
                    )
                ]
            )

        elapsed = time.time() - start_time
        print(f" [v] Indexed in {elapsed:.2f}s.")

    except Exception as e:
        print(f" [!] Failed to process vector for {doc_id}: {e}")