import { useEffect, useState } from "react";
import { analyzeBrief, draftProposal, getHealth } from "./api.js";
import AnalysisEditor from "./AnalysisEditor.jsx";

const SAMPLE_BRIEF = `Hi! I run a small yoga studio called Sunrise Flow. We need a simple website with a class schedule, an instructor page, and a way for people to book a drop-in class and pay online. We'd like it live before January 1st. Budget is around $2,000. We use Instagram a lot so maybe show our feed?`;

export default function App() {
  const [health, setHealth] = useState(null);
  const [brief, setBrief] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [analysisRun, setAnalysisRun] = useState(0);
  const [details, setDetails] = useState({ freelancer_name: "", rate: "", tone: "professional" });
  const [proposal, setProposal] = useState("");
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealth({ status: "down" }));
  }, []);

  async function run(label, fn) {
    setBusy(label);
    setError("");
    try {
      await fn();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  }

  const onAnalyze = () =>
    run("Reading the brief…", async () => {
      const res = await analyzeBrief(brief);
      setAnalysis(res.analysis);
      setAnalysisRun((n) => n + 1);
      setProposal("");
    });

  const onDraft = () =>
    run("Drafting the proposal…", async () => {
      const res = await draftProposal({ brief, analysis, ...details });
      setProposal(res.markdown);
    });

  function download() {
    const blob = new Blob([proposal], { type: "text/markdown" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "proposal.md";
    a.click();
    URL.revokeObjectURL(a.href);
  }

  return (
    <main>
      <header>
        <h1>FreelanceFlow AI</h1>
        <p className="tagline">Turn client briefs into structured proposals with open-weight models running locally.</p>
        <HealthBadge health={health} />
      </header>

      <section className="card">
        <div className="row-between">
          <h2>1. Client brief</h2>
          <button className="link" onClick={() => setBrief(SAMPLE_BRIEF)}>Use sample brief</button>
        </div>
        <textarea
          rows={8}
          value={brief}
          onChange={(e) => setBrief(e.target.value)}
          placeholder="Paste the client's email or brief here…"
        />
        <button disabled={!!busy || brief.trim().length < 20} onClick={onAnalyze}>
          Extract requirements
        </button>
      </section>

      {analysis && (
        <section className="card">
          <h2>2. Review the scope</h2>
          <p className="hint">The model can miss or invent details. Fix anything wrong before drafting.</p>
          <AnalysisEditor key={analysisRun} value={analysis} onChange={setAnalysis} />

          <h3>Your details</h3>
          <div className="grid">
            <label>
              Your name
              <input value={details.freelancer_name} onChange={(e) => setDetails({ ...details, freelancer_name: e.target.value })} />
            </label>
            <label>
              Your rate (never guessed by the AI)
              <input placeholder="e.g. $1,800 fixed" value={details.rate} onChange={(e) => setDetails({ ...details, rate: e.target.value })} />
            </label>
            <label>
              Tone
              <select value={details.tone} onChange={(e) => setDetails({ ...details, tone: e.target.value })}>
                <option>professional</option>
                <option>friendly</option>
                <option>concise</option>
              </select>
            </label>
          </div>
          <button disabled={!!busy} onClick={onDraft}>Draft proposal</button>
        </section>
      )}

      {proposal && (
        <section className="card">
          <div className="row-between">
            <h2>3. Edit &amp; send</h2>
            <div className="actions">
              <button className="secondary" onClick={() => navigator.clipboard.writeText(proposal)}>Copy</button>
              <button className="secondary" onClick={download}>Download .md</button>
            </div>
          </div>
          <textarea rows={24} value={proposal} onChange={(e) => setProposal(e.target.value)} />
        </section>
      )}

      {busy && <div className="status">{busy} (local models can take a minute)</div>}
      {error && <div className="error">{error}</div>}

      <footer>AI output is a draft, not legal or financial advice. Review before sending.</footer>
    </main>
  );
}

function HealthBadge({ health }) {
  if (!health) return <span className="badge">Checking model…</span>;
  if (health.status === "ok") return <span className="badge ok">Model: {health.model}</span>;
  if (health.ollama_reachable === false || health.status === "down")
    return <span className="badge warn">Backend or Ollama not reachable</span>;
  return <span className="badge warn">Model {health.model} not pulled. Run: ollama pull {health.model}</span>;
}
