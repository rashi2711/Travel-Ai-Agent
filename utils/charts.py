"""
utils/charts.py
Plotly chart factory — 6 chart types for the Business Analytics Dashboard.
All charts share a dark luxury theme matching the Streamlit CSS.
"""

from __future__ import annotations
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── Shared theme ────────────────────────────────────────────────────────────
THEME = dict(
    bg="#0a0e1a",
    paper="#111827",
    card="#1a2235",
    gold="#d4a843",
    teal="#2dd4bf",
    blue="#3b82f6",
    coral="#f87171",
    purple="#a78bfa",
    green="#4ade80",
    text="#f1f5f9",
    muted="#64748b",
    grid="rgba(255,255,255,0.05)",
    border="rgba(255,255,255,0.08)",
)

PALETTE = [THEME["gold"], THEME["teal"], THEME["blue"], THEME["coral"],
           THEME["purple"], THEME["green"]]


def _base_layout(title: str = "", height: int = 400) -> dict:
    return dict(
        title=dict(text=title, font=dict(family="Playfair Display", size=16, color=THEME["gold"])),
        height=height,
        paper_bgcolor=THEME["paper"],
        plot_bgcolor=THEME["card"],
        font=dict(family="DM Sans", color=THEME["text"], size=12),
        xaxis=dict(gridcolor=THEME["grid"], linecolor=THEME["border"], tickfont_color=THEME["muted"]),
        yaxis=dict(gridcolor=THEME["grid"], linecolor=THEME["border"], tickfont_color=THEME["muted"]),
        legend=dict(bgcolor="rgba(0,0,0,0)", font_color=THEME["text"]),
        margin=dict(l=40, r=20, t=50, b=40),
        hoverlabel=dict(bgcolor=THEME["card"], font_color=THEME["text"], bordercolor=THEME["border"]),
    )


# ── 1. GMV vs Revenue (dual-axis line chart) ────────────────────────────────
def gmv_vs_revenue_chart(df: pd.DataFrame) -> go.Figure:
    """Monthly GMV vs Revenue comparison."""
    if df.empty:
        return _empty_chart("No data available")

    # Aggregate by month
    df = df.copy()
    df["month_str"] = df["booking_date"].dt.to_period("M").astype(str)
    monthly = (
        df[df["status"].isin(["confirmed", "completed"])]
        .groupby("month_str")
        .agg(gmv=("gmv", "sum"), revenue=("revenue", "sum"))
        .reset_index()
        .sort_values("month_str")
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["month_str"], y=monthly["gmv"],
        name="GMV", mode="lines+markers",
        line=dict(color=THEME["gold"], width=2.5),
        marker=dict(size=6),
        fill="tozeroy", fillcolor="rgba(212,168,67,0.08)",
    ))
    fig.add_trace(go.Scatter(
        x=monthly["month_str"], y=monthly["revenue"],
        name="Revenue", mode="lines+markers",
        line=dict(color=THEME["teal"], width=2.5),
        marker=dict(size=6),
    ))

    layout = _base_layout("GMV vs Revenue (Monthly)", height=380)
    layout["xaxis"]["tickangle"] = -30
    layout["yaxis"]["tickprefix"] = "₹"
    fig.update_layout(**layout)
    return fig


# ── 2. Channel Performance (horizontal bar) ────────────────────────────────
def channel_performance_chart(df: pd.DataFrame) -> go.Figure:
    """Revenue by acquisition channel."""
    if df.empty:
        return _empty_chart("No data")

    ch = (
        df[df["status"].isin(["confirmed", "completed"])]
        .groupby("channel")
        .agg(revenue=("revenue", "sum"), bookings=("booking_id", "count"))
        .reset_index()
        .sort_values("revenue", ascending=True)
    )

    fig = go.Figure(go.Bar(
        x=ch["revenue"], y=ch["channel"],
        orientation="h",
        marker=dict(
            color=ch["revenue"],
            colorscale=[[0, "#1a2235"], [0.5, THEME["blue"]], [1, THEME["gold"]]],
            showscale=False,
        ),
        text=[f"₹{v:,.0f}" for v in ch["revenue"]],
        textposition="outside",
        textfont=dict(color=THEME["gold"]),
        customdata=ch["bookings"],
        hovertemplate="<b>%{y}</b><br>Revenue: ₹%{x:,.0f}<br>Bookings: %{customdata}<extra></extra>",
    ))

    layout = _base_layout("Revenue by Channel", height=360)
    layout["xaxis"]["tickprefix"] = "₹"
    layout["xaxis"]["showgrid"] = False
    layout["yaxis"]["showgrid"] = False
    fig.update_layout(**layout)
    return fig


