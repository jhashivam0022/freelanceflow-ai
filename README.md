# FreelanceFlow AI

**Turn messy client briefs into structured, editable freelance proposals, using open-weight models that run on your own machine.**

> Built for the [Hacktoberfest Open-Source AI Challenge, Week 2: Side Hustle](https://dev.to/challenges/hacktoberfest-week2-2026-10-12).

Freelancers spend unpaid hours turning vague client emails into scoped proposals: working out what the client actually wants, splitting it into deliverables and milestones, and writing it up professionally. FreelanceFlow AI does the first draft of that work locally with [Ollama](https://ollama.com/), so confidential client briefs never have to leave your laptop.

## How it works

```
Client brief ──▶ 1. Extract ──▶ 2. Review & edit ──▶ 3. Draft proposal ──▶ Copy / download .md
                 (JSON schema)    (you fix the scope)   (Markdown)
```

1. **Extract.** The brief goes to a local model with a strict JSON schema (Ollama structured outputs). You get back the project title, summary, requirements, deliverables, milestones, deadline, budget, assumptions, and questions to ask the client.
2. **Review.** Every extracted field can be edited. Small models miss things and sometimes make things up, so you confirm the scope before anything gets written.
3. **Draft.** The reviewed scope, your name, your rate, and a tone are used to write a Markdown proposal you can edit, copy, or download.

**You stay in control of pricing.** The model is told never to invent prices. If you don't enter a rate, the proposal uses a `[Your rate]` placeholder.

## Tech stack

| Layer | Choice |
| --- | --- |
| Frontend | React 19 + Vite |
| Backend | Python, FastAPI, Pydantic |
| Model runtime | [Ollama](https://ollama.com/) (local inference, structured JSON output) |
| Models | Any Ollama chat model. Tested with `gemma:2b`; `qwen2.5:7b` or `gemma3:4b` recommended for better extraction |

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 20+
- [Ollama](https://ollama.com/download) 0.5 or newer (needed for JSON-schema structured outputs)

### 1. Pull a model

```bash
ollama pull qwen2.5:7b
```

On low-memory machines, `gemma:2b` works, but expect to correct more of the extracted fields.

### 2. Run the backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env        # then set OLLAMA_MODEL to the model you pulled
uvicorn app.main:app --reload --port 8000
```

Open http://127.0.0.1:8000/api/health to check that the backend can reach Ollama and your model.

### 3. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The Vite dev server forwards `/api` requests to the backend.

### Configuration

Set these in `backend/.env`:

| Variable | Default | Purpose |
| --- | --- | --- |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Ollama server URL (can point at a remote GPU box) |
| `OLLAMA_MODEL` | `qwen2.5:7b` | Model used for both extraction and drafting |
| `OLLAMA_TIMEOUT` | `180` | Seconds to wait for a response |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Allowed frontend origins |

## API

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/health` | Checks that Ollama is reachable and the model is pulled |
| `POST` | `/api/analyze` | `{ brief }` → structured `analysis` |
| `POST` | `/api/proposal` | `{ brief, analysis, freelancer_name?, rate?, tone? }` → `{ markdown }` |

Interactive docs are at http://127.0.0.1:8000/docs.

## Project structure

```
backend/
  app/
    main.py       FastAPI routes
    llm.py        Ollama client (chat + JSON-schema output)
    prompts.py    System prompts for extraction and drafting
    services.py   Brief analysis and proposal pipeline
    schemas.py    Pydantic models (also used as the model's JSON schema)
  tests/          API tests with a fake LLM (no Ollama needed)
frontend/
  src/
    App.jsx            Three-step brief → review → proposal flow
    AnalysisEditor.jsx Editable view of the extracted scope
```

## Running tests

```bash
cd backend
pytest
```

The tests replace the model with a fake, so they run without Ollama.

## Why open-weight models?

- **Privacy.** Client briefs often contain budgets, unreleased product details, and names. With Ollama running locally, the brief goes from your browser to your backend to your own model and no further.
- **No per-token bill.** A side-hustle tool shouldn't cost you money every time you quote a job.
- **Swappable.** Changing `OLLAMA_MODEL` switches between Qwen, Gemma, Llama, and other models without code changes.

Local execution doesn't guarantee privacy on its own. If you point `OLLAMA_BASE_URL` at a remote server, your brief is sent to that server.

## Roadmap

- [x] Client brief input
- [x] Structured requirement extraction (JSON-schema constrained)
- [x] Editable scope review
- [x] Proposal draft with user-controlled pricing
- [x] Validation and error handling for model and runtime failures
- [ ] Streaming responses for faster feedback
- [ ] Save and reload past proposals
- [ ] Export to PDF / DOCX
- [ ] Deliverable-to-invoice drafts and payment reminder emails
- [ ] One-click deploy (Render / DigitalOcean)

## Contributing

Issues and pull requests are welcome. Please open an issue to discuss larger changes first, and run `pytest` before submitting.

## Responsible use

AI-generated proposals are drafts, not legal, financial, or contractual advice. Review scope, prices, deadlines, and terms before you send anything to a client.

## License

No license has been chosen yet. Until one is added, all rights are reserved by the author.
