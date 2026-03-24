"""Tradova — AI Follow-Up Intelligence Engine (demo backend)."""

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import ai_service
from data import init_leads
from models import (
    CreateLeadRequest,
    DashboardSummary,
    Lead,
    LeadSummary,
    RegenerateMessageResponse,
    SendFollowUpRequest,
    SendFollowUpResponse,
    TimelineEvent,
)
from scoring import compute_score_and_label

app = FastAPI(title="Tradova API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LEADS = init_leads()


# ── Helpers ─────────────────────────────────────────────────────────────────

_STAGE_DEFAULT_PROBABILITY: dict[str, float] = {
    "closing": 80, "negotiation": 60, "quoted": 50, "follow-up": 40, "new": 30,
}

_LABEL_DEFAULT_ACTION: dict[str, str] = {
    "Follow Up Now": "Send follow-up message immediately",
    "Needs Follow-Up": "Schedule follow-up within this week",
    "Close Soon": "Send final proposal and close the deal",
    "On Track": "Maintain relationship, follow standard cadence",
}


COOLDOWN_HOURS = 24

AT_RISK_INACTIVE_DAYS = 3
_AT_RISK_LABELS = frozenset({"Follow Up Now", "Needs Follow-Up"})


def _is_at_risk(lead: Lead) -> bool:
    """A lead is actionable/at-risk if it needs follow-up or has gone cold."""
    return (
        lead.ai_recommendation in _AT_RISK_LABELS
        or lead.days_inactive >= AT_RISK_INACTIVE_DAYS
    )


def _is_in_cooldown(lead: Lead) -> bool:
    """True if a follow-up was sent within the last COOLDOWN_HOURS."""
    if not lead.last_followup_at:
        return False
    try:
        sent = datetime.fromisoformat(lead.last_followup_at)
        return datetime.now() - sent < timedelta(hours=COOLDOWN_HOURS)
    except (ValueError, TypeError):
        return False


def _recommendation_text(company: str, next_action: str, label: str, cooldown: bool) -> str:
    """Render-ready string for dashboard AI sections: "{Company} — {action}"."""
    if cooldown:
        return f"{company} — Awaiting reply after recent follow-up"
    if next_action:
        return f"{company} — {next_action}"
    return f"{company} — {label}"


def _recompute_scoring(lead: Lead) -> Lead:
    """Return a copy of *lead* with priority_score, ai_recommendation, and recommendation_text refreshed."""
    cooldown = _is_in_cooldown(lead)
    score, label = compute_score_and_label(
        days_inactive=lead.days_inactive,
        deal_value=lead.deal_value,
        revenue_at_risk=lead.revenue_at_risk,
        conversion_probability=lead.conversion_probability,
        stage=lead.stage,
        cooldown_active=cooldown,
    )
    rec_text = _recommendation_text(lead.company_name, lead.next_action, label, cooldown)
    return lead.model_copy(update={
        "priority_score": score,
        "ai_recommendation": label,
        "recommendation_text": rec_text,
    })


# ── GET /leads ──────────────────────────────────────────────────────────────

@app.get("/leads", response_model=list[LeadSummary])
def list_leads():
    """Return all leads as lightweight summaries, sorted by priority score."""
    summaries = [
        LeadSummary(
            id=lead.id,
            company_name=lead.company_name,
            contact_person=lead.contact_person,
            deal_value=lead.deal_value,
            stage=lead.stage,
            ai_recommendation=lead.ai_recommendation,
            next_action=lead.next_action,
            last_contact_time=lead.last_contact_time,
            revenue_at_risk=lead.revenue_at_risk,
            urgency_text=lead.urgency_text,
            conversion_probability=lead.conversion_probability,
            days_inactive=lead.days_inactive,
            last_message_snippet=lead.last_message_snippet,
            phone_number=lead.phone_number,
            priority_score=lead.priority_score,
            last_followup_at=lead.last_followup_at,
            recommendation_text=lead.recommendation_text,
        )
        for lead in LEADS.values()
    ]
    summaries.sort(key=lambda s: -s.priority_score)
    return summaries


# ── GET /leads/{id} ─────────────────────────────────────────────────────────

@app.get("/leads/{lead_id}", response_model=Lead)
def get_lead(lead_id: str):
    """Return full lead detail including AI reasoning, timeline, and messages."""
    lead = LEADS.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


# ── POST /leads/{id}/send-followup ──────────────────────────────────────────

@app.post("/leads/{lead_id}/send-followup", response_model=SendFollowUpResponse)
def send_followup(lead_id: str, body: SendFollowUpRequest | None = None):
    """Simulate sending a follow-up message. Mutates lead state in memory.

    Post-send state transition:
      - days_inactive → 0
      - last_contact_time → now
      - last_followup_at → now  (starts 24-h cooldown)
      - revenue_at_risk → halved (outreach reduces immediate risk)
      - urgency_text / next_action updated
      - scoring recomputed with cooldown → label becomes "On Track"
      - lead drops in the priority queue
    """
    lead = LEADS.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    message = (body.message if body and body.message else lead.generated_followup_message)
    channel = body.channel if body else "whatsapp"
    sent_at = datetime.now()

    new_event = TimelineEvent(
        date=sent_at.isoformat(),
        type=channel,
        summary=f"AI-assisted follow-up sent via {channel}",
    )

    updated = lead.model_copy(
        update={
            "last_contact_time": sent_at.isoformat(),
            "last_followup_at": sent_at.isoformat(),
            "days_inactive": 0,
            "revenue_at_risk": round(lead.revenue_at_risk / 2, 2),
            "interaction_timeline": lead.interaction_timeline + [new_event],
            "urgency_text": "Follow-up sent today — on track, awaiting response",
            "next_action": "Await response — re-engage if no reply in 2-3 days",
            "last_message_snippet": f"You: {message[:100]}{'…' if len(message) > 100 else ''}",
        }
    )
    updated = _recompute_scoring(updated)
    LEADS[lead_id] = updated

    return SendFollowUpResponse(
        success=True,
        message_sent=message,
        channel=channel,
        sent_at=sent_at.isoformat(),
        updated_lead=updated,
    )


# ── POST /leads/{id}/regenerate-message ─────────────────────────────────────

@app.post("/leads/{lead_id}/regenerate-message", response_model=RegenerateMessageResponse)
def regenerate_message(lead_id: str):
    """Generate a new follow-up draft (OpenAI if available, else template rotation)."""
    lead = LEADS.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    new_message, msg_source = ai_service.regenerate_followup_message(
        lead_id=lead_id,
        company_name=lead.company_name,
        contact_person=lead.contact_person,
        stage=lead.stage,
        days_inactive=lead.days_inactive,
        deal_value=lead.deal_value,
        last_message_snippet=lead.last_message_snippet,
        conversation_signals=lead.conversation_signals,
        previous_message=lead.generated_followup_message,
    )

    new_summary, _ = ai_service.generate_conversation_summary(
        company_name=lead.company_name,
        contact_person=lead.contact_person,
        stage=lead.stage,
        deal_value=lead.deal_value,
        conversation_signals=lead.conversation_signals,
        last_message_snippet=lead.last_message_snippet,
        existing_summary=lead.conversation_summary,
    )

    updated = lead.model_copy(update={
        "generated_followup_message": new_message,
        "conversation_summary": new_summary,
    })
    LEADS[lead_id] = updated

    return RegenerateMessageResponse(
        generated_followup_message=new_message,
        conversation_summary=new_summary,
        source=msg_source,
    )


# ── POST /leads ─────────────────────────────────────────────────────────────

@app.post("/leads", response_model=Lead, status_code=201)
def create_lead(body: CreateLeadRequest):
    """Add a new lead to the in-memory store and return it with scoring applied."""
    lead_num = len(LEADS) + 1
    lead_id = f"lead-{lead_num:03d}"
    while lead_id in LEADS:
        lead_num += 1
        lead_id = f"lead-{lead_num:03d}"

    prob = _STAGE_DEFAULT_PROBABILITY.get(body.stage, 30)
    score, label = compute_score_and_label(
        days_inactive=0,
        deal_value=body.deal_value,
        revenue_at_risk=0,
        conversion_probability=prob,
        stage=body.stage,
    )

    now = datetime.now()
    next_action = body.next_action or _LABEL_DEFAULT_ACTION.get(label, "Review and plan next steps")
    lead = Lead(
        id=lead_id,
        company_name=body.company_name,
        contact_person=body.contact_person,
        deal_value=body.deal_value,
        stage=body.stage,
        phone_number=body.phone_number,
        ai_recommendation=label,
        priority_score=score,
        recommendation_text=_recommendation_text(body.company_name, next_action, label, False),
        next_action=next_action,
        last_contact_time=now.isoformat(),
        urgency_text=f"New lead added — {label.lower()}",
        ai_reasoning=f"New lead for {body.company_name}. Stage: {body.stage}. Recommended action: {label.lower()}.",
        conversation_summary=body.conversation_summary or f"New lead: {body.company_name} ({body.contact_person})",
        last_message_snippet=body.last_message_snippet,
        generated_followup_message=(
            f"Hi {body.contact_person}, thanks for connecting! I'd love to learn "
            f"more about {body.company_name}'s requirements and explore how we can "
            f"help. Would you be free for a quick call this week?"
        ),
        conversion_probability=prob,
        interaction_timeline=[
            TimelineEvent(date=now.isoformat(), type="system", summary="Lead created in Tradova"),
        ],
    )

    LEADS[lead_id] = lead
    return lead


# ── GET /dashboard/summary ─────────────────────────────────────────────────

@app.get("/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary():
    """Aggregated pipeline stats for the dashboard view."""
    leads = list(LEADS.values())
    total = len(leads)

    stage_counts: dict[str, int] = {}
    for lead in leads:
        stage_counts[lead.stage] = stage_counts.get(lead.stage, 0) + 1

    total_pipeline = sum(l.deal_value for l in leads)
    total_risk = sum(l.revenue_at_risk for l in leads)
    avg_prob = sum(l.conversion_probability for l in leads) / total if total else 0
    urgent = sum(1 for l in leads if l.days_inactive >= 7)
    needs_followup = sum(1 for l in leads if l.days_inactive >= 5)

    at_risk = [l for l in leads if _is_at_risk(l)]
    leads_at_risk = [
        {
            "id": l.id,
            "company_name": l.company_name,
            "revenue_at_risk": l.revenue_at_risk,
            "days_inactive": l.days_inactive,
            "ai_recommendation": l.ai_recommendation,
        }
        for l in at_risk
    ]
    hot_leads = [
        {"id": l.id, "company_name": l.company_name, "deal_value": l.deal_value}
        for l in leads if l.conversion_probability >= 60 or l.stage == "closing"
    ]
    followups_due_today = [
        {"id": l.id, "company_name": l.company_name, "days_inactive": l.days_inactive}
        for l in leads if l.days_inactive >= 5
    ]
    sorted_leads = sorted(leads, key=lambda l: -l.priority_score)
    top_recommendations = [
        {"id": l.id, "company_name": l.company_name, "ai_recommendation": l.ai_recommendation, "recommendation_text": l.recommendation_text}
        for l in sorted_leads[:5]
    ]

    return DashboardSummary(
        total_leads=total,
        total_pipeline_value=total_pipeline,
        total_revenue_at_risk=total_risk,
        avg_conversion_probability=round(avg_prob, 1),
        leads_by_stage=stage_counts,
        urgent_leads=urgent,
        leads_needing_followup=needs_followup,
        leads_at_risk_count=len(leads_at_risk),
        leads_at_risk=leads_at_risk,
        hot_leads=hot_leads,
        followups_due_today=followups_due_today,
        top_recommendations=top_recommendations,
    )
