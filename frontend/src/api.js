async function request(path, options = {}) {
  const resp = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const body = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    const detail = Array.isArray(body.detail)
      ? body.detail.map((d) => d.msg).join("; ")
      : body.detail;
    throw new Error(detail || `Request failed (${resp.status})`);
  }
  return body;
}

export const getHealth = () => request("/api/health");

export const analyzeBrief = (brief) =>
  request("/api/analyze", { method: "POST", body: JSON.stringify({ brief }) });

export const draftProposal = (payload) =>
  request("/api/proposal", { method: "POST", body: JSON.stringify(payload) });
