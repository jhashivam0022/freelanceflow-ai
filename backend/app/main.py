from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings, get_settings
from .llm import LLMError, OllamaClient
from .schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    HealthResponse,
    ProposalRequest,
    ProposalResponse,
)
from .services import analyze_brief, draft_proposal

app = FastAPI(title="FreelanceFlow AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origin_list,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def get_llm(settings: Annotated[Settings, Depends(get_settings)]) -> OllamaClient:
    return OllamaClient(settings.ollama_base_url, settings.ollama_model, settings.ollama_timeout)


LLM = Annotated[OllamaClient, Depends(get_llm)]


@app.get("/api/health", response_model=HealthResponse)
async def health(llm: LLM) -> HealthResponse:
    reachable, available = await llm.health()
    return HealthResponse(
        status="ok" if reachable and available else "degraded",
        ollama_reachable=reachable,
        model=llm.model,
        model_available=available,
    )


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest, llm: LLM) -> AnalyzeResponse:
    try:
        analysis = await analyze_brief(llm, req.brief)
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return AnalyzeResponse(analysis=analysis, model=llm.model)


@app.post("/api/proposal", response_model=ProposalResponse)
async def proposal(req: ProposalRequest, llm: LLM) -> ProposalResponse:
    try:
        markdown = await draft_proposal(
            llm, req.brief, req.analysis, req.freelancer_name, req.rate, req.tone
        )
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return ProposalResponse(markdown=markdown, model=llm.model)
