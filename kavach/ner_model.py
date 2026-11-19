"""Transformer NER backend (District D2) — the MuRIL swap-in.

Wraps a MuRIL-based token-classification model (default: ai4bharat/IndicNER,
which is MuRIL fine-tuned for Indian-language NER) to catch names and places
that the gazetteer cannot. Optional: if ``transformers`` / ``torch`` or the
model weights are unavailable, callers fall back to the heuristic NER, so the
pipeline always runs.

Enable with:  pip install "kavach[ner]"   (then the model downloads on first use)
"""
from __future__ import annotations

_PIPE = None
_TRIED = False
_ERROR: Exception | None = None

# Preferred model is MuRIL fine-tuned for Indic NER, but ai4bharat/IndicNER is a
# GATED HF repo (request access + `huggingface-cli login`). We default to an
# ungated multilingual NER so the backend runs out of the box; pass
# model_id="ai4bharat/IndicNER" once you have access for best Indic-script coverage.
INDIC_MODEL = "ai4bharat/IndicNER"          # MuRIL-based, gated
DEFAULT_MODEL = "Babelscape/wikineural-multilingual-ner"  # ungated multilingual NER

# CoNLL-style tags -> Kavach PII classes (MISC is ignored).
LABEL_MAP = {"PER": "NAME", "PERSON": "NAME", "LOC": "ADDRESS", "ORG": "ORG"}


def _load(model_id: str):
    global _PIPE, _TRIED, _ERROR
    if _TRIED:
        return _PIPE
    _TRIED = True
    try:
        from transformers import pipeline
        _PIPE = pipeline(
            "token-classification",
            model=model_id,
            aggregation_strategy="simple",
            framework="pt",   # force PyTorch (avoid TF/Keras-3 import path)
        )
    except Exception as exc:  # missing deps, offline, or load failure
        _ERROR = exc
        _PIPE = None
    return _PIPE


class TransformerNER:
    """MuRIL-backed NER with per-entity spans; empty list if unavailable."""

    def __init__(self, model_id: str = DEFAULT_MODEL, min_score: float = 0.5):
        self.model_id = model_id
        self.min_score = min_score

    @property
    def available(self) -> bool:
        return _load(self.model_id) is not None

    @property
    def error(self) -> Exception | None:
        return _ERROR

    def detect(self, text: str):
        """Return [(cls, value, start, end, confidence), ...]."""
        pipe = _load(self.model_id)
        if pipe is None:
            return []
        out = []
        for ent in pipe(text):
            group = str(ent.get("entity_group") or ent.get("entity") or "").split("-")[-1]
            cls = LABEL_MAP.get(group)
            score = float(ent.get("score", 0.0))
            if cls and cls != "ORG" and score >= self.min_score:
                s, e = int(ent["start"]), int(ent["end"])
                out.append((cls, text[s:e], s, e, round(score, 3)))
        return out
