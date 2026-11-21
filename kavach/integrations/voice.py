"""Voice-pipeline integration (District D1).

Voice agents (collections, KYC, support in Hindi/Tamil) are the densest PII
surface in India. Kavach plugs in at two points of a voice pipeline:

  STT (speech-to-text) --guard_stt--> agent/tools   (don't let a spoken Aadhaar
                                                      reach an external tool)
  agent --guard_tts--> TTS (text-to-speech)          (never read a card/OTP aloud)
"""
from __future__ import annotations


def guard_stt(kav, transcript: str, destination: str) -> str:
    """Sanitise what the caller *said* before it goes to a tool/LLM."""
    return kav.guard(transcript, destination).sanitized_text


def guard_tts(kav, text: str, destination: str = "caller") -> str:
    """Sanitise what the bot is about to *say* — secrets are never spoken."""
    return kav.guard(text, destination).sanitized_text
