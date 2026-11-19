# Kavach — Agent Data-Firewall (District D7 / Phase 0)

An attachable PII & credential governance layer for AI agents handling Indian
personal data. This repo is **Phase 0**: the defensible core — the PII
taxonomy, the deterministic validator library, and the seed of the open
code-mixed (Hindi / Tamil / English) PII-leak benchmark.

> Design synthesis in progress. See the architecture and district plan for the
> full picture. Nothing here is production-hardened yet.

## What's in this phase

| Module | Purpose |
|---|---|
| `kavach/taxonomy.py` | The PII/credential registry: class, group, sensitivity (S1–S3), default action, and the validator each uses. |
| `kavach/validators.py` | Deterministic, zero-dependency validators — the high-precision first pass that keeps false positives low: Verhoeff (Aadhaar), Luhn (card), PAN, IFSC, GSTIN checksum, UPI VPA. |
| `tests/test_validators.py` | Unit tests (19, all green). |
| `kavach/ner.py` | Heuristic NER (gazetteer + trigger phrases) for names — the dependency-free default. |
| `kavach/ner_model.py` | Optional MuRIL-class transformer NER backend (names + addresses), with graceful fallback. |
| `benchmark/generate.py` | Synthetic code-mixed benchmark generator → labelled JSONL with ground-truth spans, in native-digit and number-word forms across Hi/Ta/En. |

## Why deterministic-first

Over-blocking breaks the host agent faster than a miss. Checksums and
structure carry precision for free, so the ML/NER layer (next phase, D2) only
handles the fuzzy, language-dependent residue — capping the false-positive rate.

## Quickstart

```bash
# run the tests
python -m unittest discover -s tests -p "test_*.py" -v

# generate benchmark examples
python benchmark/generate.py --n 8
python benchmark/generate.py --n 500 -o seed.jsonl
```

```python
from kavach import validators as v
v.is_aadhaar("2345 6789 0123")   # Verhoeff-checked
v.luhn_validate("4111111111111111")
v.is_gstin("27AAPFU0939F1ZV")
v.is_upi_vpa("ravi@okhdfcbank")
```

### Detection, with the optional MuRIL NER

```python
from kavach.detect import Detector

Detector().scan(text)                       # deterministic + heuristic NER (no deps)

# transformer NER backend (pip install "kavach[ner]"):
from kavach.ner_model import TransformerNER
Detector(ner_backend=TransformerNER()).scan(text)   # catches out-of-gazetteer names + addresses
```

The backend defaults to an ungated multilingual NER so it runs out of the box.
For best Indic-script coverage use MuRIL's `ai4bharat/IndicNER` — a **gated** HF
repo: request access, `huggingface-cli login`, then
`TransformerNER(model_id="ai4bharat/IndicNER")`. Run the model test with
`KAVACH_TEST_NER=1 python -m unittest discover -s tests -p "test_*.py"`.

## Roadmap (districts)

- **D7 Benchmark & validators** ← you are here
- **D2** Detection pipeline (normalize → validators → Indic NER → score)
- **D3/D4** Decision & policy · action & tokenization
- **D1** Interceptors (SDK, MCP proxy, gateway, voice)
- **D5** Audit & DPDP evidence · **D6** console · **D8** deployment

## Scope

v1 languages: **Hindi, Tamil, English** (including code-mixed). Architecture is
language-pluggable; adding a language is a data + model task, not a rewrite.
