"""
The Brain: Qdrant client, embeddings, and LLM orchestration.
"""

import time
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from config import settings


SYSTEM_PROMPT = """You are an elite financial analyst.

Use the provided historical context and live news to answer the user's question.
If the answer is not contained in the context, say "I do not have enough data to answer this."

Historical Context (Wisdom):
{wisdom_context}

Live News (The Wire):
{wire_context}

Question: {question}
"""


class RAGEngine:

    def __init__(self):

        # Qdrant
        self.qdrant = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )

        self.qdrant.get_collections()

        # embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=settings.OPENAI_API_KEY
        )

        # normal LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.OPENAI_API_KEY,
            temperature=0.2
        )

        # streaming LLM
        self.llm_streaming = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.OPENAI_API_KEY,
            temperature=0.2,
            streaming=True
        )

        self.prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)

    def search(self, question_vector):

        wisdom_results = self.qdrant.query_points(
            collection_name=settings.COLLECTION_WISDOM,
            query=question_vector,
            limit=3
        ).points

        wire_results = self.qdrant.query_points(
            collection_name=settings.COLLECTION_WIRE,
            query=question_vector,
            limit=3
        ).points

        wisdom_text = "\n".join(
            [hit.payload.get("page_content", "") for hit in wisdom_results]
        )

        wire_text = "\n".join(
            [hit.payload.get("page_content", "") for hit in wire_results]
        )

        return wisdom_text, wire_text, len(wisdom_results) + len(wire_results)

    def query(self, question):

        start = time.time()

        question_vector = self.embeddings.embed_query(question)

        wisdom, wire, sources = self.search(question_vector)

        chain = self.prompt | self.llm

        response = chain.invoke({
            "wisdom_context": wisdom,
            "wire_context": wire,
            "question": question
        })

        return {
            "answer": response.content,
            "sources_scanned": sources,
            "latency": time.time() - start
        }

    async def stream(self, question):

        question_vector = self.embeddings.embed_query(question)

        wisdom, wire, sources = self.search(question_vector)

        chain = self.prompt | self.llm_streaming

        async for chunk in chain.astream({
            "wisdom_context": wisdom,
            "wire_context": wire,
            "question": question
        }):
            if chunk.content:
                yield chunk.content

        yield {"done": True, "sources_scanned": sources}