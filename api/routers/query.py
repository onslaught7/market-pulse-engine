"""
The Interface: API endpoints.
"""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel

from services.rag_engine import RAGEngine


router = APIRouter()

engine = RAGEngine()


class QueryRequest(BaseModel):
    question: str


@router.post("/query")
def query_marketpulse(request: QueryRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = engine.query(question)

    return {
        "question": question,
        "answer": result["answer"],
        "sources_scanned": result["sources_scanned"]
    }


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):

    await ws.accept()

    try:
        while True:

            data = await ws.receive_text()
            payload = json.loads(data)

            question = payload.get("question", "").strip()

            if not question:
                await ws.send_json({
                    "type": "error",
                    "detail": "Question cannot be empty."
                })
                continue

            async for chunk in engine.stream(question):

                if isinstance(chunk, dict):
                    await ws.send_json({"type": "done", **chunk})

                else:
                    await ws.send_json({
                        "type": "token",
                        "content": chunk
                    })

    except WebSocketDisconnect:
        pass