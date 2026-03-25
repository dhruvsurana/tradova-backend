from __future__ import annotations

from pydantic import BaseModel


class TimelineEvent(BaseModel):
    date: str
    type: str
    summary: str


class WhatsAppMessage(BaseModel):
    sender: str
    text: str
    time: str


class Lead(BaseModel):
    id: str
    company_name: str
    contact_person: str
    deal_value: float
    stage: str
    ai_recommendation: str = ""
    next_action: str = ""
    last_contact_time: str = ""
    revenue_at_risk: float = 0.0
    urgency_text: str = ""
    ai_reasoning: str = ""
    conversation_summary: str = ""
    conversation_signals: list[str] = []
    last_message_snippet: str = ""
    whatsapp_preview_messages: list[WhatsAppMessage] = []
    generated_followup_message: str = ""
    conversion_probability: float = 0.0
    days_inactive: int = 0
    interaction_timeline: list[TimelineEvent] = []
    phone_number: str = ""
    priority_score: float = 0.0
    last_followup_at: str = ""
    recommendation_text: str = ""


class LeadSummary(BaseModel):
    id: str
    company_name: str
    contact_person: str
    deal_value: float
    stage: str
    ai_recommendation: str = ""
    next_action: str = ""
    last_contact_time: str = ""
    revenue_at_risk: float = 0.0
    urgency_text: str = ""
    conversion_probability: float = 0.0
    days_inactive: int = 0
    last_message_snippet: str = ""
    phone_number: str = ""
    priority_score: float = 0.0
    last_followup_at: str = ""
    recommendation_text: str = ""


class SendFollowUpRequest(BaseModel):
    message: str | None = None
    channel: str = "whatsapp"


class SendFollowUpResponse(BaseModel):
    success: bool
    message_sent: str
    channel: str
    sent_at: str
    updated_lead: Lead


class CreateLeadRequest(BaseModel):
    company_name: str
    contact_person: str
    deal_value: float
    stage: str = "new"
    phone_number: str = ""
    next_action: str = ""
    conversation_summary: str = ""
    last_message_snippet: str = ""


class RegenerateMessageResponse(BaseModel):
    generated_followup_message: str
    conversation_summary: str
    source: str


class PipelineStageLead(BaseModel):
    id: str
    company_name: str
    deal_value: float


class PipelineStageSummary(BaseModel):
    stage: str
    count: int
    total_value: float
    leads: list[PipelineStageLead]


class DashboardSummary(BaseModel):
    total_leads: int
    total_pipeline_value: float
    total_revenue_at_risk: float
    avg_conversion_probability: float
    leads_by_stage: dict[str, int]
    pipeline_stages: list[PipelineStageSummary] = []
    urgent_leads: int
    leads_needing_followup: int
    leads_at_risk_count: int = 0
    leads_at_risk: list[dict] = []
    hot_leads: list[dict] = []
    followups_due_today: list[dict] = []
    ai_insights: list[str] = []
