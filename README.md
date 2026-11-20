# Kavach — the agent data-firewall

**Stop your AI agents from leaking Aadhaar, UPI, cards and health data — in
Indian languages — and generate your DPDP evidence automatically.**

Kavach is a runtime layer that inspects every outbound tool call an AI agent
makes, detects credentials and PII (including **code-mixed Hindi / Tamil /
English** and spoken number-words), then **allows / masks / tokenizes / blocks /
escalates** per destination trust, and records a tamper-evident audit trail —
without you rebuilding the agent.

> Status: working vertical slice across all eight build "districts" (detection →
> decision → interceptors → audit → console → deployment). Validated on
> **synthetic data**; production hardening (KMS/HSM vault, real-ASGI serving) and
> real Tamil/Hindi-script quality (IndicNER access / pilot data) are the
> remaining work. See [Status](#status).

---

## Why

An AI agent's risky moment is calling a tool — a CRM, SMS gateway, payment or
3rd-party API — with **arguments that carry the user's PII**. Output-only
guardrails miss this; the leak happens in the tool call, before any reply.
Global agent-DLP tools don't understand Indian identifiers or code-mixed speech.
DPDP (Rule 6) and RBI's FREE-AI framework make preventing and *proving* this a
2026–27 obligation. Kavach is that control, India-first.

## Quickstart

```bash
python -m unittest discover -s tests -p "test_*.py"   # 52 tests
python scripts/demo.py            # engine: same payload, untrusted vs trusted
python -m kavach.console.server   # admin console at http://localhost:8765
```

Guard an agent's tool call (the core API — the shape of MCP / function-calling):

```python
from kavach import Kavach, Trust

kav = Kavach(trust={"crm_api": Trust.UNTRUSTED, "core_banking": Trust.TRUSTED})

safe = kav.guard_arguments("crm_api", {
    "summary": "Aadhaar 2345-6789-0124, card 4111 1111 1111 1111",
    "amount": 500,
}).sanitized
# -> summary tokenised, amount untouched; nothing raw leaves
```

### Attach to a framework (one wrapper each)

```python
# LangChain — hand the agent guarded tools
from kavach.integrations.langchain import guard_tools
agent = create_react_agent(llm, guard_tools(kav, tools))

# MCP — wrap the server's dispatcher
from kavach.integrations.mcp import guard_call_tool
call_tool = guard_call_tool(kav, call_tool)

# OpenAI function-calling — guard the tool call before running it
from kavach.integrations.openai import guard_tool_call
name, safe_args, _ = guard_tool_call(kav, tool_call)
```

Runnable: `examples/agent_integration.py`, `examples/langchain_integration.py`,
`examples/mcp_integration.py`, `examples/openai_integration.py`.

## How it works

```
tool call (name, arguments with PII)
        │
   ┌────▼───────────────────────────── D1 interceptor (SDK / LangChain / MCP / OpenAI)
   │  D2 detect: normalize → validators (Verhoeff/Luhn/IFSC/GSTIN/VPA)
   │            → Indic NER (MuRIL) ∪ gazetteer → confidence
   │  D3 decide: sensitivity × destination-trust × policy
   │            → allow / mask / tokenize / block / escalate
   │  D4 act   : mask · format-preserving reversible token vault
   │  D5 audit : hash-chained evidence (no raw PII) + DPDP report
   └────▼─────────────────────────────
 clean payload → external tool        D6 console · D8 Docker/on-prem
```

- **Deterministic-first:** checksums carry precision (Aadhaar via Verhoeff, cards
  via Luhn, GSTIN/IFSC/PAN/UPI), so the ML/NER layer only handles the fuzzy,
  language-dependent residue — keeping false positives low.
- **11 PII classes** across government, financial, contact, biometric and health.
- On the synthetic benchmark: **99.7% recall / 99.7% precision** with the NER on,
  sub-millisecond per call (NER off).

## Layout

| Path | District | What |
|---|---|---|
| `kavach/validators.py`, `benchmark/` | D7 | validators + synthetic code-mixed benchmark |
| `kavach/detect.py`, `normalize.py`, `ner*.py`, `gazetteers.py` | D2 | detection pipeline |
| `kavach/policy.py`, `engine.py`, `vault.py` | D3/D4 | decision engine + token vault |
| `kavach/sdk.py`, `kavach/integrations/` | D1 | SDK + framework wrappers |
| `kavach/audit.py` | D5 | tamper-evident audit + DPDP report |
| `kavach/console/` | D6 | admin console (stdlib web UI) |
| `Dockerfile`, `kavach/config.py`, `DEPLOY.md` | D8 | deployment |

## Deployment

See [`DEPLOY.md`](DEPLOY.md). Core is stdlib-only (air-gap safe); the optional
MuRIL NER is the only networked piece. `docker build . && docker run -p 8765:8765 kavach`.

## Status

Built: D7, D2, D3, D1, D5, D6, D8 + a D4 slice. **Remaining / honest caveats:**
numbers are on synthetic data; the gazetteer flatters known names/cities while
the real transformer NER is the honest generaliser; true Tamil/Hindi-*script*
quality needs IndicNER access (gated) or pilot data; the production vault
(KMS/HSM) and a hardened ASGI server are not done. See `kavach-districts` plan.

## License

Apache-2.0.
