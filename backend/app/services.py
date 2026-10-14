import re

from pydantic import ValidationError

from .llm import LLMError, OllamaClient
from .prompts import analyze_messages, proposal_messages
from .schemas import BriefAnalysis

_FENCE = re.compile(r"^```(?:markdown|md)?\s*\n(.*)\n```\s*$", re.DOTALL)


async def analyze_brief(llm: OllamaClient, brief: str) -> BriefAnalysis:
    data = await llm.chat_json(analyze_messages(brief), BriefAnalysis.model_json_schema())
    try:
        return BriefAnalysis.model_validate(data)
    except ValidationError as exc:
        raise LLMError("Model output did not match the expected structure") from exc


async def draft_proposal(
    llm: OllamaClient,
    brief: str,
    analysis: BriefAnalysis,
    freelancer_name: str = "",
    rate: str = "",
    tone: str = "professional",
) -> str:
    messages = proposal_messages(
        brief, analysis.model_dump_json(indent=2), freelancer_name, rate, tone
    )
    text = (await llm.chat(messages, temperature=0.4)).strip()
    # Small models sometimes wrap the whole answer in a code fence.
    match = _FENCE.match(text)
    if match:
        text = match.group(1).strip()
    if not text:
        raise LLMError("Model returned an empty proposal")
    return text
