"""
ai/itinerary.py
AI-powered itinerary generator, dynamic pricing suggester,
and travel recommendation engine.
"""

from __future__ import annotations
import json
import re
from ai.llm import chat, _detect_provider

# ── Itinerary Generator ────────────────────────────────────────────────────
def generate_itinerary(
    destination: str,
    days: int,
    budget: int,
    travelers: int = 1,
    style: str = "leisure",
    preferences: list[str] | None = None,
) -> str:
    """
    Generate a detailed travel itinerary using the configured LLM.
    Returns markdown-formatted string.
    """
    pref_str = ", ".join(preferences) if preferences else "no specific preferences"
    prompt = f"""Create a detailed {days}-day travel itinerary for {destination}.

Parameters:
- Total budget: ₹{budget:,} for {travelers} person(s)
- Travel style: {style}
- Preferences: {pref_str}

Please provide:
1. Complete day-wise itinerary with morning, afternoon, evening activities
2. Exact budget breakdown table in INR
3. Recommended accommodation (with price range)
4. Local food recommendations with approximate prices
5. Transport tips within the destination
6. Packing checklist (5-7 items)
7. Important tips & warnings
8. Best season to visit

Format everything clearly with headers, tables, and emojis for readability."""

    messages = [{"role": "user", "content": prompt}]
    return chat(messages)


# ── Dynamic Pricing Suggestion ─────────────────────────────────────────────
def get_dynamic_pricing(
    destination: str,
    travel_date: str,
    vertical: str = "packages",
    base_price: float = 10000,
) -> dict:
    """
    Suggest dynamic pricing based on demand signals.
    Returns dict with suggested_price, demand_level, and reasoning.
    """
    prompt = f"""You are a travel pricing analyst. Analyze demand and suggest dynamic pricing.

Input:
- Destination: {destination}
- Travel Date: {travel_date}
- Product Type: {vertical}
- Base Price: ₹{base_price:,.0f}

Respond ONLY with valid JSON (no markdown, no explanation outside JSON):
{{
  "demand_level": "low|medium|high|surge",
  "demand_score": 0-100,
  "price_multiplier": 0.7-2.5,
  "suggested_price": <calculated>,
  "factors": ["factor1", "factor2", "factor3"],
  "recommendation": "one sentence pricing recommendation"
}}"""

    messages = [{"role": "user", "content": prompt}]
    raw = chat(messages)

    try:
        # Strip markdown fences if present
        clean = re.sub(r"```(?:json)?|```", "", raw).strip()
        data = json.loads(clean)
        data["suggested_price"] = round(base_price * data.get("price_multiplier", 1.0), 0)
        return data
    except Exception:
        # Fallback: rule-based pricing
        return _rule_based_pricing(destination, travel_date, base_price)


def _rule_based_pricing(destination: str, travel_date: str, base_price: float) -> dict:
    """Fallback rule-based dynamic pricing."""
    import datetime
    try:
        dt = datetime.datetime.strptime(travel_date, "%Y-%m-%d")
    except Exception:
        dt = datetime.datetime.now()

    month = dt.month
    # Peak season: Oct–Feb for most India destinations
    peak_months = [10, 11, 12, 1, 2]
    is_weekend = dt.weekday() >= 5
    is_peak = month in peak_months

    multiplier = 1.0
    if is_peak:
        multiplier += 0.3
    if is_weekend:
        multiplier += 0.15
    if destination.lower() in ["goa", "kerala", "andaman"]:
        multiplier += 0.1

    level = "low"
    if multiplier > 1.4:
        level = "surge"
    elif multiplier > 1.2:
        level = "high"
    elif multiplier > 1.0:
        level = "medium"

    factors = []
    if is_peak:
        factors.append("Peak season demand")
    if is_weekend:
        factors.append("Weekend premium")
    factors.append("Destination popularity score")

    return {
        "demand_level": level,
        "demand_score": int((multiplier - 0.7) / 1.8 * 100),
        "price_multiplier": round(multiplier, 2),
        "suggested_price": round(base_price * multiplier, 0),
        "factors": factors,
        "recommendation": f"Apply {multiplier:.1f}x multiplier based on seasonal demand patterns.",
    }


# ── Travel Recommendation Engine ───────────────────────────────────────────
def get_recommendations(
    budget: int,
    season: str,
    interests: list[str],
    duration: int = 5,
    from_city: str = "Delhi",
) -> str:
    """
    Generate personalised destination recommendations.
    """
    interest_str = ", ".join(interests) if interests else "general sightseeing"
    prompt = f"""You are an expert Indian travel curator. Recommend the BEST destinations.

Traveler Profile:
- Budget: ₹{budget:,} total
- Season: {season}
- Interests: {interest_str}
- Trip Duration: {duration} days
- Departing From: {from_city}

Provide:
1. Top 3 destination recommendations with brief reasoning
2. For each destination: estimated cost, highlight, and best activity
3. One hidden gem destination (less touristy)
4. Quick comparison table

Be specific with costs and practical. Use emojis generously."""

    messages = [{"role": "user", "content": prompt}]
    return chat(messages)


# ── Quick helpers for the UI ───────────────────────────────────────────────
def extract_trip_params(user_message: str) -> dict:
    """
    Try to extract trip parameters from a natural language query.
    Returns a dict with destination, days, budget if detectable.
    """
    params = {}
    msg = user_message.lower()

    # Days
    days_match = re.search(r"(\d+)[- ]day", msg)
    if days_match:
        params["days"] = int(days_match.group(1))

    # Budget
    budget_match = re.search(r"(?:under|within|budget of|₹|rs\.?|inr)[\s]?([\d,]+)", msg)
    if budget_match:
        params["budget"] = int(budget_match.group(1).replace(",", ""))

    # Common destinations
    destinations = [
        "goa", "kerala", "rajasthan", "manali", "shimla", "himachal",
        "andaman", "ladakh", "leh", "rishikesh", "varanasi", "jaipur",
        "udaipur", "darjeeling", "ooty", "coorg", "munnar", "alleppey",
        "agra", "delhi", "mumbai", "bangalore", "mysore", "hampi",
    ]
    for dest in destinations:
        if dest in msg:
            params["destination"] = dest.title()
            break

    return params
