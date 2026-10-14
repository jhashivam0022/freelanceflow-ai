const TEXT_FIELDS = [
  ["project_title", "Project title"],
  ["client_name", "Client"],
  ["deadline", "Deadline"],
  ["budget", "Budget (from brief)"],
];

const LIST_FIELDS = [
  ["requirements", "Requirements"],
  ["deliverables", "Deliverables"],
  ["tech_stack", "Tech stack"],
  ["assumptions", "Assumptions"],
  ["open_questions", "Questions for the client"],
];

// Lists are edited as one item per line.
const toLines = (items) => items.join("\n");
const fromLines = (text) => text.split("\n").map((s) => s.trim()).filter(Boolean);

export default function AnalysisEditor({ value, onChange }) {
  const set = (key, v) => onChange({ ...value, [key]: v });

  const setMilestone = (i, patch) =>
    set("milestones", value.milestones.map((m, j) => (j === i ? { ...m, ...patch } : m)));

  return (
    <div className="analysis">
      <div className="grid">
        {TEXT_FIELDS.map(([key, label]) => (
          <label key={key}>
            {label}
            <input value={value[key]} onChange={(e) => set(key, e.target.value)} />
          </label>
        ))}
      </div>

      <label>
        Summary
        <textarea rows={3} value={value.summary} onChange={(e) => set("summary", e.target.value)} />
      </label>

      <div className="grid">
        {LIST_FIELDS.map(([key, label]) => (
          <label key={key}>
            {label} <small>(one per line)</small>
            <textarea rows={4} defaultValue={toLines(value[key])} onBlur={(e) => set(key, fromLines(e.target.value))} />
          </label>
        ))}
      </div>

      <h3>Milestones</h3>
      {value.milestones.map((m, i) => (
        <div className="milestone" key={i}>
          <input value={m.title} onChange={(e) => setMilestone(i, { title: e.target.value })} placeholder="Title" />
          <input value={m.estimated_duration} onChange={(e) => setMilestone(i, { estimated_duration: e.target.value })} placeholder="Duration" />
          <textarea rows={2} value={m.description} onChange={(e) => setMilestone(i, { description: e.target.value })} placeholder="Description" />
          <button className="link danger" onClick={() => set("milestones", value.milestones.filter((_, j) => j !== i))}>
            Remove
          </button>
        </div>
      ))}
      <button
        className="link"
        onClick={() =>
          set("milestones", [...value.milestones, { title: "", description: "", deliverables: [], estimated_duration: "" }])
        }
      >
        + Add milestone
      </button>
    </div>
  );
}
