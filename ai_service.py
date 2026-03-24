"""OpenAI integration for Tradova with automatic fallback to templates.

If OPENAI_API_KEY is set, language-generation calls go to gpt-4o-mini.
If the key is missing or the API fails, every function returns a usable
fallback so the demo never breaks.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

# ── Client init (safe — no crash if key is absent) ─────────────────────────
_api_key = os.environ.get("OPENAI_API_KEY")
_client = None

if _api_key:
    try:
        from openai import OpenAI
        _client = OpenAI(api_key=_api_key)
        logger.info("OpenAI client initialized")
    except Exception as exc:
        logger.warning("Could not initialise OpenAI client: %s", exc)

_MODEL = "gpt-4o-mini"

_SYSTEM_PROMPT = (
    "You are a sales assistant for a wholesale/trade business in India. "
    "You write professional, concise follow-up messages to business clients. "
    "Your tone is warm but businesslike. Keep messages under 100 words. "
    "Do not include subject lines, email headers, or signature blocks. "
    "Write directly as if sending a WhatsApp or SMS message."
)

# ── Fallback templates (rotated on each regenerate call) ───────────────────
_regen_counters: dict[str, int] = {}

_FALLBACK_TEMPLATES = [
    (
        "Hi {contact}, just checking in regarding {topic}. "
        "I'd love to help move things forward — are you available for a quick chat this week?"
    ),
    (
        "Hi {contact}, following up on our recent conversation. "
        "We've got some updates on {topic} that might interest you. "
        "Would you like me to send over the details?"
    ),
    (
        "Hi {contact}, hope all is well! Wanted to touch base about {topic}. "
        "Happy to work around your schedule — let me know a good time to connect."
    ),
    (
        "Hi {contact}, reaching out again about {topic}. "
        "I understand things can get busy — just wanted to confirm we're still aligned. "
        "Let me know how you'd like to proceed."
    ),
]


def _deal_topic(stage: str, deal_value: float) -> str:
    value_str = f"₹{deal_value:,.0f}"
    topics = {
        "closing": f"the {value_str} order finalization",
        "negotiation": f"the {value_str} deal we're working on",
        "quoted": f"the {value_str} quote",
        "follow-up": "the supply requirements we discussed",
        "new": "how we can support your business",
    }
    return topics.get(stage, "our ongoing discussion")


def _build_user_prompt(
    company_name: str,
    contact_person: str,
    stage: str,
    days_inactive: int,
    deal_value: float,
    last_message_snippet: str,
    conversation_signals: list[str],
    extra_instruction: str = "",
) -> str:
    signals_text = (
        "\n".join(f"  - {s}" for s in conversation_signals)
        if conversation_signals
        else "  (none)"
    )
    prompt = (
        f"Write a follow-up message for this lead:\n"
        f"- Company: {company_name}\n"
        f"- Contact person: {contact_person}\n"
        f"- Sales stage: {stage}\n"
        f"- Days since last contact: {days_inactive}\n"
        f"- Deal value: ₹{deal_value:,.0f}\n"
        f"- Last message: {last_message_snippet}\n"
        f"- Key signals:\n{signals_text}\n"
    )
    if extra_instruction:
        prompt += f"\n{extra_instruction}\n"
    return prompt


# ── Public API ──────────────────────────────────────────────────────────────

def generate_followup_message(
    company_name: str,
    contact_person: str,
    stage: str,
    days_inactive: int,
    deal_value: float,
    last_message_snippet: str,
    conversation_signals: list[str],
    existing_message: str = "",
) -> tuple[str, str]:
    """Return *(message, source)* where source is ``"openai"`` or ``"fallback"``."""
    if _client:
        try:
            resp = _client.chat.completions.create(
                model=_MODEL,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": _build_user_prompt(
                        company_name, contact_person, stage, days_inactive,
                        deal_value, last_message_snippet, conversation_signals,
                    )},
                ],
                temperature=0.7,
                max_tokens=250,
            )
            text = resp.choices[0].message.content.strip()
            if text:
                return text, "openai"
        except Exception as exc:
            logger.warning("OpenAI generate failed: %s", exc)

    if existing_message:
        return existing_message, "fallback"
    topic = _deal_topic(stage, deal_value)
    return _FALLBACK_TEMPLATES[0].format(contact=contact_person, topic=topic), "fallback"


def regenerate_followup_message(
    lead_id: str,
    company_name: str,
    contact_person: str,
    stage: str,
    days_inactive: int,
    deal_value: float,
    last_message_snippet: str,
    conversation_signals: list[str],
    previous_message: str = "",
) -> tuple[str, str]:
    """Generate a *different* follow-up draft.  Returns *(message, source)*."""
    if _client:
        try:
            extra = ""
            if previous_message:
                extra = (
                    "IMPORTANT: Write a DIFFERENT message. "
                    "Do not reuse this previous draft:\n"
                    f'"{previous_message[:200]}"'
                )
            resp = _client.chat.completions.create(
                model=_MODEL,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": _build_user_prompt(
                        company_name, contact_person, stage, days_inactive,
                        deal_value, last_message_snippet, conversation_signals,
                        extra_instruction=extra,
                    )},
                ],
                temperature=0.9,
                max_tokens=250,
            )
            text = resp.choices[0].message.content.strip()
            if text:
                return text, "openai"
        except Exception as exc:
            logger.warning("OpenAI regenerate failed: %s", exc)

    # Fallback: rotate through templates so each press gives a new message
    counter = _regen_counters.get(lead_id, 0)
    _regen_counters[lead_id] = counter + 1
    topic = _deal_topic(stage, deal_value)
    template = _FALLBACK_TEMPLATES[counter % len(_FALLBACK_TEMPLATES)]
    return template.format(contact=contact_person, topic=topic), "fallback"


def generate_conversation_summary(
    company_name: str,
    contact_person: str,
    stage: str,
    deal_value: float,
    conversation_signals: list[str],
    last_message_snippet: str,
    existing_summary: str = "",
) -> tuple[str, str]:
    """Return *(summary, source)*.  Falls back to the existing summary."""
    if _client:
        try:
            signals_text = (
                ", ".join(conversation_signals) if conversation_signals else "(none)"
            )
            prompt = (
                f"Summarize this sales conversation in 2-3 concise sentences:\n"
                f"- Company: {company_name}\n"
                f"- Contact: {contact_person}\n"
                f"- Stage: {stage}\n"
                f"- Deal value: ₹{deal_value:,.0f}\n"
                f"- Key signals: {signals_text}\n"
                f"- Last message: {last_message_snippet}\n"
            )
            resp = _client.chat.completions.create(
                model=_MODEL,
                messages=[
                    {"role": "system", "content": (
                        "You summarize sales conversations concisely "
                        "for a CRM dashboard. 2-3 sentences max."
                    )},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=150,
            )
            text = resp.choices[0].message.content.strip()
            if text:
                return text, "openai"
        except Exception as exc:
            logger.warning("OpenAI summary failed: %s", exc)

    return existing_summary, "fallback"
