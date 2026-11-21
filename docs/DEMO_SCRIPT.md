# Kavach — 90-second demo script & storyboard

Goal: a hiring manager / founder *gets it* in 90 seconds — an AI agent leaks
private data, you add Kavach in one line, the leak stops, and it's provable.

Setup before recording:
- Terminal open in the repo; `python -m kavach.console.server` running in a 2nd tab.
- Browser at `http://localhost:8765` (the console) and the landing page.
- Font size up; dark theme; hide secrets/other tabs.

Total ~90s. Keep narration tight; let the screen do the work.

---

### Scene 1 — The hook (0:00–0:10)
- **On screen:** landing page hero ("Stop your AI agents from leaking private data").
- **Voiceover:** "AI agents are going into banks and call-centres. The problem: they leak people's private data to third-party tools — and in India, that's now illegal."
- **Text overlay:** *Aadhaar · UPI · cards · health*

### Scene 2 — Show the leak (0:10–0:30)
- **On screen:** terminal — run the agent WITHOUT Kavach.
  ```bash
  python examples/agent_integration.py
  ```
  Scroll to the "RAW tool" lines.
- **Point at:** `EXTERNAL CRM receives: Aadhaar 234567890124, card 4111111111111111`.
- **Voiceover:** "Here's an agent calling an external CRM. Look — the real Aadhaar and card number go straight out. No guardrail catches this, because it happens inside the tool call."

### Scene 3 — Attach Kavach, one line (0:30–0:50)
- **On screen:** editor — show the one line.
  ```python
  agent = create_react_agent(llm, guard_tools(kav, tools))
  ```
- Back to terminal, scroll to the "GUARDED tool" lines of the same run.
- **Point at:** `Aadhaar <AADHAAR:tok0002>, card <CARD_PAN:tok0001>, OTP [BLOCKED:OTP]`.
- **Voiceover:** "Add Kavach with one wrapper. Same agent — now the CRM only sees tokens. The card is tokenised, the OTP is blocked outright. Nothing private left the building."

### Scene 4 — The console + proof (0:50–1:10)
- **On screen:** the browser console. Paste a payload, pick `crm_external_api`, click **Guard**.
- **Point at:** the colour-coded decision cards (ALLOW / MASK / TOKENIZE / BLOCK) and the **Audit panel** — events, *reportable*, **chain ✓**.
- **Voiceover:** "Every decision is logged in a tamper-proof trail — that's your DPDP evidence, generated automatically. And it reads India's languages: here's a card dictated in Tamil, still caught."
- **Optional:** switch destination to `core_banking` (trusted) → data passes, but OTP still blocked. "Trusted systems get the data; secrets never leave, ever."

### Scene 5 — Close (1:10–1:30)
- **On screen:** quick montage — the integration list (LangChain · MCP · OpenAI · voice), then the GitHub repo (green CI badge, README).
- **Voiceover:** "Attaches to LangChain, MCP, OpenAI or voice agents. Runs on-prem or air-gapped. Open source, tested, ready."
- **End card:** `Kavach — the agent data-firewall` + `github.com/hxshxnsivx-hub/S.H.I.E.L.D-101`

---

## 30-second cut (for social)
1. (0–6s) Hero line + "AI agents leak private data."
2. (6–16s) RAW run: Aadhaar + card leak to the CRM.
3. (16–26s) One line added → tokens + `[BLOCKED:OTP]`.
4. (26–30s) End card + GitHub.

## Recording tips
- Pre-run commands so output appears instantly (no waiting on the model-NER load).
- Zoom the terminal to ~18pt; highlight the leaked values with your cursor.
- Keep it silent-captioned too (many watch muted) — overlay the key phrases.
- Two takes: one narrated, one captions-only.
