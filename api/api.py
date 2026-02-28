import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from config import settings

print("[*] Initializing MarketPulse Query Engine (The API)...")

app = FastAPI(title="MarketPulse Query Engine")

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

# Initialize GPT-4o-mini for synthesis
try:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=settings.OPENAI_API_KEY,
        temperature=0.2
    )
    print(" [v] GPT-4o-mini LLM initialized.")
except Exception as e:
    raise ConnectionError(f"Failed to initialize LLM: {e}")


# Data Contract
class QueryRequest(BaseModel):
    question: str


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
@app.post("/query")
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
        wisdom_results = qdrant_client.search(
            collection_name=settings.COLLECTION_WISDOM,
            query_vector=question_vector,
            limit=3
        )
    except Exception as e:
        print(f" [!] Qdrant search failed on '{settings.COLLECTION_WISDOM}': {e}")
        raise HTTPException(status_code=502, detail="Failed to search historical knowledge base.")

    # Step 3: Search the 'wire' collection (Top 3 results)
    try:
        wire_results = qdrant_client.search(
            collection_name=settings.COLLECTION_WIRE,
            query_vector=question_vector,
            limit=3
        )
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)