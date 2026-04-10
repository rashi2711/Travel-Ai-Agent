"""
database/bookings.py
Booking data management + 800-row realistic mock data seeder.
"""

from __future__ import annotations
import random
from datetime import datetime, timedelta
from database.connection import get_db

# ── Constants ──────────────────────────────────────────────────────────────
DESTINATIONS = [
    "Goa", "Kerala", "Rajasthan", "Himachal Pradesh", "Uttarakhand",
    "Andaman", "Leh-Ladakh", "Manali", "Rishikesh", "Varanasi",
    "Agra", "Jaipur", "Mumbai", "Delhi", "Bangalore",
    "Ooty", "Coorg", "Darjeeling", "Sikkim", "Meghalaya",
]
CHANNELS = ["organic", "google_ads", "instagram", "referral", "email", "direct"]
VERTICALS = ["flights", "hotels", "packages", "activities", "transport"]
STATUSES = ["confirmed", "cancelled", "pending", "completed"]

PRICE_RANGES = {
    "flights": (3000, 18000),
    "hotels": (1500, 12000),
    "packages": (8000, 75000),
    "activities": (500, 5000),
    "transport": (800, 6000),
}
REVENUE_MARGIN = {
    "flights": 0.06,
    "hotels": 0.15,
    "packages": 0.22,
    "activities": 0.30,
    "transport": 0.18,
}
CAC_BY_CHANNEL = {
    "organic": 180,
    "google_ads": 620,
    "instagram": 480,
    "referral": 210,
    "email": 95,
    "direct": 140,
}


# ── Seeder ─────────────────────────────────────────────────────────────────
def seed_bookings(n: int = 800, force: bool = False) -> None:
    """
    Insert `n` realistic bookings into MongoDB.
    Skips seeding if data already exists (unless force=True).
    """
    db = get_db()
    col = db["bookings"]

    if not force and col.count_documents({}) >= n:
        return  # already seeded

    print(f"[DB] Seeding {n} bookings …")
    random.seed(42)

    bookings = []
    base_date = datetime(2024, 1, 1)
    user_pool = [f"user_{i:04d}" for i in range(1, 201)]  # 200 unique users

    for i in range(n):
        vertical = random.choice(VERTICALS)
        channel = random.choices(
            CHANNELS, weights=[25, 20, 18, 15, 12, 10]
        )[0]
        status = random.choices(
            STATUSES, weights=[60, 10, 8, 22]
        )[0]

        gmv = round(random.uniform(*PRICE_RANGES[vertical]), 2)
        revenue = round(gmv * REVENUE_MARGIN[vertical], 2)
        cac = CAC_BY_CHANNEL[channel] + random.randint(-30, 60)

        days_offset = random.randint(0, 364)
        booking_date = base_date + timedelta(days=days_offset)
        travel_date = booking_date + timedelta(days=random.randint(3, 90))

        username = random.choice(user_pool)
        # ~20 % of users book more than once → repeat customer metric
        is_repeat = random.random() < 0.2

        bookings.append({
            "booking_id": f"BK{i+1:05d}",
            "username": username,
            "destination": random.choice(DESTINATIONS),
            "vertical": vertical,
            "channel": channel,
            "status": status,
            "gmv": gmv,
            "revenue": revenue,
            "cac": cac,
            "booking_date": booking_date.isoformat(),
            "travel_date": travel_date.isoformat(),
            "duration_days": random.randint(2, 14),
            "pax": random.randint(1, 6),
            "is_repeat_customer": is_repeat,
            "rating": round(random.uniform(3.0, 5.0), 1) if status == "completed" else None,
            "year": booking_date.year,
            "month": booking_date.month,
            "quarter": f"Q{(booking_date.month - 1) // 3 + 1}",
        })

    col.insert_many(bookings)
    print(f"[DB] ✓ Seeded {n} bookings.")


# ── Query helpers ──────────────────────────────────────────────────────────
def get_bookings_df(
    start_date: str | None = None,
    end_date: str | None = None,
    channels: list[str] | None = None,
    verticals: list[str] | None = None,
):
    """Return bookings as a pandas DataFrame with optional filters."""
    import pandas as pd

    db = get_db()
    filt: dict = {}
    if start_date:
        filt.setdefault("booking_date", {})["$gte"] = start_date
    if end_date:
        filt.setdefault("booking_date", {})["$lte"] = end_date + "T23:59:59"
    if channels:
        filt["channel"] = {"$in": channels}
    if verticals:
        filt["vertical"] = {"$in": verticals}

    cursor = db["bookings"].find(filt)
    df = pd.DataFrame(list(cursor))
    if df.empty:
        return df

    df["booking_date"] = pd.to_datetime(df["booking_date"])
    df["travel_date"] = pd.to_datetime(df["travel_date"])
    return df


def get_kpis(df=None) -> dict:
    """Compute high-level KPIs from booking data."""
    if df is None:
        df = get_bookings_df()

    if df is None or df.empty:
        return {
            "gmv": 0, "revenue": 0, "bookings": 0,
            "conversion_rate": 0, "repeat_rate": 0, "avg_cac": 0,
        }

    confirmed = df[df["status"].isin(["confirmed", "completed"])]
    total = len(df)
    conv = len(confirmed) / total * 100 if total else 0
    repeat = df["is_repeat_customer"].sum() / total * 100 if total else 0

    return {
        "gmv": round(confirmed["gmv"].sum(), 2),
        "revenue": round(confirmed["revenue"].sum(), 2),
        "bookings": total,
        "confirmed": len(confirmed),
        "conversion_rate": round(conv, 1),
        "repeat_rate": round(repeat, 1),
        "avg_cac": round(df["cac"].mean(), 0),
        "avg_rating": round(
            df[df["rating"].notna()]["rating"].mean(), 2
        ) if "rating" in df.columns else 0,
    }