# ── 3. Conversion by Vertical (grouped bar) ────────────────────────────────
def conversion_by_vertical_chart(df: pd.DataFrame) -> go.Figure:
    """Booking count and conversion rate by vertical."""
    if df.empty:
        return _empty_chart("No data")

    grp = (
        df.groupby(["vertical", "status"])
        .size()
        .reset_index(name="count")
    )
    total = df.groupby("vertical").size().reset_index(name="total")
    confirmed = (
        df[df["status"].isin(["confirmed", "completed"])]
        .groupby("vertical")
        .size()
        .reset_index(name="confirmed")
    )
    merged = total.merge(confirmed, on="vertical")
    merged["conv_rate"] = (merged["confirmed"] / merged["total"] * 100).round(1)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=merged["vertical"], y=merged["total"],
        name="Total Bookings",
        marker_color=THEME["blue"],
        opacity=0.8,
    ))
    fig.add_trace(go.Bar(
        x=merged["vertical"], y=merged["confirmed"],
        name="Confirmed",
        marker_color=THEME["teal"],
    ))
    fig.add_trace(go.Scatter(
        x=merged["vertical"], y=merged["conv_rate"],
        name="Conversion %",
        mode="lines+markers",
        yaxis="y2",
        line=dict(color=THEME["gold"], width=2),
        marker=dict(size=8, symbol="diamond"),
    ))

    layout = _base_layout("Conversion by Vertical", height=400)
    layout["barmode"] = "group"
    layout["yaxis2"] = dict(
        overlaying="y", side="right",
        ticksuffix="%", tickfont_color=THEME["gold"],
        gridcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(**layout)
    return fig


# ── 4. Revenue Heatmap (month × channel) ────────────────────────────────────
def revenue_heatmap(df: pd.DataFrame) -> go.Figure:
    """Monthly revenue heatmap by channel."""
    if df.empty:
        return _empty_chart("No data")

    df = df.copy()
    df["month_str"] = df["booking_date"].dt.strftime("%b")
    MONTH_ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    pivot = (
        df[df["status"].isin(["confirmed", "completed"])]
        .groupby(["month_str", "channel"])["revenue"]
        .sum()
        .unstack(fill_value=0)
    )
    # Reorder months
    pivot = pivot.reindex([m for m in MONTH_ORDER if m in pivot.index])

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0, "#0a0e1a"], [0.5, "#1e3a5f"], [1, THEME["gold"]]],
        hovertemplate="Channel: %{x}<br>Month: %{y}<br>Revenue: ₹%{z:,.0f}<extra></extra>",
        showscale=True,
        colorbar=dict(tickfont_color=THEME["muted"]),
    ))

    layout = _base_layout("Revenue Heatmap (Month × Channel)", height=380)
    fig.update_layout(**layout)
    return fig


# ── 5. CAC vs Revenue Scatter ────────────────────────────────────────────────
def cac_revenue_scatter(df: pd.DataFrame) -> go.Figure:
    """Customer Acquisition Cost vs Revenue per booking by channel."""
    if df.empty:
        return _empty_chart("No data")

    confirmed = df[df["status"].isin(["confirmed", "completed"])].copy()
    channels = confirmed["channel"].unique()
    colors = {ch: PALETTE[i % len(PALETTE)] for i, ch in enumerate(channels)}

    fig = go.Figure()
    for channel in channels:
        sub = confirmed[confirmed["channel"] == channel]
        fig.add_trace(go.Scatter(
            x=sub["cac"], y=sub["revenue"],
            mode="markers",
            name=channel,
            marker=dict(color=colors[channel], size=6, opacity=0.7),
            hovertemplate=f"<b>{channel}</b><br>CAC: ₹%{{x:,.0f}}<br>Revenue: ₹%{{y:,.0f}}<extra></extra>",
        ))

    layout = _base_layout("CAC vs Revenue by Channel", height=400)
    layout["xaxis"]["title"] = "Customer Acquisition Cost (₹)"
    layout["xaxis"]["tickprefix"] = "₹"
    layout["yaxis"]["title"] = "Revenue per Booking (₹)"
    layout["yaxis"]["tickprefix"] = "₹"
    fig.update_layout(**layout)
    return fig


# ── 6. Destination popularity (pie / donut) ─────────────────────────────────
def destination_popularity_chart(df: pd.DataFrame) -> go.Figure:
    """Top destinations by booking volume."""
    if df.empty:
        return _empty_chart("No data")

    top = (
        df.groupby("destination")["booking_id"]
        .count()
        .nlargest(8)
        .reset_index()
        .rename(columns={"booking_id": "count"})
    )

    fig = go.Figure(go.Pie(
        labels=top["destination"],
        values=top["count"],
        hole=0.5,
        marker=dict(colors=PALETTE * 2, line=dict(color=THEME["bg"], width=2)),
        textfont=dict(color=THEME["text"]),
        hovertemplate="<b>%{label}</b><br>Bookings: %{value}<br>Share: %{percent}<extra></extra>",
    ))

    layout = _base_layout("Top Destinations", height=380)
    layout.pop("xaxis", None)
    layout.pop("yaxis", None)
    fig.update_layout(**layout)
    return fig


# ── Helpers ──────────────────────────────────────────────────────────────────
def _empty_chart(msg: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=msg, x=0.5, y=0.5, xref="paper", yref="paper",
                       showarrow=False, font=dict(color=THEME["muted"], size=14))
    fig.update_layout(paper_bgcolor=THEME["paper"], plot_bgcolor=THEME["card"],
                      height=300, margin=dict(l=20, r=20, t=20, b=20))
    return fig


def format_inr(value: float) -> str:
    """Format a number as Indian Rupees with lakh/crore suffix."""
    if value >= 1e7:
        return f"₹{value/1e7:.2f}Cr"
    if value >= 1e5:
        return f"₹{value/1e5:.2f}L"
    return f"₹{value:,.0f}"
