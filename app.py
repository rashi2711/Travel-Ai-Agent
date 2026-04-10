"""
app.py — AI Travel Assistant + Business Analytics Dashboard
Run with: streamlit run app.py

Architecture:
  app.py          ← Entry point & page router
  ai/             ← LLM client + itinerary generators
  database/       ← MongoDB connection, users, chats, bookings
  utils/          ← UI theme, reusable components, chart factory
"""

import os
import streamlit as st
from dotenv import load_dotenv

# ── Load env first ──────────────────────────────────────────────────────────
load_dotenv()

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="TravelMind AI",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Internal imports (after page config) ───────────────────────────────────
from utils.ui import (
    apply_theme, render_header, render_chat_message,
    render_kpi_card, render_info_box, render_provider_badge,
    loading_placeholder,
)
from utils.charts import (
    gmv_vs_revenue_chart, channel_performance_chart,
    conversion_by_vertical_chart, revenue_heatmap,
    cac_revenue_scatter, destination_popularity_chart,
    format_inr,
)
from database.connection import get_db
from database.users import create_user, authenticate_user, get_user, update_preferences
from database.chats import save_message, get_history, clear_history, get_session_messages
from database.bookings import seed_bookings, get_bookings_df, get_kpis
from ai.llm import chat, get_provider_name
from ai.itinerary import (
    generate_itinerary, get_recommendations,
    get_dynamic_pricing, extract_trip_params,
)

# ── Apply CSS theme ─────────────────────────────────────────────────────────
apply_theme()


