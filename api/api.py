import time
import json
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.callbacks import BaseCallbackHandler
from config import settings

print("[*] Initializing MarketPulse Query Engine (The API)...")

app = FastAPI(title="MarketPulse Query Engine")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Qdrant
try:
    qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    qdrant_client.get_collections()  # Force a real connection attempt
    print(" [v] Connected to Qdrant.")
except Exception as e:
    raise ConnectionError(f"Failed to connect to Qdrant: {e}")

# Initialize OpenAI Embeddings
try:
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=settings.OPENAI_API_KEY
    )
    print(" [v] OpenAI Embeddings model initialized.")
except Exception as e:
    raise ConnectionError(f"Failed to initialize OpenAI Embeddings: {e}")

# Initialize GPT-4o-mini for synthesis (non-streaming for REST)
try:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=settings.OPENAI_API_KEY,
        temperature=0.2
    )
    print(" [v] GPT-4o-mini LLM initialized.")
except Exception as e:
    raise ConnectionError(f"Failed to initialize LLM: {e}")

# Streaming LLM instance for WebSocket
llm_streaming = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=settings.OPENAI_API_KEY,
    temperature=0.2,
    streaming=True
)


# Data Contract
class QueryRequest(BaseModel):
    question: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"question": "What is the current sentiment around Bitcoin?"},
                {"question": "Summarize the latest news on the S&P 500"},
                {"question": "What are analysts saying about the Fed's interest rate decision?"},
            ]
        }
    }


# The Analyst Prompt
SYSTEM_PROMPT = """You are an elite financial analyst. 
Use the provided historical context and live news to answer the user's question.
If the answer is not contained in the context, say "I do not have enough data to answer this."

Historical Context (Wisdom):
{wisdom_context}

Live News (The Wire):
{wire_context}

Question: {question}
"""

prompt_template = ChatPromptTemplate.from_template(SYSTEM_PROMPT)


# API Endpoint
@app.post(
    "/query",
    summary="Ask MarketPulse a financial question",
    description=(
        "Submit a natural-language question about markets, stocks, or crypto. "
        "The engine searches both historical knowledge (Wisdom) and live news (The Wire), "
        "then synthesizes an answer using LLM.\n\n"
        "**Example questions to try:**\n"
        "- *What is the current sentiment around Bitcoin?*\n"
        "- *Summarize the latest news on the S&P 500*\n"
        "- *What are analysts saying about the Fed's interest rate decision?*"
    ),
)
def query_marketpulse(request: QueryRequest):
    question = request.question.strip()

    # Validate the question is not empty or whitespace
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    print(f" [->] Received query: {question[:60]}...")
    start_time = time.time()

    # Step 1: Embed the user's question
    try:
        question_vector = embeddings.embed_query(question)
    except Exception as e:
        print(f" [!] Embedding failed: {e}")
        raise HTTPException(status_code=502, detail="Failed to generate embedding for your question.")

    # Step 2: Search the 'wisdom' collection (Top 3 results)
    try:
        wisdom_results = qdrant_client.query_points(
            collection_name=settings.COLLECTION_WISDOM,
            query=question_vector,
            limit=3
        ).points
    except Exception as e:
        print(f" [!] Qdrant search failed on '{settings.COLLECTION_WISDOM}': {e}")
        raise HTTPException(status_code=502, detail="Failed to search historical knowledge base.")

    # Step 3: Search the 'wire' collection (Top 3 results)
    try:
        wire_results = qdrant_client.query_points(
            collection_name=settings.COLLECTION_WIRE,
            query=question_vector,
            limit=3
        ).points
    except Exception as e:
        print(f" [!] Qdrant search failed on '{settings.COLLECTION_WIRE}': {e}")
        raise HTTPException(status_code=502, detail="Failed to search live news feed.")

    # Step 4: Extract the text from the payloads
    wisdom_text = "\n".join([hit.payload.get("page_content", "") for hit in wisdom_results])
    wire_text = "\n".join([hit.payload.get("page_content", "") for hit in wire_results])

    # Step 5: Synthesize with the LLM
    try:
        chain = prompt_template | llm
        response = chain.invoke({
            "wisdom_context": wisdom_text,
            "wire_context": wire_text,
            "question": question
        })
    except Exception as e:
        print(f" [!] LLM synthesis failed: {e}")
        raise HTTPException(status_code=502, detail="Failed to synthesize answer from AI model.")

    elapsed_time = time.time() - start_time
    sources_scanned = len(wisdom_results) + len(wire_results)
    print(f" [v] Query answered in {elapsed_time:.2f}s | Sources: {sources_scanned}")

    return {
        "question": question,
        "answer": response.content,
        "sources_scanned": sources_scanned
    }

# --- WebSocket Endpoint for Streaming ---
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print(" [ws] Client connected.")

    try:
        while True:
            data = await ws.receive_text()
            payload = json.loads(data)
            question = payload.get("question", "").strip()

            if not question:
                await ws.send_json({"type": "error", "detail": "Question cannot be empty."})
                continue

            print(f" [ws ->] Query: {question[:60]}...")
            start_time = time.time()

            try:
                # Embed
                question_vector = embeddings.embed_query(question)

                # Search both collections
                wisdom_results = qdrant_client.query_points(
                    collection_name=settings.COLLECTION_WISDOM,
                    query=question_vector,
                    limit=3
                ).points

                wire_results = qdrant_client.query_points(
                    collection_name=settings.COLLECTION_WIRE,
                    query=question_vector,
                    limit=3
                ).points

                wisdom_text = "\n".join([hit.payload.get("page_content", "") for hit in wisdom_results])
                wire_text = "\n".join([hit.payload.get("page_content", "") for hit in wire_results])

                # Stream LLM response token by token
                chain = prompt_template | llm_streaming
                async for chunk in chain.astream({
                    "wisdom_context": wisdom_text,
                    "wire_context": wire_text,
                    "question": question
                }):
                    if chunk.content:
                        await ws.send_json({"type": "token", "content": chunk.content})

                sources_scanned = len(wisdom_results) + len(wire_results)
                elapsed = time.time() - start_time
                await ws.send_json({"type": "done", "sources_scanned": sources_scanned})
                print(f" [ws v] Streamed in {elapsed:.2f}s | Sources: {sources_scanned}")

            except Exception as e:
                print(f" [ws !] Error: {e}")
                await ws.send_json({"type": "error", "detail": str(e)})

    except WebSocketDisconnect:
        print(" [ws] Client disconnected.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)