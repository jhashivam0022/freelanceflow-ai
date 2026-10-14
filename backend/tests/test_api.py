import pytest
from fastapi.testclient import TestClient

from app.llm import LLMError
from app.main import app, get_llm

BRIEF = "We need a landing page for our bakery with an online order form. Launch by Nov 30."

ANALYSIS = {
    "project_title": "Bakery landing page",
    "client_name": "",
    "summary": "A landing page with an order form.",
    "requirements": ["Online order form"],
    "deliverables": ["Landing page"],
    "milestones": [
        {"title": "Build", "description": "", "deliverables": ["Landing page"], "estimated_duration": "1 week"}
    ],
    "deadline": "Nov 30",
    "budget": "",
    "tech_stack": [],
    "assumptions": [],
    "open_questions": ["Which payment provider?"],
}


class FakeLLM:
    model = "fake:1b"

    def __init__(self, chat_reply="", json_reply=None, error=None):
        self.chat_reply = chat_reply
        self.json_reply = json_reply
        self.error = error
        self.calls = []

    async def chat(self, messages, **kwargs):
        self.calls.append(messages)
        if self.error:
            raise self.error
        return self.chat_reply

    async def chat_json(self, messages, json_schema):
        self.calls.append(messages)
        if self.error:
            raise self.error
        return self.json_reply

    async def health(self):
        return True, True


@pytest.fixture
def client_with():
    def make(fake):
        app.dependency_overrides[get_llm] = lambda: fake
        return TestClient(app)

    yield make
    app.dependency_overrides.clear()


def test_health(client_with):
    resp = client_with(FakeLLM()).get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_analyze_returns_structured_brief(client_with):
    resp = client_with(FakeLLM(json_reply=ANALYSIS)).post("/api/analyze", json={"brief": BRIEF})
    assert resp.status_code == 200
    body = resp.json()
    assert body["analysis"]["project_title"] == "Bakery landing page"
    assert body["model"] == "fake:1b"


def test_analyze_rejects_short_brief(client_with):
    resp = client_with(FakeLLM()).post("/api/analyze", json={"brief": "too short"})
    assert resp.status_code == 422


def test_analyze_invalid_model_output_is_502(client_with):
    resp = client_with(FakeLLM(json_reply={"nope": 1})).post("/api/analyze", json={"brief": BRIEF})
    assert resp.status_code == 502


def test_llm_unreachable_is_502(client_with):
    fake = FakeLLM(error=LLMError("Could not reach Ollama"))
    resp = client_with(fake).post("/api/analyze", json={"brief": BRIEF})
    assert resp.status_code == 502
    assert "Ollama" in resp.json()["detail"]


def test_proposal_strips_code_fence_and_passes_rate(client_with):
    fake = FakeLLM(chat_reply="```markdown\n# Proposal\nHello\n```")
    resp = client_with(fake).post(
        "/api/proposal",
        json={"brief": BRIEF, "analysis": ANALYSIS, "rate": "$1,200 fixed"},
    )
    assert resp.status_code == 200
    assert resp.json()["markdown"] == "# Proposal\nHello"
    prompt = fake.calls[0][-1]["content"]
    assert "$1,200 fixed" in prompt
    assert "Nov 30" in prompt


def test_proposal_without_rate_uses_placeholder_instruction(client_with):
    fake = FakeLLM(chat_reply="# Proposal")
    client_with(fake).post("/api/proposal", json={"brief": BRIEF, "analysis": ANALYSIS})
    assert "[Your rate]" in fake.calls[0][-1]["content"]
