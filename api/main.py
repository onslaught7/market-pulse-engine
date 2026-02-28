from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from config import settings

app = FastAPI(title="MarketPulse Query Engine")

# Initialize Connections
qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=settings.OPENAI_API_KEY)

# Use GPT-4o-mini for the synthesis
llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY, temperature=0.2)

# Define the Data Contract
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

@app.post("/query")
def query_marketpulse(request: QueryRequest):
    question = request.question
    
    try:
        # Embed the user's question
        question_vector = embeddings.embed_query(question)
        
        # Search the 'wisdom' collection (Top 3 results)
        wisdom_results = qdrant_client.search(
            collection_name=settings.COLLECTION_WISDOM,
            query_vector=question_vector,
            limit=3
        )
        
        # Search the 'wire' collection (Top 3 results)
        wire_results = qdrant_client.search(
            collection_name=settings.COLLECTION_WIRE,
            query_vector=question_vector,
            limit=3
        )
        
        # Extract the text from the payloads
        wisdom_text = "\n".join([hit.payload.get("page_content", "") for hit in wisdom_results])
        wire_text = "\n".join([hit.payload.get("page_content", "") for hit in wire_results])
        
        # Synthesize with the LLM
        chain = prompt_template | llm
        response = chain.invoke({
            "wisdom_context": wisdom_text,
            "wire_context": wire_text,
            "question": question
        })
        
        return {
            "question": question,
            "answer": response.content,
            "sources_scanned": len(wisdom_results) + len(wire_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)