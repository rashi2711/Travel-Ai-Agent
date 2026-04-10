# ✈️ TravelMind AI — Travel Assistant + Business Analytics Dashboard

A production-grade full-stack AI application built with Streamlit, MongoDB, and OpenAI/Gemini.

---

## 🗂️ Project Structure

```
travel_ai/
├── app.py                  ← Main entry point (run this)
├── .env.example            ← Environment variable template
├── requirements.txt        ← Python dependencies
├── README.md               ← This file
│
├── ai/
│   ├── __init__.py
│   ├── llm.py              ← Unified LLM client (OpenAI / Gemini / Demo)
│   └── itinerary.py        ← Itinerary generator, dynamic pricing, recommendations
│
├── database/
│   ├── __init__.py
│   ├── connection.py       ← MongoDB + in-memory fallback
│   ├── users.py            ← Auth (bcrypt) + preferences
│   ├── chats.py            ← Per-user chat history
│   └── bookings.py         ← 800-row mock data + query helpers
│
└── utils/
    ├── __init__.py
    ├── ui.py               ← Dark luxury CSS + UI components
    └── charts.py           ← 6 Plotly chart types
```

---

## 🚀 Quick Start

### 1. Clone / Download
```bash
# If using git:
git clone <your-repo>
cd travel_ai

# Or just extract the project folder
cd travel_ai
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate:
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
# Choose ONE AI provider:
OPENAI_API_KEY=sk-your-key-here      # OpenAI
GEMINI_API_KEY=your-key-here         # OR Google Gemini

AI_PROVIDER=openai                   # openai | gemini | demo

# MongoDB (optional — falls back to in-memory if unavailable):
MONGODB_URI=mongodb://localhost:27017
DB_NAME=travel_ai
```

### 5. Run the App
```bash
streamlit run app.py
```

Open your browser at: **http://localhost:8501**

---

## 🔑 Demo Credentials

The app auto-creates a demo account on first run:
- **Username:** `demo`
- **Password:** `demo123`

---

## 🤖 AI Providers

### Option A: Demo Mode (no API key)
Works out of the box with pre-built responses for popular Indian destinations. 
Set `AI_PROVIDER=demo` in `.env`.

### Option B: OpenAI (GPT-4o-mini)
1. Get API key: https://platform.openai.com/api-keys
2. Set in `.env`: `OPENAI_API_KEY=sk-...` and `AI_PROVIDER=openai`
3. Cost: ~$0.01–0.05 per itinerary (very affordable)

### Option C: Google Gemini (gemini-1.5-flash)
1. Get API key: https://makersuite.google.com/app/apikey
2. Set in `.env`: `GEMINI_API_KEY=...` and `AI_PROVIDER=gemini`
3. Free tier available (60 requests/minute)

---

## 🗄️ Database Setup

### Option A: No MongoDB (in-memory fallback)
Leave `MONGODB_URI` blank or unreachable. The app automatically falls back to 
an in-memory store. Data resets on app restart.

### Option B: Local MongoDB
```bash
# Install MongoDB: https://www.mongodb.com/try/download/community
# Start MongoDB:
mongod --dbpath /data/db
```
Set: `MONGODB_URI=mongodb://localhost:27017`

### Option C: MongoDB Atlas (Cloud, Free Tier)
1. Create free account: https://www.mongodb.com/cloud/atlas
2. Create a cluster → Get connection string
3. Set: `MONGODB_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/`

---

## 📊 Features Overview

### 💬 AI Travel Chat
- Natural language trip planning
- Maintains conversation history per user
- Context-aware multi-turn conversations
- Supports queries like:
  - "Plan a 5-day trip to Goa under ₹15,000"
  - "Best places to visit in winter in India"
  - "Family trip to Kerala for 4 people, ₹60,000 budget"

### 🗺️ Itinerary Builder
- Structured form for trip parameters
- Day-wise itinerary generation
- Budget breakdown tables
- Destination recommendation engine
- Download itinerary as Markdown

### 🏷️ Dynamic Pricing Suggester
- AI-powered demand analysis
- Price multiplier recommendations
- Demand score (0–100)
- Visual price comparison chart
- Supports: packages, flights, hotels, activities, transport

### 📊 Analytics Dashboard
- **KPIs:** GMV, Revenue, Bookings, Conversion Rate, Repeat Customers, CAC
- **Charts:**
  - GMV vs Revenue (monthly trend)
  - Channel Performance (horizontal bar)
  - Conversion by Vertical (grouped bar + line)
  - Revenue Heatmap (month × channel)
  - CAC vs Revenue Scatter
  - Destination Popularity (donut)
- Filters: Date range, Channel, Vertical
- 800-row realistic mock dataset (auto-seeded)

### ⚙️ User Preferences
- Budget range preference
- Travel style preference
- Favourite destinations
- Account information

---

## 🏗️ Architecture Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| UI Framework | Streamlit | Rapid prototyping, Python-native |
| Database | MongoDB + in-memory fallback | Flexible schema, graceful degradation |
| AI | Multi-provider (OpenAI/Gemini/Demo) | Flexibility, no vendor lock-in |
| Auth | bcrypt + SHA-256 fallback | Secure, portable |
| Charts | Plotly | Interactive, dark theme support |
| Caching | `@st.cache_resource` | MongoDB connection caching |

---

## 🔧 Customization

### Change AI Model
In `ai/llm.py`, update:
```python
model="gpt-4o-mini"   # → gpt-4o, gpt-3.5-turbo, etc.
model_name="gemini-1.5-flash"  # → gemini-1.5-pro, etc.
```

### Change Color Theme
In `utils/ui.py`, update CSS variables:
```css
--accent-gold: #d4a843;    /* Primary accent */
--accent-teal: #2dd4bf;    /* Secondary accent */
--bg-primary: #0a0e1a;     /* Main background */
```

### Add More Destinations to Demo Mode
In `ai/llm.py`, add entries to `_DEMO_ITINERARIES` dict and corresponding 
handler functions.

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| MongoDB connection fails | App auto-falls back to in-memory. Check URI in `.env`. |
| OpenAI rate limit | Switch to Gemini or Demo mode temporarily |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` in activated venv |
| bcrypt import error | Run `pip install bcrypt` — app has SHA-256 fallback |
| Charts not rendering | Clear Streamlit cache: `streamlit cache clear` |
| Slow itinerary generation | Normal — LLM calls take 3–15 seconds |

---

## 📦 Production Deployment

### Streamlit Cloud (Free)
1. Push code to GitHub (add `.env` to `.gitignore`)
2. Go to https://share.streamlit.io
3. Connect repo → set secrets in dashboard
4. Deploy!

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t travelmind .
docker run -p 8501:8501 --env-file .env travelmind
```

---

## 📄 License
MIT — Free to use, modify, and distribute.
