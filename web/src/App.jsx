import React, { useEffect, useState } from "react";

const api = (p, opts) => fetch(p, opts).then((r) => r.json());

const ACTION_COLOR = {
  allow: "allow", mask: "mask", tokenize: "tokenize", escalate: "escalate", block: "block",
};

const SAMPLE =
  "Customer Priya from Chennai, Aadhaar 234567890124, UPI ravi@okhdfcbank, card 4111111111111111, OTP 123456, diagnosis diabetes.";

export default function App() {
  const [meta, setMeta] = useState(null);
  const [text, setText] = useState(SAMPLE);
  const [dest, setDest] = useState("crm_external_api");
  const [result, setResult] = useState(null);
  const [audit, setAudit] = useState(null);
  const [busy, setBusy] = useState(false);

  const loadAudit = () => api("/api/audit").then(setAudit);
  useEffect(() => {
    api("/api/meta").then((m) => { setMeta(m); if (m.destinations?.[0]) setDest(m.destinations[0].name); });
    loadAudit();
  }, []);

  const guard = async () => {
    setBusy(true);
    const r = await api("/api/scan", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, destination: dest }),
    });
    setResult(r);
    await loadAudit();
    setBusy(false);
  };

  const trustOf = (name) => meta?.destinations?.find((d) => d.name === name)?.trust ?? "unknown";

  return (
    <div className="app">
      <header>
        <div className="logo">K</div>
        <div>
          <h1>Kavach</h1>
          <div className="muted">agent data-firewall · DPDP · code-mixed Hi/Ta/En</div>
        </div>
        <a className="repo" href="https://github.com/hxshxnsivx-hub/S.H.I.E.L.D-101" target="_blank" rel="noreferrer">GitHub ↗</a>
      </header>

      <main>
        <section className="card">
          <h2>Outbound payload → tool</h2>
          <textarea value={text} onChange={(e) => setText(e.target.value)} spellCheck={false} />
          <div className="row">
            <select value={dest} onChange={(e) => setDest(e.target.value)}>
              {meta?.destinations?.map((d) => (
                <option key={d.name} value={d.name}>{d.name} · {d.trust}</option>
              ))}
            </select>
            <button className="go" onClick={guard} disabled={busy}>{busy ? "…" : "Guard →"}</button>
            <span className="muted">trust: <b className={`trust t-${trustOf(dest)}`}>{trustOf(dest)}</b></span>
          </div>

          {result && (
            <>
              <h2 className="mt">Result <span className={`status s-${result.status}`}>{result.status}</span>
                <span className="muted lat"> {result.latency_ms} ms</span></h2>
              <div className="io"><div className="iolbl">in</div>{text}</div>
              <div className="io out"><div className="iolbl">out · sent to tool</div>{result.sanitized}</div>
              <div className="chips">
                {result.decisions.length === 0 && <div className="muted">no PII detected</div>}
                {result.decisions.map((d, i) => (
                  <div className="chip" key={i}>
                    <span className={`act a-${ACTION_COLOR[d.action]}`}>{d.action}</span>
                    <span className="cls">{d.cls}</span>
                    <span className="reason">{d.reason}</span>
                    <span className="conf"><span className="bar" style={{ width: `${d.confidence * 100}%` }} />{d.confidence}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </section>

        <section className="card">
          <h2>Audit &amp; DPDP evidence</h2>
          <div className="stats">
            <Stat n={audit?.report.events ?? 0} label="events" />
            <Stat n={audit?.report.reportable_events ?? 0} label="reportable" />
            <Stat n={audit?.report.chain_intact ? "✓" : "✗"} label="chain" good={audit?.report.chain_intact} />
          </div>
          <h2>Recent decisions</h2>
          <table>
            <thead><tr><th>#</th><th>dest</th><th>status</th><th>PII</th><th>hash</th></tr></thead>
            <tbody>
              {audit?.recent?.map((e) => (
                <tr key={e.seq}>
                  <td>{e.seq}</td><td>{e.destination}</td>
                  <td><span className={`status s-${e.status}`}>{e.status}</span></td>
                  <td>{e.entities}</td><td className="muted mono">{e.hash}</td>
                </tr>
              ))}
              {!audit?.recent?.length && <tr><td colSpan={5} className="muted">no events yet — guard a payload</td></tr>}
            </tbody>
          </table>
          <h2>Policy / registry</h2>
          <div className="muted">{meta?.classes?.length ?? 0} PII classes · {[...new Set((meta?.classes ?? []).map((c) => c.group))].join(" · ")}</div>
        </section>
      </main>
    </div>
  );
}

function Stat({ n, label, good }) {
  return (
    <div className="stat">
      <b className={good === undefined ? "" : good ? "ok" : "bad"}>{n}</b>
      <span>{label}</span>
    </div>
  );
}
