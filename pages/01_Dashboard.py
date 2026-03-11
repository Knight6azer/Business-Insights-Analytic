"""01_Dashboard.py — BGAI KPI Dashboard"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from backend import database, crud

# ── Auth Guard ──────────────────────────────────────────────────────────────
if not st.session_state.get("authentication_status"):
    st.warning("🔒 Please login from the main page.")
    st.stop()

st.title("📊 Dashboard")
st.caption("Real-time overview of your analytics activity and system health.")

user_id = st.session_state["user"]["id"]
db = database.SessionLocal()
try:
    stats        = crud.get_user_stats(db, user_id)
    predictions  = crud.get_predictions(db, user_id)
    business_data = crud.get_business_data(db, user_id)
finally:
    db.close()

# ── KPI Metric Cards ─────────────────────────────────────────────────────────
st.markdown("### 📈 Key Performance Indicators")
c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Predictions",
    stats["total_predictions"],
    delta=f"{stats['completed_predictions']} completed",
)
c2.metric(
    "Data Records",
    stats["total_data_records"],
)
c3.metric(
    "Active Integrations",
    stats["active_integrations"],
)
c4.metric(
    "Avg Confidence",
    f"{stats['avg_confidence']*100:.1f}%" if stats["avg_confidence"] else "—",
    delta="across all predictions",
)

st.divider()

# ── Charts Row ────────────────────────────────────────────────────────────────
if business_data:
    df = pd.DataFrame([
        {
            "data_type": r.data_type,
            "timestamp": r.timestamp,
            "id": r.id,
            "value": r.data.get("value", 0) if isinstance(r.data, dict) else 0,
        }
        for r in business_data
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Records by Type")
        fig_pie = px.pie(
            df, names="data_type",
            color_discrete_sequence=px.colors.sequential.Purp,
            hole=0.4,
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#cbd5e1", showlegend=True,
            margin=dict(t=10, b=10, l=10, r=10),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        st.markdown("#### Upload Activity (Last 30 Days)")
        df_daily = (
            df.set_index("timestamp")
            .resample("D")["id"]
            .count()
            .reset_index()
            .rename(columns={"id": "uploads"})
        )
        fig_area = px.area(
            df_daily, x="timestamp", y="uploads",
            color_discrete_sequence=["#8b5cf6"],
        )
        fig_area.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#cbd5e1", xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
            margin=dict(t=10, b=10, l=10, r=10),
        )
        st.plotly_chart(fig_area, use_container_width=True)
else:
    st.info("💡 No business data yet. Go to **Integrations** → Generate Demo Data to populate the system.")

st.divider()

# ── Recent Activity Tables ─────────────────────────────────────────────────
col_p, col_d = st.columns(2)

with col_p:
    st.markdown("#### 🤖 Recent Predictions")
    if predictions:
        pred_rows = []
        for p in predictions[:5]:
            badge_color = "#34d399" if p.status == "completed" else "#f87171"
            pred_rows.append({
                "Name":       p.name or "—",
                "Model":      p.model_type,
                "Status":     p.status.capitalize(),
                "Confidence": f"{p.confidence*100:.1f}%" if p.confidence else "—",
                "Date":       p.created_at.strftime("%b %d, %Y"),
            })
        st.dataframe(
            pd.DataFrame(pred_rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No predictions yet.")

with col_d:
    st.markdown("#### 📂 Recent Data Uploads")
    if business_data:
        data_rows = [
            {
                "Type":      r.data_type,
                "Value ($)": r.data.get("value", "—") if isinstance(r.data, dict) else "—",
                "Region":    r.data.get("region", "—") if isinstance(r.data, dict) else "—",
                "Date":      r.timestamp.strftime("%b %d, %Y"),
            }
            for r in business_data[:5]
        ]
        st.dataframe(
            pd.DataFrame(data_rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No business data uploaded.")

st.divider()

# ── System Health Panel ────────────────────────────────────────────────────
st.markdown("#### 🖥️ System Health")
h1, h2, h3 = st.columns(3)
h1.markdown("""
<div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);
            border-radius:10px;padding:0.9rem;text-align:center;">
    <div style="color:#34d399;font-size:1.5rem;">✅</div>
    <div style="color:#94a3b8;font-size:0.85rem;margin-top:0.3rem;">Database</div>
    <div style="color:#34d399;font-weight:700;">CONNECTED</div>
</div>""", unsafe_allow_html=True)

h2.markdown("""
<div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);
            border-radius:10px;padding:0.9rem;text-align:center;">
    <div style="color:#34d399;font-size:1.5rem;">✅</div>
    <div style="color:#94a3b8;font-size:0.85rem;margin-top:0.3rem;">ML Engine</div>
    <div style="color:#34d399;font-weight:700;">OPERATIONAL</div>
</div>""", unsafe_allow_html=True)

h3.markdown("""
<div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);
            border-radius:10px;padding:0.9rem;text-align:center;">
    <div style="color:#34d399;font-size:1.5rem;">✅</div>
    <div style="color:#94a3b8;font-size:0.85rem;margin-top:0.3rem;">Auth Service</div>
    <div style="color:#34d399;font-weight:700;">SECURED</div>
</div>""", unsafe_allow_html=True)
