"""
ai/llm.py
Unified LLM client — supports OpenAI, Google Gemini, and Demo (offline) mode.
Auto-detects provider from environment variables.
"""

from __future__ import annotations
import os
import json
import random
from dotenv import load_dotenv

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "demo").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

SYSTEM_PROMPT = """You are TravelMind AI — an expert Indian travel assistant and itinerary planner.

Your capabilities:
1. Create detailed day-wise travel itineraries
2. Provide accurate budget breakdowns in INR
3. Recommend destinations based on season, budget, and preferences
4. Suggest local food, transport options, and hidden gems
5. Handle trip planning for solo, couple, family, and group travel

Guidelines:
- Always respond in a friendly, enthusiastic tone
- Structure itineraries clearly with Day 1, Day 2, etc.
- Include budget breakdowns: flights, accommodation, food, activities, transport, miscellaneous
- Mention best season to visit, local tips, and packing suggestions
- If budget is tight, suggest cost-saving alternatives
- Always ask clarifying questions if the request is too vague
- Use INR (₹) for all prices
- Format responses with clear sections using markdown

Remember: You serve users planning travel in India primarily, but can handle international queries too."""


# ── Public API ─────────────────────────────────────────────────────────────
def chat(messages: list[dict], stream: bool = False) -> str:
    """
    Send a conversation to the configured LLM and return the response string.

    messages: list of {"role": "user"/"assistant", "content": "..."}
    """
    provider = _detect_provider()

    if provider == "openai":
        return _openai_chat(messages)
    elif provider == "gemini":
        return _gemini_chat(messages)
    else:
        return _demo_chat(messages)


def get_provider_name() -> str:
    return _detect_provider().upper()


# ── Provider detection ─────────────────────────────────────────────────────
def _detect_provider() -> str:
    if AI_PROVIDER == "openai" and OPENAI_API_KEY.startswith("sk-"):
        return "openai"
    if AI_PROVIDER == "gemini" and GEMINI_API_KEY:
        return "gemini"
    # Auto-fallback: try keys in env even if provider not explicitly set
    if OPENAI_API_KEY.startswith("sk-"):
        return "openai"
    if GEMINI_API_KEY:
        return "gemini"
    return "demo"


