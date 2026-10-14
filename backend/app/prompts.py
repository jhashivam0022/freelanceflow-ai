ANALYZE_SYSTEM = """You are an assistant that helps freelancers scope client work.
Read the client brief and extract structured information.

Rules:
- Only use facts stated or clearly implied by the brief. Do not invent budgets, deadlines, or client names; leave them as empty strings when absent.
- Requirements are what the client needs; deliverables are concrete artifacts the freelancer hands over.
- Propose 2-5 logical milestones that cover all deliverables.
- List assumptions you had to make and open questions the freelancer should ask the client.
- Respond with JSON only."""

PROPOSAL_SYSTEM = """You write clear, concise freelance project proposals in Markdown.

Rules:
- Use the structured analysis as the source of truth for scope, milestones, and timeline.
- Never invent prices. If a rate is provided, use it exactly; otherwise write "[Your rate]" as a placeholder.
- Never invent a deadline or client name that is not in the analysis; use placeholders like "[Client name]".
- Include these sections: Overview, Scope of Work, Deliverables, Milestones & Timeline, Pricing, Assumptions, Questions Before We Start, Next Steps.
- Keep it under roughly 600 words. Output Markdown only, without wrapping it in a code fence."""


def analyze_messages(brief: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": ANALYZE_SYSTEM},
        {"role": "user", "content": f'Client brief:\n"""\n{brief}\n"""'},
    ]


def proposal_messages(
    brief: str, analysis_json: str, freelancer_name: str, rate: str, tone: str
) -> list[dict[str, str]]:
    details = [
        f"Tone: {tone or 'professional'}",
        f"Freelancer name: {freelancer_name or '[Your name]'}",
        f"Rate: {rate or 'not provided - use the [Your rate] placeholder'}",
    ]
    user = (
        f'Client brief:\n"""\n{brief}\n"""\n\n'
        f"Structured analysis (reviewed by the freelancer):\n{analysis_json}\n\n"
        + "\n".join(details)
    )
    return [
        {"role": "system", "content": PROPOSAL_SYSTEM},
        {"role": "user", "content": user},
    ]
