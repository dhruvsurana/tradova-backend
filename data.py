"""In-memory seed data for 10 realistic wholesale/trade leads."""

from __future__ import annotations

from datetime import datetime, timedelta

from models import Lead, TimelineEvent, WhatsAppMessage
from scoring import compute_score_and_label

_now = datetime.now()


def _days_ago(n: int) -> str:
    return (_now - timedelta(days=n)).isoformat()


def _time_ago(hours: int) -> str:
    return (_now - timedelta(hours=hours)).strftime("%I:%M %p")


_seed: list[dict] = [
    # ── 1. Metro Distributors — AT RISK, going cold ─────────────────────
    {
        "id": "lead-001",
        "company_name": "Metro Distributors",
        "contact_person": "Vikram Mehta",
        "phone_number": "+91 98210 44001",
        "deal_value": 285000,
        "stage": "negotiation",
        "next_action": "Send revised pricing before they go with competitor",
        "last_contact_time": _days_ago(12),
        "revenue_at_risk": 285000,
        "urgency_text": "12 days since last contact — deal slipping away",
        "ai_reasoning": "Vikram requested a revised quote 12 days ago and hasn't received one. Competitor (National Supplies) is actively pitching. High deal value makes this the top priority. The tone in last messages suggests impatience.",
        "conversation_summary": "Vikram reached out about bulk packaging materials for Q2. Initial quote sent at ₹285K. He asked for 8% discount citing competitor pricing. No response sent to his last message.",
        "conversation_signals": [
            "Mentioned competitor pricing",
            "Asked for discount — buying signal",
            "Last message unanswered for 12 days",
            "Previously responsive within 24h",
        ],
        "last_message_snippet": "Vikram: Can you match National's rate? Need to decide by this week.",
        "whatsapp_preview_messages": [
            WhatsAppMessage(sender="them", text="Hi, got the quote. Looks good but National Supplies is offering 8% less on the same SKUs.", time=_time_ago(288)),
            WhatsAppMessage(sender="you", text="Let me check with the team on what we can do. Will get back to you.", time=_time_ago(285)),
            WhatsAppMessage(sender="them", text="Can you match National's rate? Need to decide by this week.", time=_time_ago(264)),
        ],
        "generated_followup_message": "Hi Vikram, apologies for the delay. I've worked out revised pricing for the Q2 bulk order — we can offer a 6% discount bringing it to ₹267,900. This includes priority dispatch and flexible payment terms that National doesn't match. Can we hop on a quick call today to finalize?",
        "conversion_probability": 42,
        "days_inactive": 12,
        "interaction_timeline": [
            TimelineEvent(date=_days_ago(30), type="whatsapp", summary="Initial inquiry about bulk packaging materials"),
            TimelineEvent(date=_days_ago(22), type="call", summary="Discovery call — discussed Q2 requirements, ~₹285K order"),
            TimelineEvent(date=_days_ago(18), type="email", summary="Sent formal quote with product catalog"),
            TimelineEvent(date=_days_ago(12), type="whatsapp", summary="Vikram mentioned competitor pricing, asked for discount"),
            TimelineEvent(date=_days_ago(12), type="whatsapp", summary="Promised to check with team — NO FOLLOW-UP SENT"),
        ],
    },
    # ── 2. Raj Traders — HOT, ready to close ────────────────────────────
    {
        "id": "lead-002",
        "company_name": "Raj Traders",
        "contact_person": "Suresh Rajput",
        "phone_number": "+91 98210 44002",
        "deal_value": 520000,
        "stage": "closing",
        "next_action": "Send payment link and delivery schedule",
        "last_contact_time": _days_ago(2),
        "revenue_at_risk": 0,
        "urgency_text": "Deal ready to close — awaiting final confirmation",
        "ai_reasoning": "Suresh has verbally confirmed the order and asked for payment details. This is a high-value deal at the finish line. Any delay risks him reconsidering. All buying signals are strong — he's asked about delivery timelines, not pricing.",
        "conversation_summary": "Raj Traders needs industrial cleaning supplies for their chain of 15 stores. Went through full sales cycle — demo, quote, negotiation. Suresh verbally confirmed ₹520K order and asked how to proceed with payment.",
        "conversation_signals": [
            "Verbal confirmation received",
            "Asked about payment process — strongest buying signal",
            "No price objections in last 3 interactions",
            "Mentioned internal deadline to onboard supplier",
        ],
        "last_message_snippet": "Suresh: All good from our end. Send me the payment details and delivery schedule.",
        "whatsapp_preview_messages": [
            WhatsAppMessage(sender="you", text="Hi Suresh, the final quote for 15 stores comes to ₹5,20,000 with the volume discount applied.", time=_time_ago(72)),
            WhatsAppMessage(sender="them", text="Looks good. Let me confirm with my partner.", time=_time_ago(60)),
            WhatsAppMessage(sender="them", text="All good from our end. Send me the payment details and delivery schedule.", time=_time_ago(48)),
        ],
        "generated_followup_message": "Hi Suresh! Great to hear the confirmation. Here are the payment details:\n\nOrder: Industrial cleaning supplies (15 stores)\nAmount: ₹5,20,000\nPayment: Bank transfer / UPI\n\nDelivery starts within 5 business days of payment. I'll share the store-wise dispatch schedule once we're confirmed. Thanks for choosing us!",
        "conversion_probability": 92,
        "days_inactive": 2,
        "interaction_timeline": [
            TimelineEvent(date=_days_ago(45), type="email", summary="Inbound inquiry via website — bulk cleaning supplies"),
            TimelineEvent(date=_days_ago(38), type="call", summary="Discovery call — 15-store chain, quarterly supply needs"),
            TimelineEvent(date=_days_ago(30), type="meeting", summary="Product demo at Raj Traders HQ"),
            TimelineEvent(date=_days_ago(20), type="email", summary="Sent detailed quote — ₹5.2L with volume discount"),
            TimelineEvent(date=_days_ago(10), type="whatsapp", summary="Negotiation — agreed on payment terms"),
            TimelineEvent(date=_days_ago(2), type="whatsapp", summary="Suresh confirmed order, asked for payment details"),
        ],
    },
    # ── 3. Patel & Sons Trading — HIGH VALUE, needs nurturing ───────────
    {
        "id": "lead-003",
        "company_name": "Patel & Sons Trading",
        "contact_person": "Amit Patel",
        "phone_number": "+91 98210 44003",
        "deal_value": 740000,
        "stage": "quoted",
        "next_action": "Propose a product demo or factory visit this week",
        "last_contact_time": _days_ago(6),
        "revenue_at_risk": 370000,
        "urgency_text": "Highest-value deal in pipeline — needs active nurturing",
        "ai_reasoning": "₹7.4L deal is the biggest in the pipeline. Amit is interested but cautious — he's asked detailed quality questions, which suggests he's evaluating seriously but hasn't committed. A demo or factory visit would build the trust needed to move forward. Competitors are not yet in the picture, so timing is in our favor.",
        "conversation_summary": "Patel & Sons is expanding their FMCG distribution and needs packaging and logistics supplies. Amit received the quote but has quality concerns — wants to see samples or visit the factory before committing to such a large order.",
        "conversation_signals": [
            "Asking detailed quality questions — serious buyer",
            "No competitor mentions — we have the advantage",
            "Requested samples/factory visit",
            "Deal value is 40% of monthly pipeline",
        ],
        "last_message_snippet": "Amit: The pricing works. But for this volume, I'd need to see the quality firsthand. Can we arrange something?",
        "whatsapp_preview_messages": [
            WhatsAppMessage(sender="you", text="Hi Amit, here's the detailed quote for the packaging and logistics supplies — ₹7,40,000 for the full order.", time=_time_ago(168)),
            WhatsAppMessage(sender="them", text="Thanks. The numbers look reasonable. What's the quality grade on the corrugated boxes?", time=_time_ago(156)),
            WhatsAppMessage(sender="you", text="We use 5-ply 180 GSM — same spec as what Hindustan Unilever uses. Happy to send samples.", time=_time_ago(150)),
            WhatsAppMessage(sender="them", text="The pricing works. But for this volume, I'd need to see the quality firsthand. Can we arrange something?", time=_time_ago(144)),
        ],
        "generated_followup_message": "Hi Amit, absolutely — let's arrange a visit. I can set up a factory tour this Thursday or Friday where you can see the production line and inspect samples directly. We'll also prepare a custom spec sheet for your FMCG requirements. Which day works better for you?",
        "conversion_probability": 65,
        "days_inactive": 6,
        "interaction_timeline": [
            TimelineEvent(date=_days_ago(25), type="call", summary="Cold call — introduced product range for FMCG distribution"),
            TimelineEvent(date=_days_ago(20), type="email", summary="Sent product catalog and company profile"),
            TimelineEvent(date=_days_ago(14), type="whatsapp", summary="Amit expressed interest, asked for custom quote"),
            TimelineEvent(date=_days_ago(7), type="email", summary="Sent detailed quote — ₹7.4L"),
            TimelineEvent(date=_days_ago(6), type="whatsapp", summary="Amit asked about quality, requested factory visit"),
        ],
    },
    # ── 4-10: Supporting leads ──────────────────────────────────────────
    {
        "id": "lead-004",
        "company_name": "Krishna Enterprises",
        "contact_person": "Deepak Krishna",
        "phone_number": "+91 98210 44004",
        "deal_value": 180000,
        "stage": "follow-up",
        "next_action": "Share new Q2 catalog and check if requirements changed",
        "last_contact_time": _days_ago(18),
        "revenue_at_risk": 180000,
        "urgency_text": "18 days inactive — re-engagement needed",
        "ai_reasoning": "Deepak showed strong initial interest but went quiet after receiving the first quote. The long gap suggests he may be exploring alternatives or the requirement shifted. A fresh touchpoint with the updated catalog could reignite the conversation.",
        "conversation_summary": "Krishna Enterprises needs office and warehouse supplies for their new Pune facility. Initial discussions were positive but stalled after quoting stage.",
        "conversation_signals": [
            "Went silent after quote — possible price concern",
            "New facility opening — real need exists",
            "18-day gap is above average response time",
        ],
        "last_message_snippet": "Deepak: Let me review the quote and get back to you.",
        "whatsapp_preview_messages": [
            WhatsAppMessage(sender="you", text="Hi Deepak, here's the quote for the Pune facility supplies.", time=_time_ago(432)),
            WhatsAppMessage(sender="them", text="Let me review the quote and get back to you.", time=_time_ago(420)),
        ],
        "generated_followup_message": "Hi Deepak, hope you're doing well! Just wanted to check in on the Pune facility supplies. We've updated our Q2 catalog with some new products and better pricing on bulk orders. Would you like me to send over a revised quote? Happy to adjust based on any changes in your requirements.",
        "conversion_probability": 30,
        "days_inactive": 18,
        "interaction_timeline": [
            TimelineEvent(date=_days_ago(30), type="call", summary="Initial inquiry about office and warehouse supplies"),
            TimelineEvent(date=_days_ago(25), type="email", summary="Sent product catalog for facility setup"),
            TimelineEvent(date=_days_ago(18), type="whatsapp", summary="Sent quote, Deepak said he'd review — no response since"),
        ],
    },
    {
        "id": "lead-005",
        "company_name": "Gupta Wholesale Mart",
        "contact_person": "Priya Gupta",
        "phone_number": "+91 98210 44005",
        "deal_value": 95000,
        "stage": "new",
        "next_action": "Share catalog and schedule discovery call",
        "last_contact_time": _days_ago(3),
        "revenue_at_risk": 0,
        "urgency_text": "New lead — respond quickly to build momentum",
        "ai_reasoning": "Fresh inbound lead from trade show. Priya expressed interest in stationery supplies for her wholesale chain. Quick response will set the right impression. Deal value is moderate but could grow with repeat orders.",
        "conversation_summary": "Met Priya at the IndiaMART trade show. She runs a wholesale mart chain and is looking for a reliable stationery supplier. Exchanged contacts and she asked for a catalog.",
        "conversation_signals": [
            "Inbound interest from trade show",
            "Asked for catalog — early buying signal",
            "Wholesale chain — potential for recurring orders",
        ],
        "last_message_snippet": "Priya: Nice meeting you at the show! Please send over your catalog when you get a chance.",
        "whatsapp_preview_messages": [
            WhatsAppMessage(sender="them", text="Nice meeting you at the show! Please send over your catalog when you get a chance.", time=_time_ago(72)),
        ],
        "generated_followup_message": "Hi Priya! Great meeting you at the IndiaMART show. Here's our latest stationery catalog with wholesale pricing. I've highlighted a few products that typically work well for retail chains like yours. Would you be free for a quick 15-min call this week to discuss your specific needs?",
        "conversion_probability": 45,
        "days_inactive": 3,
        "interaction_timeline": [
            TimelineEvent(date=_days_ago(3), type="meeting", summary="Met at IndiaMART trade show, exchanged contacts"),
        ],
    },
    {
        "id": "lead-006",
        "company_name": "Singh Brothers Import-Export",
        "contact_person": "Harpreet Singh",
        "phone_number": "+91 98210 44006",
        "deal_value": 410000,
        "stage": "negotiation",
        "next_action": "Propose consolidated shipping to reduce per-unit cost",
        "last_contact_time": _days_ago(5),
        "revenue_at_risk": 123000,
        "urgency_text": "Active negotiation — shipping cost is the blocker",
        "ai_reasoning": "Harpreet is keen on the products but concerned about shipping costs to his Delhi warehouse. The deal value is strong at ₹4.1L. Proposing consolidated shipment or adjusting MOQ could resolve the objection without cutting into margins significantly.",
        "conversation_summary": "Singh Brothers imports specialty food packaging. They like our products and pricing but shipping costs are eating into their margins. Need a creative logistics solution.",
        "conversation_signals": [
            "Product fit confirmed — no quality objections",
            "Price is acceptable — shipping is the only blocker",
            "Asked about minimum order for free shipping",
            "Engaged and responsive",
        ],
        "last_message_snippet": "Harpreet: The product pricing is great, but the shipping to Delhi is adding ₹15 per unit. That's a dealbreaker at this volume.",
        "whatsapp_preview_messages": [
            WhatsAppMessage(sender="them", text="The product pricing is great, but the shipping to Delhi is adding ₹15 per unit. That's a dealbreaker at this volume.", time=_time_ago(120)),
            WhatsAppMessage(sender="you", text="I understand, Harpreet. Let me work out a consolidated shipping option and get back to you.", time=_time_ago(118)),
        ],
        "generated_followup_message": "Hi Harpreet, I've worked out a solution for the shipping. If we consolidate into 2 bulk shipments per month instead of weekly dispatches, we can bring the per-unit shipping cost down to ₹6 (from ₹15). For your volume, that saves over ₹90K annually. Want me to send a revised proposal with these logistics terms?",
        "conversion_probability": 58,
        "days_inactive": 5,
        "interaction_timeline": [
            TimelineEvent(date=_days_ago(35), type="email", summary="Inbound inquiry about specialty food packaging"),
            TimelineEvent(date=_days_ago(28), type="call", summary="Product discussion — confirmed fit for import-export needs"),
            TimelineEvent(date=_days_ago(15), type="email", summary="Sent quote — ₹4.1L for initial order"),
            TimelineEvent(date=_days_ago(5), type="whatsapp", summary="Harpreet raised shipping cost concern"),
        ],
    },
    {
        "id": "lead-007",
        "company_name": "Noor Textiles",
        "contact_person": "Fatima Noor",
        "phone_number": "+91 98210 44007",
        "deal_value": 160000,
        "stage": "follow-up",
        "next_action": "Ask about sample quality and next steps",
        "last_contact_time": _days_ago(9),
        "revenue_at_risk": 80000,
        "urgency_text": "Samples sent 9 days ago — no feedback yet",
        "ai_reasoning": "Fatima requested samples of our textile packaging materials. We shipped them 9 days ago. No feedback yet. This could mean she's still evaluating or has deprioritized. A gentle check-in is appropriate.",
        "conversation_summary": "Noor Textiles needs custom packaging for their garment export business. Fatima liked the initial pitch and asked for samples. Samples were couriered but no response on quality/feedback.",
        "conversation_signals": [
            "Requested samples — strong interest signal",
            "9 days without feedback — needs a nudge",
            "Export business — time-sensitive procurement",
        ],
        "last_message_snippet": "You: Samples dispatched! Tracking: DL4829371. Should reach you by Thursday.",
        "whatsapp_preview_messages": [
            WhatsAppMessage(sender="them", text="Can you send samples of the garment packaging in medium and large?", time=_time_ago(240)),
            WhatsAppMessage(sender="you", text="Absolutely! Sending both sizes via courier today.", time=_time_ago(238)),
            WhatsAppMessage(sender="you", text="Samples dispatched! Tracking: DL4829371. Should reach you by Thursday.", time=_time_ago(230)),
        ],
        "generated_followup_message": "Hi Fatima, hope you received the packaging samples! Would love to hear your feedback on the quality and sizing. If they work for your garment exports, I can prepare a custom quote for your first batch. Let me know!",
        "conversion_probability": 50,
        "days_inactive": 9,
        "interaction_timeline": [
            TimelineEvent(date=_days_ago(20), type="call", summary="Cold call — discussed garment export packaging needs"),
            TimelineEvent(date=_days_ago(14), type="whatsapp", summary="Fatima asked for samples in medium and large"),
            TimelineEvent(date=_days_ago(9), type="whatsapp", summary="Samples dispatched via courier"),
        ],
    },
    {
        "id": "lead-008",
        "company_name": "Reddy & Co. Supplies",
        "contact_person": "Anil Reddy",
        "phone_number": "+91 98210 44008",
        "deal_value": 320000,
        "stage": "quoted",
        "next_action": "Call to discuss quote and address any concerns",
        "last_contact_time": _days_ago(4),
        "revenue_at_risk": 96000,
        "urgency_text": "Quote under review — decision expected by Friday",
        "ai_reasoning": "Anil mentioned his team would review the quote by end of week. It's been 4 days. A timely call can nudge the decision in our favor and address last-minute concerns before they become objections.",
        "conversation_summary": "Reddy & Co. needs industrial safety equipment for their manufacturing units. Detailed quote sent covering PPE, fire safety, and signage. Anil said his procurement team would review.",
        "conversation_signals": [
            "Gave a decision timeline — serious buyer",
            "Procurement team involved — B2B process",
            "No objections raised yet",
            "Asked about bulk discount tiers",
        ],
        "last_message_snippet": "Anil: Got the quote. Our procurement team will review it this week. I'll circle back.",
        "whatsapp_preview_messages": [
            WhatsAppMessage(sender="you", text="Hi Anil, here's the detailed quote for safety equipment across your 3 manufacturing units.", time=_time_ago(110)),
            WhatsAppMessage(sender="them", text="Got the quote. Our procurement team will review it this week. I'll circle back.", time=_time_ago(96)),
        ],
        "generated_followup_message": "Hi Anil, just checking in on the safety equipment quote. If your procurement team has any questions or needs clarification on specs/pricing, I'm happy to jump on a quick call. We can also offer an additional 3% for orders confirmed this week. Let me know!",
        "conversion_probability": 55,
        "days_inactive": 4,
        "interaction_timeline": [
            TimelineEvent(date=_days_ago(40), type="email", summary="Inbound inquiry — industrial safety equipment for manufacturing"),
            TimelineEvent(date=_days_ago(32), type="meeting", summary="Site visit to assess safety requirements"),
            TimelineEvent(date=_days_ago(15), type="email", summary="Sent comprehensive quote — ₹3.2L"),
            TimelineEvent(date=_days_ago(4), type="whatsapp", summary="Anil confirmed procurement team is reviewing"),
        ],
    },
    {
        "id": "lead-009",
        "company_name": "Joshi Agro Products",
        "contact_person": "Manoj Joshi",
        "phone_number": "+91 98210 44009",
        "deal_value": 210000,
        "stage": "new",
        "next_action": "Schedule a call to understand specific requirements",
        "last_contact_time": _days_ago(1),
        "revenue_at_risk": 0,
        "urgency_text": "Fresh referral — act quickly",
        "ai_reasoning": "Manoj was referred by an existing customer (Raj Traders). Referral leads convert 3x better. He's looking for agricultural packaging supplies. Fast follow-up will leverage the warm introduction.",
        "conversation_summary": "Referral from Suresh at Raj Traders. Manoj runs an agro products company and needs specialized packaging for grain and spice exports. Initial WhatsApp exchange — seems interested.",
        "conversation_signals": [
            "Referral from existing customer — high trust",
            "Export business — recurring need",
            "Responded within hours — engaged",
        ],
        "last_message_snippet": "Manoj: Suresh mentioned you guys do great packaging work. We export grains and spices — looking for a reliable supplier.",
        "whatsapp_preview_messages": [
            WhatsAppMessage(sender="them", text="Hi, Suresh from Raj Traders recommended you. We export grains and spices — looking for a reliable packaging supplier.", time=_time_ago(24)),
            WhatsAppMessage(sender="you", text="Hi Manoj! Thanks for reaching out. Suresh is a great partner. Would love to understand your requirements. Free for a call tomorrow?", time=_time_ago(22)),
        ],
        "generated_followup_message": "Hi Manoj, following up on our chat yesterday. I'd love to understand your export packaging needs in more detail — volumes, destinations, and any compliance requirements. Would a 20-minute call work today or tomorrow? I can share relevant case studies from similar agro export businesses we work with.",
        "conversion_probability": 60,
        "days_inactive": 1,
        "interaction_timeline": [
            TimelineEvent(date=_days_ago(1), type="whatsapp", summary="Referral introduction from Raj Traders — initial exchange"),
        ],
    },
    {
        "id": "lead-010",
        "company_name": "Choudhary Steel Works",
        "contact_person": "Ravi Choudhary",
        "phone_number": "+91 98210 44010",
        "deal_value": 135000,
        "stage": "follow-up",
        "next_action": "Send monthly newsletter and check in next quarter",
        "last_contact_time": _days_ago(25),
        "revenue_at_risk": 40500,
        "urgency_text": "25 days inactive — likely deprioritized",
        "ai_reasoning": "Ravi's requirement seems to be on hold due to internal budget delays. He mentioned revisiting in Q3. Not worth aggressive follow-up now but should stay on radar. A light-touch monthly check-in is sufficient.",
        "conversation_summary": "Choudhary Steel Works was exploring packaging solutions for their hardware distribution. Initial interest was strong but Ravi mentioned budget freeze until Q3. Deal is on hold.",
        "conversation_signals": [
            "Budget freeze mentioned — timing issue, not interest issue",
            "Said 'revisit in Q3' — future opportunity",
            "25-day gap expected given context",
        ],
        "last_message_snippet": "Ravi: We'll have to put this on hold until Q3 budgets are approved. Will reach out when ready.",
        "whatsapp_preview_messages": [
            WhatsAppMessage(sender="them", text="We'll have to put this on hold until Q3 budgets are approved. Will reach out when ready.", time=_time_ago(600)),
            WhatsAppMessage(sender="you", text="Understood, Ravi. No rush at all. I'll keep you in the loop on any new products or offers.", time=_time_ago(598)),
        ],
        "generated_followup_message": "Hi Ravi, hope things are going well at Choudhary Steel! Just a quick note — we've launched some new packaging solutions that might be a good fit for hardware distribution. No rush, but happy to share details whenever Q3 planning kicks in. Cheers!",
        "conversion_probability": 20,
        "days_inactive": 25,
        "interaction_timeline": [
            TimelineEvent(date=_days_ago(50), type="call", summary="Initial inquiry — packaging for hardware distribution"),
            TimelineEvent(date=_days_ago(40), type="email", summary="Sent catalog and quote — ₹1.35L"),
            TimelineEvent(date=_days_ago(25), type="whatsapp", summary="Ravi mentioned budget freeze, deal on hold until Q3"),
        ],
    },
]


def _build_lead(d: dict) -> Lead:
    msgs = d.get("whatsapp_preview_messages", [])
    timeline = d.get("interaction_timeline", [])
    return Lead(
        **{
            **d,
            "whatsapp_preview_messages": [
                m if isinstance(m, WhatsAppMessage) else WhatsAppMessage(**m)
                for m in msgs
            ],
            "interaction_timeline": [
                t if isinstance(t, TimelineEvent) else TimelineEvent(**t)
                for t in timeline
            ],
        }
    )


def init_leads() -> dict[str, Lead]:
    """Build the in-memory store with deterministic scoring applied."""
    store: dict[str, Lead] = {}
    for raw in _seed:
        lead = _build_lead(raw)
        score, label = compute_score_and_label(
            days_inactive=lead.days_inactive,
            deal_value=lead.deal_value,
            revenue_at_risk=lead.revenue_at_risk,
            conversion_probability=lead.conversion_probability,
            stage=lead.stage,
        )
        rec_text = f"{lead.company_name} — {lead.next_action}" if lead.next_action else f"{lead.company_name} — {label}"
        lead = lead.model_copy(update={
            "priority_score": score,
            "ai_recommendation": label,
            "recommendation_text": rec_text,
        })
        store[lead.id] = lead
    return store
