import json
import time
import redis
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from opentelemetry.propagate import extract

from config import settings
from services.ingestion_service import process_task
from core.telemetry import setup_telemetry

print("[*] Initializing AI Brain (The Worker)...")

tracer = setup_telemetry()

# Redis
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

r.ping()
print(" [v] Connected to Redis Buffer.")

# Qdrant
qdrant_client = QdrantClient(
    host=settings.QDRANT_HOST,
    port=settings.QDRANT_PORT
)

qdrant_client.get_collections()
print(" [v] Connected to Qdrant.")

# OpenAI
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=settings.OPENAI_API_KEY
)


def start_worker():
    """
    Continuously listen to the Redis queue and process incoming tasks.

    Uses a blocking BRPOP call to fetch messages from Redis. Each message
    is decoded from JSON and forwarded to `process_task()`.

    A Redis dequeue span is created using OpenTelemetry so queue wait
    times can be visualized in Jaeger.

    Designed to run indefinitely with basic error handling for resilience.
    """
    queue_name = "ingestion_queue"

    print(f" [*] Worker is LIVE. Listening to Redis queue: '{queue_name}'...")

    while True:

        # Extract the work payload from the queue without tracing the long wait itself
        result = r.brpop(queue_name, timeout=0)

        if result:
            _, message = result
            envelope = json.loads(message)

            # Support both the new envelope pattern and the old raw payload pattern
            if "payload" in envelope and "trace_context" in envelope:
                payload = envelope["payload"]
                carrier = envelope["trace_context"]
            else:
                payload = envelope
                carrier = {}

            # Reconstruct the trace context originally injected by Gateway
            ctx = extract(carrier)

            # Start a linked span using the reconstructed context
            with tracer.start_as_current_span("worker.process_task", context=ctx):
                process_task(payload, embeddings, qdrant_client)


if __name__ == "__main__":
    time.sleep(2)
    start_worker()