# ═══════════════════════════════════════════════════════════════════════════
# SESSION STATE HELPERS
# ═══════════════════════════════════════════════════════════════════════════
def _init_session():
    defaults = {
        "logged_in": False,
        "username": None,
        "page": "chat",          # chat | dashboard | itinerary | pricing
        "chat_messages": [],     # in-memory for current session display
        "db_seeded": False,
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def _is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def _current_user() -> str:
    return st.session_state.get("username", "guest")


# ═══════════════════════════════════════════════════════════════════════════
# AUTH PAGES
# ═══════════════════════════════════════════════════════════════════════════
def page_login():
    """Login / signup page."""
    render_header("TravelMind AI", "Your intelligent travel companion", "✈️")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_signup = st.tabs(["🔑  Sign In", "📝  Create Account"])

        # ── Login ──────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_user", placeholder="your_username")
            password = st.text_input("Password", type="password", key="login_pw", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Sign In →", use_container_width=True, key="btn_login"):
                if username and password:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = username
                        # Load persistent chat history into session
                        history = get_history(username, limit=50)
                        st.session_state["chat_messages"] = [
                            {"role": m["role"], "content": m["content"]} for m in history
                        ]
                        st.success(f"Welcome back, {username}! 🎉")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")
                else:
                    st.warning("Please enter both username and password.")

            st.markdown("<br>", unsafe_allow_html=True)
            render_info_box("Demo: use username <b>demo</b> / password <b>demo123</b>", "info")

        # ── Signup ─────────────────────────────────────────────────────────
        with tab_signup:
            st.markdown("<br>", unsafe_allow_html=True)
            new_user = st.text_input("Choose Username", key="su_user", placeholder="traveller_name")
            new_email = st.text_input("Email (optional)", key="su_email", placeholder="you@email.com")
            new_pw = st.text_input("Password", type="password", key="su_pw", placeholder="min 6 chars")
            new_pw2 = st.text_input("Confirm Password", type="password", key="su_pw2", placeholder="repeat password")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Create Account →", use_container_width=True, key="btn_signup"):
                if not new_user or not new_pw:
                    st.warning("Username and password are required.")
                elif len(new_pw) < 6:
                    st.warning("Password must be at least 6 characters.")
                elif new_pw != new_pw2:
                    st.error("Passwords do not match.")
                else:
                    user = create_user(new_user, new_pw, new_email)
                    if user:
                        st.success("Account created! Please sign in.")
                    else:
                        st.error("Username already taken. Choose another.")

    # ── Feature highlights ─────────────────────────────────────────────────
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, icon, title, desc in [
        (c1, "🤖", "AI Itinerary", "Day-wise plans powered by GPT-4 / Gemini"),
        (c2, "💰", "Budget Planner", "Accurate INR breakdowns for any trip"),
        (c3, "📊", "Analytics", "Real-time business KPIs & dashboards"),
        (c4, "🏷️", "Dynamic Pricing", "AI-driven pricing recommendations"),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div style="font-size:2rem;">{icon}</div>
                <div style="font-weight:600;color:#f1f5f9;margin:6px 0 4px;">{title}</div>
                <div style="font-size:0.8rem;color:#64748b;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR (authenticated)
# ═══════════════════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        # Logo + user info
        st.markdown("""
        <div style="text-align:center;padding:1rem 0 1.5rem;">
            <div style="font-size:2.5rem;">✈️</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.3rem;color:#d4a843;font-weight:700;">
                TravelMind AI
            </div>
        </div>
        """, unsafe_allow_html=True)

        # AI provider badge
        render_provider_badge(get_provider_name())
        st.markdown("<br>", unsafe_allow_html=True)

        # User info
        user = get_user(_current_user())
        trip_count = user.get("total_trips", 0) if user else 0
        st.markdown(f"""
        <div style="background:#1a2235;border-radius:10px;padding:12px;margin-bottom:1rem;">
            <div style="color:#94a3b8;font-size:0.75rem;">SIGNED IN AS</div>
            <div style="color:#f1f5f9;font-weight:600;font-size:1rem;">👤 {_current_user()}</div>
            <div style="color:#64748b;font-size:0.8rem;">🗺️ {trip_count} trips planned</div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        st.markdown("**Navigation**")
        pages = {
            "chat": "💬 AI Travel Chat",
            "itinerary": "🗺️ Itinerary Builder",
            "pricing": "🏷️ Dynamic Pricing",
            "dashboard": "📊 Analytics Dashboard",
            "preferences": "⚙️ Preferences",
        }
        for key, label in pages.items():
            active = st.session_state.get("page") == key
            if st.button(
                label,
                use_container_width=True,
                key=f"nav_{key}",
                type="primary" if active else "secondary",
            ):
                st.session_state["page"] = key
                st.rerun()

        st.divider()

        # Quick tips
        st.markdown("**💡 Try asking:**")
        tips = [
            '"Plan 5-day Goa trip ₹15,000"',
            '"Best winter destinations"',
            '"Kerala itinerary for 2 people"',
            '"Adventure trips in monsoon"',
        ]
        for tip in tips:
            st.markdown(f'<div style="color:#64748b;font-size:0.8rem;margin:3px 0;">→ {tip}</div>', unsafe_allow_html=True)

        st.divider()

        if st.button("🚪 Logout", use_container_width=True):
            for key in ["logged_in", "username", "chat_messages", "page"]:
                st.session_state.pop(key, None)
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: AI TRAVEL CHAT
# ═══════════════════════════════════════════════════════════════════════════
def page_chat():
    st.markdown("## 💬 AI Travel Assistant")
    st.markdown('<p style="color:#64748b;">Ask anything about travel in India or worldwide.</p>', unsafe_allow_html=True)

    # Controls row
    col_clear, col_export, _ = st.columns([1, 1, 5])
    with col_clear:
        if st.button("🗑️ Clear Chat"):
            st.session_state["chat_messages"] = []
            clear_history(_current_user())
            st.rerun()
    with col_export:
        history = get_history(_current_user(), limit=100)
        if history:
            export_text = "\n\n".join(
                [f"[{m['role'].upper()}]\n{m['content']}" for m in history]
            )
            st.download_button(
                "📥 Export",
                data=export_text,
                file_name=f"chat_{_current_user()}.txt",
                mime="text/plain",
            )

    st.divider()

    # Display chat history
    messages = st.session_state.get("chat_messages", [])
    if not messages:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:#64748b;">
            <div style="font-size:3rem;margin-bottom:1rem;">🌏</div>
            <div style="font-size:1.1rem;color:#94a3b8;">Start planning your dream trip!</div>
            <div style="font-size:0.9rem;margin-top:0.5rem;">
                Try: <i>"Plan a 5-day trip to Goa under ₹15,000"</i>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in messages:
            render_chat_message(msg["role"], msg["content"])

    # Chat input
    st.markdown("<br>", unsafe_allow_html=True)
    user_input = st.chat_input("Ask about destinations, itineraries, budgets…", key="chat_input")

    if user_input:
        # Show user message immediately
        st.session_state["chat_messages"].append({"role": "user", "content": user_input})
        save_message(_current_user(), "user", user_input)

        # Get conversation history for context
        history = get_session_messages(_current_user())

        with loading_placeholder("TravelMind is crafting your itinerary…"):
            try:
                response = chat(history)
            except Exception as e:
                response = f"⚠️ Something went wrong: {e}\n\nPlease try again or check your API configuration."

        st.session_state["chat_messages"].append({"role": "assistant", "content": response})
        save_message(_current_user(), "assistant", response)
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: ITINERARY BUILDER
# ═══════════════════════════════════════════════════════════════════════════
def page_itinerary():
    st.markdown("## 🗺️ AI Itinerary Builder")
    st.markdown('<p style="color:#64748b;">Generate detailed day-wise travel plans with budget breakdowns.</p>', unsafe_allow_html=True)

    tab_build, tab_recommend = st.tabs(["📅 Build Itinerary", "🔍 Get Recommendations"])

    # ── Build Itinerary ────────────────────────────────────────────────────
    with tab_build:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            destination = st.text_input(
                "🏖️ Destination",
                placeholder="e.g. Goa, Kerala, Manali",
                key="itin_dest",
            )
            days = st.slider("📅 Trip Duration (days)", 1, 21, 5)
            budget = st.number_input(
                "💰 Total Budget (₹)",
                min_value=2000,
                max_value=500000,
                value=15000,
                step=1000,
            )

        with col2:
            travelers = st.number_input("👥 Number of Travelers", 1, 20, 1)
            style = st.selectbox(
                "🎭 Travel Style",
                ["leisure", "adventure", "cultural", "romantic", "family", "business", "backpacking"],
            )
            preferences = st.multiselect(
                "✨ Preferences",
                ["beaches", "mountains", "history", "food", "shopping", "nightlife",
                 "wildlife", "yoga", "adventure sports", "budget travel", "luxury"],
            )

        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.button("✨ Generate Itinerary", use_container_width=True, key="btn_gen_itin")

        if generate_btn:
            if not destination.strip():
                st.warning("Please enter a destination.")
            else:
                with loading_placeholder(f"Building your {days}-day {destination} itinerary…"):
                    result = generate_itinerary(
                        destination=destination,
                        days=days,
                        budget=budget,
                        travelers=travelers,
                        style=style,
                        preferences=preferences,
                    )

                st.markdown("---")
                st.markdown(result)

                # Save to chat + increment counter
                save_message(_current_user(), "user",
                             f"Generate {days}-day itinerary for {destination} budget ₹{budget:,}")
                save_message(_current_user(), "assistant", result)

                from database.users import increment_trip_count
                increment_trip_count(_current_user())

                # Download option
                st.download_button(
                    "📥 Download Itinerary",
                    data=result,
                    file_name=f"{destination.replace(' ','_')}_{days}day_itinerary.md",
                    mime="text/markdown",
                )

    # ── Recommendations ────────────────────────────────────────────────────
    with tab_recommend:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            rec_budget = st.number_input("💰 Budget (₹)", 5000, 300000, 20000, 1000, key="rec_budget")
            rec_season = st.selectbox(
                "🌦️ When are you traveling?",
                ["winter (Oct–Feb)", "summer (Mar–May)", "monsoon (Jun–Sep)"],
                key="rec_season",
            )
            rec_from = st.text_input("🛫 Departing From", value="Delhi", key="rec_from")

        with col2:
            rec_duration = st.slider("📅 Duration (days)", 2, 14, 5, key="rec_dur")
            rec_interests = st.multiselect(
                "❤️ Interests",
                ["beaches", "mountains", "culture", "food", "adventure", "wildlife",
                 "history", "luxury", "budget", "offbeat"],
                default=["beaches", "culture"],
                key="rec_interests",
            )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Find Best Destinations", use_container_width=True, key="btn_rec"):
            with loading_placeholder("Finding the perfect destinations for you…"):
                result = get_recommendations(
                    budget=rec_budget,
                    season=rec_season,
                    interests=rec_interests,
                    duration=rec_duration,
                    from_city=rec_from,
                )
            st.markdown("---")
            st.markdown(result)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: DYNAMIC PRICING
# ═══════════════════════════════════════════════════════════════════════════
def page_pricing():
    st.markdown("## 🏷️ Dynamic Pricing Suggester")
    st.markdown('<p style="color:#64748b;">AI-powered pricing recommendations based on demand signals.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        dest = st.text_input("🏖️ Destination", "Goa", key="pr_dest")
        travel_date = st.date_input("📅 Travel Date", key="pr_date")
        vertical = st.selectbox("📦 Product Type",
                                ["packages", "flights", "hotels", "activities", "transport"],
                                key="pr_vert")
    with col2:
        base_price = st.number_input("💰 Base Price (₹)", 1000, 200000, 10000, 500, key="pr_base")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box">
            📈 Dynamic pricing analyzes:<br>
            • Seasonal demand patterns<br>
            • Day-of-week effects<br>
            • Destination popularity<br>
            • Booking lead time
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🧠 Get AI Pricing Suggestion", use_container_width=True, key="btn_price"):
        with loading_placeholder("Analyzing demand signals…"):
            result = get_dynamic_pricing(
                destination=dest,
                travel_date=str(travel_date),
                vertical=vertical,
                base_price=float(base_price),
            )

        st.markdown("---")
        # Display results
        cols = st.columns(4)
        demand_colors = {
            "low": "#4ade80", "medium": "#facc15",
            "high": "#f97316", "surge": "#ef4444",
        }
        d_color = demand_colors.get(result.get("demand_level", "medium"), "#d4a843")

        with cols[0]:
            render_kpi_card("Demand Level", result.get("demand_level", "—").upper(), color=d_color)
        with cols[1]:
            render_kpi_card("Demand Score", f"{result.get('demand_score', 0)}/100")
        with cols[2]:
            render_kpi_card("Price Multiplier", f"{result.get('price_multiplier', 1.0):.2f}×")
        with cols[3]:
            render_kpi_card("Suggested Price", format_inr(result.get("suggested_price", 0)), color="#2dd4bf")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-box">
            💡 <b>AI Recommendation:</b> {result.get('recommendation', '')}
        </div>
        """, unsafe_allow_html=True)

        # Demand factors
        factors = result.get("factors", [])
        if factors:
            st.markdown("**📊 Demand Factors:**")
            for f in factors:
                st.markdown(f"• {f}")

        # Price comparison bar
        import plotly.graph_objects as go
        fig = go.Figure(go.Bar(
            x=["Base Price", "Suggested Price"],
            y=[base_price, result.get("suggested_price", base_price)],
            marker_color=["#1a2235", "#d4a843"],
            text=[format_inr(base_price), format_inr(result.get("suggested_price", base_price))],
            textposition="outside",
            textfont=dict(color="#f1f5f9"),
        ))
        fig.update_layout(
            title="Price Comparison",
            paper_bgcolor="#111827", plot_bgcolor="#1a2235",
            font=dict(color="#f1f5f9"),
            height=300, margin=dict(l=20, r=20, t=40, b=20),
            yaxis=dict(tickprefix="₹", gridcolor="rgba(255,255,255,0.05)"),
        )
        st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: ANALYTICS DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
def page_dashboard():
    st.markdown("## 📊 Business Analytics Dashboard")

    # ── Seed data once ─────────────────────────────────────────────────────
    if not st.session_state.get("db_seeded"):
        with st.spinner("Loading analytics data…"):
            seed_bookings(800)
        st.session_state["db_seeded"] = True

    # ── Filters ────────────────────────────────────────────────────────────
    with st.expander("🔧 Filters", expanded=False):
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            start_date = st.date_input("Start Date", value=None, key="f_start")
        with fc2:
            end_date = st.date_input("End Date", value=None, key="f_end")
        with fc3:
            from database.bookings import CHANNELS
            sel_channels = st.multiselect("Channels", CHANNELS, key="f_channels")
        with fc4:
            from database.bookings import VERTICALS
            sel_verticals = st.multiselect("Verticals", VERTICALS, key="f_verts")

    # Load data with filters
    df = get_bookings_df(
        start_date=str(start_date) if start_date else None,
        end_date=str(end_date) if end_date else None,
        channels=sel_channels if sel_channels else None,
        verticals=sel_verticals if sel_verticals else None,
    )

    if df.empty:
        render_info_box("No booking data found for selected filters.", "warning")
        return

    kpis = get_kpis(df)

    # ── KPI Row ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        render_kpi_card("Total GMV", format_inr(kpis["gmv"]))
    with k2:
        render_kpi_card("Revenue", format_inr(kpis["revenue"]), color="#2dd4bf")
    with k3:
        render_kpi_card("Total Bookings", f"{kpis['bookings']:,}", color="#3b82f6")
    with k4:
        render_kpi_card("Conversion Rate", f"{kpis['conversion_rate']}%", color="#4ade80")
    with k5:
        render_kpi_card("Repeat Customers", f"{kpis['repeat_rate']}%", color="#a78bfa")
    with k6:
        render_kpi_card("Avg CAC", format_inr(kpis["avg_cac"]), color="#f87171")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Chart Row 1: GMV vs Revenue + Channel Performance ─────────────────
    col1, col2 = st.columns([3, 2])
    with col1:
        st.plotly_chart(gmv_vs_revenue_chart(df), use_container_width=True)
    with col2:
        st.plotly_chart(channel_performance_chart(df), use_container_width=True)

    # ── Chart Row 2: Conversion by Vertical + Heatmap ─────────────────────
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(conversion_by_vertical_chart(df), use_container_width=True)
    with col4:
        st.plotly_chart(revenue_heatmap(df), use_container_width=True)

    # ── Chart Row 3: CAC Scatter + Destination Pie ─────────────────────────
    col5, col6 = st.columns(2)
    with col5:
        st.plotly_chart(cac_revenue_scatter(df), use_container_width=True)
    with col6:
        st.plotly_chart(destination_popularity_chart(df), use_container_width=True)

    # ── Raw data table ─────────────────────────────────────────────────────
    with st.expander("📋 Raw Bookings Data (last 50)", expanded=False):
        display_cols = ["booking_id", "destination", "vertical", "channel",
                        "status", "gmv", "revenue", "cac", "booking_date"]
        show_df = df[display_cols].tail(50).copy()
        show_df["booking_date"] = show_df["booking_date"].dt.strftime("%Y-%m-%d")
        show_df["gmv"] = show_df["gmv"].apply(lambda x: f"₹{x:,.0f}")
        show_df["revenue"] = show_df["revenue"].apply(lambda x: f"₹{x:,.0f}")
        show_df["cac"] = show_df["cac"].apply(lambda x: f"₹{x:,.0f}")
        st.dataframe(show_df, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: PREFERENCES
# ═══════════════════════════════════════════════════════════════════════════
def page_preferences():
    st.markdown("## ⚙️ User Preferences")
    user = get_user(_current_user()) or {}
    prefs = user.get("preferences", {})

    col1, col2 = st.columns(2)
    with col1:
        budget_pref = st.selectbox(
            "💰 Default Budget Range",
            ["low", "medium", "high", "luxury"],
            index=["low", "medium", "high", "luxury"].index(prefs.get("budget", "medium")),
        )
        style_pref = st.selectbox(
            "🎭 Default Travel Style",
            ["leisure", "adventure", "cultural", "backpacking", "business"],
            index=["leisure", "adventure", "cultural", "backpacking", "business"].index(
                prefs.get("travel_style", "leisure")
            ),
        )
    with col2:
        fav_dests = st.multiselect(
            "🌏 Favourite Destinations",
            ["Goa", "Kerala", "Rajasthan", "Himachal Pradesh", "Andaman",
             "Ladakh", "Karnataka", "Uttarakhand", "Tamil Nadu", "Maharashtra"],
            default=prefs.get("preferred_destinations", []),
        )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Save Preferences", use_container_width=True):
        update_preferences(_current_user(), {
            "budget": budget_pref,
            "travel_style": style_pref,
            "preferred_destinations": fav_dests,
        })
        st.success("✅ Preferences saved!")

    # Account info
    st.markdown("---")
    st.markdown("**Account Information**")
    st.markdown(f"""
    <div class="kpi-card" style="text-align:left;">
        <div style="color:#94a3b8;font-size:0.8rem;">Username</div>
        <div style="color:#f1f5f9;font-weight:600;">{_current_user()}</div>
        <div style="color:#94a3b8;font-size:0.8rem;margin-top:8px;">Email</div>
        <div style="color:#f1f5f9;">{user.get('email', 'Not provided')}</div>
        <div style="color:#94a3b8;font-size:0.8rem;margin-top:8px;">Trips Planned</div>
        <div style="color:#d4a843;font-weight:700;">{user.get('total_trips', 0)}</div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════
def main():
    _init_session()

    # ── Ensure demo user exists ────────────────────────────────────────────
    if not get_user("demo"):
        create_user("demo", "demo123", "demo@travelmind.ai")

    # ── Route to pages ─────────────────────────────────────────────────────
    if not _is_logged_in():
        page_login()
        return

    render_sidebar()

    page = st.session_state.get("page", "chat")
    if page == "chat":
        page_chat()
    elif page == "itinerary":
        page_itinerary()
    elif page == "pricing":
        page_pricing()
    elif page == "dashboard":
        page_dashboard()
    elif page == "preferences":
        page_preferences()
    else:
        page_chat()


if __name__ == "__main__":
    main()
