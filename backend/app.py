from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import PromptQueryRequest, PromptQueryResponse
from .sql_service import SQLService

app = FastAPI(title="Prompt-to-SQL Dashboard", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

service: Optional[SQLService] = None


def get_service() -> SQLService:
    global service
    if service is None:
        try:
            service = SQLService()
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
    return service


@app.post("/query", response_model=PromptQueryResponse)
async def run_prompt_query(payload: PromptQueryRequest) -> PromptQueryResponse:
    question = payload.natural_language.strip()
    if len(question) < 5:
        raise HTTPException(status_code=400, detail="Query too short")

    svc = get_service()
    return svc.prompt_and_query(question)


@app.get("/schema")
async def schema_snapshot():
    svc = get_service()
    return {"schema": svc.describe_schema()}


@app.get("/")
async def root():
    return {
        "message": "POST /query with natural_language to convert into SQL and run against sales.db",
        "prompt": "Convert this English query into valid SQL for the following schema...",
    }