# ── OpenAI ─────────────────────────────────────────────────────────────────
def _openai_chat(messages: list[dict]) -> str:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        response = client.chat.completions.create(
            model="gpt-4o-mini",          # cost-effective; swap to gpt-4o if needed
            messages=full_messages,
            max_tokens=2000,
            temperature=0.7,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"⚠️ OpenAI error: {e}\n\nFalling back to demo mode.\n\n{_demo_chat(messages)}"


# ── Gemini ─────────────────────────────────────────────────────────────────
def _gemini_chat(messages: list[dict]) -> str:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(
           model_name="gemini-2.0-flash",
            system_instruction=SYSTEM_PROMPT,
        )

        # Convert to Gemini format
        history = []
        for m in messages[:-1]:
            history.append({
                "role": "user" if m["role"] == "user" else "model",
                "parts": [m["content"]],
            })

        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(messages[-1]["content"])
        return response.text or ""
    except Exception as e:
        return f"⚠️ Gemini error: {e}\n\nFalling back to demo mode.\n\n{_demo_chat(messages)}"


# ── Demo mode (no API key needed) ──────────────────────────────────────────
_DEMO_ITINERARIES = {
    "goa": """## 🌴 5-Day Goa Trip Under ₹15,000

### Budget Breakdown
| Category | Cost |
|----------|------|
| ✈️ Flights (roundtrip, from Delhi) | ₹5,500 |
| 🏨 Hostel / Budget Guesthouse (4 nights) | ₹3,200 |
| 🍽️ Food (₹400/day) | ₹2,000 |
| 🛵 Scooter Rental (4 days) | ₹1,600 |
| 🎭 Activities & Entry Fees | ₹1,200 |
| 🎒 Miscellaneous | ₹1,500 |
| **Total** | **₹15,000** |

---

### Day-wise Itinerary

**Day 1 — Arrival + North Goa Beaches**
- Land at Goa Airport, check into hostel in Calangute/Anjuna
- Evening: Stroll Calangute Beach, sunset at Baga Beach
- Dinner at a beach shack (~₹300)

**Day 2 — North Goa Exploration**
- Morning: Aguada Fort & Sinquerim Beach
- Afternoon: Chapora Fort (Dil Chahta Hai fame 🎬)
- Evening: Anjuna Flea Market (Wednesdays) or Vagator Beach
- Try: Seafood thali (~₹180)

**Day 3 — Old Goa + Cultural Day**
- Morning: Basilica of Bom Jesus, Se Cathedral
- Afternoon: Fontainhas Latin Quarter walk
- Evening: Panaji waterfront, Mandovi River cruise (₹200)

**Day 4 — South Goa Beaches**
- Colva Beach, Benaulim Beach — much quieter than North
- Visit Cabo de Rama Fort
- Sunset at Palolem Beach

**Day 5 — Water Sports + Departure**
- Morning: Parasailing / Jet-ski at Calangute (book combo for ₹800)
- Checkout & head to airport

### 💡 Pro Tips
- Visit Oct–Feb for best weather
- Book flights 3–4 weeks in advance for cheap fares
- Carry cash — many shacks don't accept cards
- Dudhsagar Waterfall day trip: ₹800 (jeep safari)""",

    "default": """## 🗺️ AI Travel Itinerary

I'm running in **Demo Mode** (no API key configured).

Here's what I can help with when connected to a real AI:
- 📅 Custom day-wise itineraries for any destination
- 💰 Detailed budget breakdowns in INR
- 🌦️ Best season recommendations
- 🏨 Accommodation options (budget to luxury)
- 🍜 Local food recommendations
- 🚂 Transport planning

### To enable real AI responses:
1. Get an API key from [OpenAI](https://platform.openai.com) or [Google AI](https://makersuite.google.com)
2. Add it to your `.env` file
3. Restart the app

**Meanwhile, try asking about:** Goa, Kerala, Rajasthan, Himachal Pradesh, or Andaman!"""
}


def _demo_chat(messages: list[dict]) -> str:
    """Intelligent demo responses without an API key."""
    last_msg = messages[-1]["content"].lower() if messages else ""

    # Detect destination keywords
    dest_responses = {
        "goa": _DEMO_ITINERARIES["goa"],
        "kerala": _kerala_demo(),
        "rajasthan": _rajasthan_demo(),
        "himachal": _himachal_demo(),
        "manali": _himachal_demo(),
    }

    for keyword, response in dest_responses.items():
        if keyword in last_msg:
            return response

    # Generic helpful responses
    if any(w in last_msg for w in ["hello", "hi", "hey", "namaste"]):
        return """👋 **Namaste! Welcome to TravelMind AI!**

I'm your personal Indian travel assistant. I can help you:

🗺️ **Plan Trips** — "Plan a 5-day trip to Goa under ₹15,000"
🏔️ **Find Destinations** — "Best hill stations in summer under ₹20,000"
🌴 **Seasonal Tips** — "Where to go in December in India?"
💰 **Budget Planning** — "Kerala trip for 2 people with ₹30,000 budget"

> ⚠️ Running in **Demo Mode** — add an API key for full AI capabilities!

What trip shall we plan today? 🚀"""

    if any(w in last_msg for w in ["budget", "cheap", "affordable"]):
        return _budget_tips_demo()

    if any(w in last_msg for w in ["winter", "december", "january", "cold"]):
        return _winter_destinations_demo()

    if any(w in last_msg for w in ["summer", "may", "june", "hot"]):
        return _summer_destinations_demo()

    return _DEMO_ITINERARIES["default"]


def _kerala_demo() -> str:
    return """## 🌿 Kerala — God's Own Country

### Suggested 6-Day Itinerary

**Day 1-2: Munnar (Hill Station)**
- Tea garden walks, Eravikulam National Park
- Echo Point, Mattupetty Dam
- Budget: ₹2,500/day

**Day 3: Alleppey (Backwaters)**
- Houseboat experience (budget: ₹3,500–8,000/night)
- Sunset on the backwaters 🌅

**Day 4-5: Kochi (City + Culture)**
- Fort Kochi, Chinese fishing nets
- Kathakali dance show (₹350)
- Kerala seafood thali (₹250)

**Day 6: Kovalam Beach**
- Relax, Ayurvedic massage (~₹800)

### Budget (2 persons, 6 days)
| Item | Cost |
|------|------|
| Flights | ₹9,000 |
| Stay | ₹12,000 |
| Food | ₹6,000 |
| Transport | ₹4,000 |
| Activities | ₹5,000 |
| **Total** | **~₹36,000** |

💡 **Best time**: October to February"""


def _rajasthan_demo() -> str:
    return """## 🏰 Rajasthan Royal Tour

### 7-Day Golden Triangle + Rajasthan

**Day 1-2: Jaipur (Pink City)**
- Amber Fort, City Palace, Hawa Mahal
- Local bazaar shopping
- Try: Dal Baati Churma

**Day 3-4: Jodhpur (Blue City)**
- Mehrangarh Fort (₹100 entry)
- Clock Tower market
- Sunset at Umaid Bhawan

**Day 5-6: Jaisalmer (Desert)**
- Sam Sand Dunes camel safari (₹500)
- Patwon ki Haveli
- Desert camping (₹1,800/night)

**Day 7: Udaipur (Lake City)**
- City Palace, Lake Pichola boat ride
- Bagore ki Haveli cultural show

### Budget per person
**Economy**: ₹18,000 | **Mid**: ₹32,000 | **Luxury**: ₹65,000+

💡 **Best time**: October to March"""


def _himachal_demo() -> str:
    return """## 🏔️ Manali Adventure Trip

### 5-Day Itinerary

**Day 1: Arrival + Old Manali**
- Mall Road evening walk
- Try: Siddu (local bread) & Trout fish

**Day 2: Solang Valley**
- Zorbing, paragliding (₹1,500)
- Rohtang Pass permit (₹600)

**Day 3: Rohtang Pass / Atal Tunnel**
- Snow activities, Sissu village
- Chandratal Lake viewpoint

**Day 4: Kullu + River Rafting**
- Beas River rafting (₹600)
- Manikaran Sahib hot springs

**Day 5: Departure**

### Budget (Solo, 5 days)
| Item | Cost |
|------|------|
| Bus (Volvo from Delhi) | ₹1,600 |
| Hostel (4 nights) | ₹2,800 |
| Food | ₹2,500 |
| Activities | ₹3,500 |
| Local transport | ₹1,600 |
| **Total** | **~₹12,000** |

💡 **Best time**: May–June and Oct–Nov"""


def _budget_tips_demo() -> str:
    return """## 💰 Budget Travel Tips for India

### Top Budget Destinations
1. **Rishikesh** — from ₹800/night (yoga + rafting)
2. **Varanasi** — from ₹600/night (spiritual + cultural)
3. **Hampi** — from ₹500/night (UNESCO heritage)
4. **Pushkar** — from ₹700/night (desert + festivals)
5. **Mcleod Ganj** — from ₹900/night (mountains + culture)

### Money-Saving Hacks
- 🚂 Book **Tatkal** train tickets 1 day before (save vs flights)
- 🏨 Use **Zostel** or **Gostops** for quality hostels
- 🍛 Eat at **dhaba** restaurants (₹80–150/meal)
- 🚌 Night buses = save on accommodation + transport
- 📱 Use **Redbus** and **IRCTC Rail Connect** apps

### Cheapest Months to Travel
| Season | Months | Savings |
|--------|--------|---------|
| Monsoon | Jul–Sep | 40–60% off |
| Off-peak | Apr–May | 20–30% off |
| Peak | Oct–Feb | Full price |"""


def _winter_destinations_demo() -> str:
    return """## ❄️ Best Winter Destinations in India (Dec–Feb)

### 🔥 Warm Escapes
| Destination | Temp | Budget/Person |
|-------------|------|---------------|
| **Goa** | 22–28°C | ₹12,000–25,000 |
| **Kerala** | 23–30°C | ₹15,000–35,000 |
| **Andaman** | 25–30°C | ₹20,000–40,000 |
| **Rajasthan** | 10–20°C | ₹12,000–30,000 |
| **Karnataka Coast** | 26–32°C | ₹8,000–20,000 |

### ❄️ Snow Experiences
| Destination | Activity | Cost |
|-------------|----------|------|
| **Shimla** | Snow sightseeing | ₹8,000–15,000 |
| **Auli** | Skiing | ₹12,000–25,000 |
| **Chopta** | Trekking | ₹6,000–12,000 |
| **Spiti Valley** | Winter trek | ₹15,000–30,000 |

💡 December 20 – January 10 is peak season — book 2 months ahead!"""


def _summer_destinations_demo() -> str:
    return """## ☀️ Best Summer Destinations in India (Apr–Jun)

### 🏔️ Escape the Heat — Hill Stations
| Destination | Temp | Why Visit |
|-------------|------|-----------|
| **Manali** | 10–20°C | Adventure, snow |
| **Shimla** | 15–25°C | Colonial charm |
| **Darjeeling** | 12–22°C | Tea gardens, Everest view |
| **Ooty** | 14–24°C | Nilgiri toy train |
| **Coorg** | 18–28°C | Coffee, waterfalls |

### 🌊 Beach Options (monsoon coming, fewer crowds)
- **Andaman** — best snorkeling before Jul rains
- **Lakshadweep** — restricted but pristine

### Budget Tip for Summer
✅ Summer = **30–40% cheaper** than peak winter season
✅ Avoid Goa in summer (monsoon starts June)
✅ Leh-Ladakh opens May–June — book early!"""
