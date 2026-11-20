# Kavach — one-page pitch

**The agent data-firewall for India.** An inline layer that stops AI agents from
leaking Aadhaar, UPI, cards and health data — in code-mixed Hindi/Tamil/English —
and auto-generates DPDP audit evidence.

### Problem
AI agents act by calling tools (CRMs, SMS/voice gateways, payment, 3rd-party
APIs) with arguments that carry user PII. The leak happens in the **tool call**,
which output-only guardrails never inspect. In India this is now a hard
obligation, and the data is in languages Western tools mis-handle.

### Why now (forcing functions)
- **DPDP Act + Rules 2025** — Rule 6 "reasonable security safeguards" (masking,
  access control, logging) bite ~2027; penalties to ₹250 crore.
- **RBI FREE-AI** (Aug 2025) — AI oversight + incident reporting for regulated
  entities; CERT-In 6-hour breach rule stacks on top.
- Agentic AI is in production exactly where PII is densest: **BFSI collections /
  KYC and Indian-language voice/CX** (Bajaj Finance ~20M AI calls/quarter;
  Airtel 4M+ AI voice interactions/day).

### Product
Detect → decide → act → prove, attachable in one line:
- **Detects** 11 PII classes, deterministic-first (Verhoeff/Luhn/GSTIN/IFSC/UPI)
  + MuRIL NER, including spoken/number-word and code-mixed forms.
- **Decides** by destination trust (secrets never egress; mask/tokenize/block).
- **Proves** via a tamper-evident, hash-chained audit with a DPDP report.
- **Attaches** via SDK / LangChain / MCP / OpenAI wrappers; SaaS, VPC or
  on-prem/air-gap Docker.

### Wedge & moat
Global agent-DLP has the mechanism but **zero Indic/DPDP localisation**;
Indian privacy tools do consent/discovery, not agent-runtime tool-call scanning.
The moat is (1) a **labelled code-mixed Indian-PII benchmark/corpus** (the
hard, non-copyable asset), (2) DPDP/RBI compliance trust, (3) critical-path
lock-in. The open benchmark is the standard others must cite.

### Market (directional)
Agent-security is a forming, fast-growing category (sub-$billion India slice
today, ~40% CAGR); the realistic frame is **global-from-India** using DPDP as
the timing wedge (the Securiti→Veeam $1.7B path), with acquisition by a
security/data platform as the base-case outcome. Note: enterprise-sales heavy;
demand today is anticipatory (no public India AI-PII incident yet).

### Status
Working vertical slice across all build districts: 11-class detection
(99.7%/99.7% on synthetic data), decision engine, SDK + 3 framework
integrations, tamper-evident audit, admin console, Docker/on-prem — 52 tests.
**Remaining:** production vault (KMS/HSM), hardened serving, and real
Tamil/Hindi-script quality via IndicNER access or pilot data.

### Ask
Design partners in NBFC collections / Indian voice-AI to supply real transcripts
(under DPA) and validate false-positive rates in production.

> Figures are drawn from market research and are directional where
> vendor/aggregator-sourced; numbers above are on synthetic data.
