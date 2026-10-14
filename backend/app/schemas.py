from pydantic import BaseModel, Field

MAX_BRIEF_CHARS = 20_000


class Milestone(BaseModel):
    title: str
    description: str = ""
    deliverables: list[str] = Field(default_factory=list)
    estimated_duration: str = Field(
        default="", description="Rough duration, e.g. '1 week'. Empty if unknown."
    )


class BriefAnalysis(BaseModel):
    """Structured information extracted from a client brief."""

    project_title: str
    client_name: str = Field(default="", description="Empty if not mentioned.")
    summary: str
    requirements: list[str] = Field(default_factory=list)
    deliverables: list[str] = Field(default_factory=list)
    milestones: list[Milestone] = Field(default_factory=list)
    deadline: str = Field(default="", description="As stated in the brief, or empty.")
    budget: str = Field(default="", description="As stated in the brief, or empty.")
    tech_stack: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(
        default_factory=list,
        description="Ambiguities the freelancer should clarify with the client.",
    )


class AnalyzeRequest(BaseModel):
    brief: str = Field(min_length=20, max_length=MAX_BRIEF_CHARS)


class AnalyzeResponse(BaseModel):
    analysis: BriefAnalysis
    model: str


class ProposalRequest(BaseModel):
    brief: str = Field(min_length=20, max_length=MAX_BRIEF_CHARS)
    analysis: BriefAnalysis
    freelancer_name: str = Field(default="", max_length=200)
    rate: str = Field(
        default="",
        max_length=200,
        description="Pricing the freelancer chose, e.g. '$4,500 fixed'. Never invented by the model.",
    )
    tone: str = Field(default="professional", max_length=50)


class ProposalResponse(BaseModel):
    markdown: str
    model: str


class HealthResponse(BaseModel):
    status: str
    ollama_reachable: bool
    model: str
    model_available: bool
