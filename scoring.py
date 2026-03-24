"""
Tradova — Deterministic Lead Scoring & Recommendation Engine
=============================================================

HOW IT WORKS (plain English for pitch/deck):

  Tradova ranks every lead using a weighted urgency score (0–100) based on
  five signals that any sales team intuitively tracks:

    1. Inactivity (35%) — How many days since the last contact?
       Leads going cold are the biggest risk in wholesale sales.

    2. Revenue at Risk (30%) — What fraction of the deal value is at risk?
       A ₹7L deal with 50% at risk scores higher than a ₹1L deal fully at risk.

    3. Deal Stage (15%) — Closing and negotiation stages need faster action
       than new or early follow-up leads.

    4. Deal Size (10%) — Bigger deals deserve proportionally more attention.

    5. Conversion Probability (10%) — Higher-probability leads are more
       worth pursuing right now.

  The raw score maps to one of four actionable labels:

    • Close Soon        — deal is at the finish line (closing stage, high probability)
    • Follow Up Now     — high urgency, act today
    • Needs Follow-Up   — moderate urgency, act this week
    • On Track          — no immediate action required

  COOLDOWN RULE: After a follow-up is sent, the lead enters a 24-hour
  cooldown.  During cooldown the score is penalised and the label is
  forced to "On Track" (unless the deal is in closing stage).  This
  prevents a just-contacted lead from sitting at the top of the urgent
  queue, which would make the product feel broken.

  Leads are sorted by this score in the dashboard queue so the sales team
  always knows exactly who to contact first and why.
"""

from __future__ import annotations

# ── Weights ─────────────────────────────────────────────────────────────────
W_INACTIVITY  = 0.35
W_RISK_RATIO  = 0.30
W_STAGE       = 0.15
W_DEAL_VALUE  = 0.10
W_PROBABILITY = 0.10

# ── Normalization caps ──────────────────────────────────────────────────────
MAX_INACTIVE_DAYS = 30
MAX_DEAL_VALUE = 750_000

# ── Stage urgency map ──────────────────────────────────────────────────────
STAGE_SCORES: dict[str, int] = {
    "closing": 90,
    "negotiation": 70,
    "quoted": 50,
    "follow-up": 40,
    "new": 30,
}

# ── Label thresholds ───────────────────────────────────────────────────────
THRESHOLD_FOLLOW_UP_NOW = 55
THRESHOLD_NEEDS_FOLLOW_UP = 25

# ── Close-ready boost (keeps closing deals near the top of the queue) ──────
CLOSE_SOON_BOOST = 25

# ── Post-send cooldown (suppresses urgency after outreach) ─────────────────
COOLDOWN_PENALTY = 30


def compute_score_and_label(
    days_inactive: int,
    deal_value: float,
    revenue_at_risk: float,
    conversion_probability: float,
    stage: str,
    *,
    cooldown_active: bool = False,
) -> tuple[float, str]:
    """Return (priority_score, ai_recommendation_label) for a lead.

    The score drives queue ordering.  The label is the user-visible
    recommendation shown on dashboard cards and lead detail pages.

    When *cooldown_active* is True (follow-up sent in the last 24 h) the
    score is reduced and the label is capped at "On Track" so the lead
    drops in the queue until the cooldown expires.
    """
    inactivity_norm = min(days_inactive / MAX_INACTIVE_DAYS, 1.0) * 100
    deal_norm = min(deal_value / MAX_DEAL_VALUE, 1.0) * 100
    risk_ratio = (revenue_at_risk / deal_value * 100) if deal_value > 0 else 0
    stage_score = STAGE_SCORES.get(stage, 30)

    raw = (
        inactivity_norm * W_INACTIVITY
        + risk_ratio * W_RISK_RATIO
        + stage_score * W_STAGE
        + deal_norm * W_DEAL_VALUE
        + conversion_probability * W_PROBABILITY
    )

    if stage == "closing" and conversion_probability >= 70:
        label = "Close Soon"
        raw += CLOSE_SOON_BOOST
    elif raw >= THRESHOLD_FOLLOW_UP_NOW:
        label = "Follow Up Now"
    elif raw >= THRESHOLD_NEEDS_FOLLOW_UP:
        label = "Needs Follow-Up"
    else:
        label = "On Track"

    if cooldown_active:
        raw = max(raw - COOLDOWN_PENALTY, 0)
        if label in ("Follow Up Now", "Needs Follow-Up"):
            label = "On Track"

    return round(raw, 1), label
