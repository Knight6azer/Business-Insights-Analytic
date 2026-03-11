"""02_Analytics.py — BGAI Advanced Analytics"""
import io
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np
from backend import database, crud

# ── Auth Guard ──────────────────────────────────────────────────────────────
if not st.session_state.get("authentication_status"):
    st.warning("🔒 Please login from the main page.")
    st.stop()

st.title("📈 Analytics")
st.caption("Multi-dimensional visualization of your business data.")

user_id = st.session_state["user"]["id"]
db = database.SessionLocal()
try:
    raw_data = crud.get_business_data(db, user_id)
finally:
    db.close()

if not raw_data:
    st.info("💡 No data yet. Go to **Integrations → Generate Demo Data** to populate the system.")
    st.stop()

# ── Build DataFrame ──────────────────────────────────────────────────────────
rows = []
for item in raw_data:
    d = item.data if isinstance(item.data, dict) else {}
    rows.append({
        "id":        item.id,
        "data_type": item.data_type,
        "timestamp": pd.to_datetime(item.timestamp),
        "region":    d.get("region", "Unknown"),
        "value":     float(d.get("value", 0)),
        "date":      d.get("date", ""),
    })
df = pd.DataFrame(rows)

# ── Sidebar Filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filters")
    types_avail = ["All"] + sorted(df["data_type"].unique().tolist())
    sel_type    = st.selectbox("Data Type", types_avail)

    min_date = df["timestamp"].min().date()
    max_date = df["timestamp"].max().date()
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

# Apply filters
df_f = df.copy()
if sel_type != "All":
    df_f = df_f[df_f["data_type"] == sel_type]
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    df_f = df_f[
        (df_f["timestamp"].dt.date >= date_range[0]) &
        (df_f["timestamp"].dt.date <= date_range[1])
    ]

st.markdown(f"**{len(df_f)} records** matching current filters.")

# ── Download ─────────────────────────────────────────────────────────────────
csv_buffer = io.StringIO()
df_f.to_csv(csv_buffer, index=False)
st.download_button(
    "⬇ Download Filtered Data (CSV)",
    data=csv_buffer.getvalue(),
    file_name="bgai_analytics_export.csv",
    mime="text/csv",
)

st.divider()

# ── 4-Chart Layout ──────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font_color="#cbd5e1",
    xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
    margin=dict(t=30, b=20, l=10, r=10),
)
COLORS = px.colors.sequential.Purpor

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🥧 Records by Type")
    fig1 = px.pie(df_f, names="data_type", color_discrete_sequence=COLORS, hole=0.42)
    fig1.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("#### 📅 Upload Timeline")
    daily = df_f.set_index("timestamp").resample("D")["id"].count().reset_index()
    daily.columns = ["date", "count"]
    fig2 = px.area(daily, x="date", y="count", color_discrete_sequence=["#8b5cf6"])
    fig2.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("#### 🌍 Revenue by Region")
    if "region" in df_f.columns and df_f["value"].sum() > 0:
        reg_df = df_f.groupby("region")["value"].sum().reset_index()
        fig3 = px.bar(
            reg_df, x="region", y="value", color="region",
            color_discrete_sequence=COLORS,
            labels={"value": "Total Value ($)"},
        )
        fig3.update_layout(**PLOTLY_LAYOUT, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Insufficient data for regional breakdown.")

with col4:
    st.markdown("#### 💡 Value Distribution")
    if df_f["value"].sum() > 0:
        fig4 = px.box(
            df_f, x="data_type", y="value", color="data_type",
            color_discrete_sequence=COLORS,
            labels={"value": "Value ($)"},
        )
        fig4.update_layout(**PLOTLY_LAYOUT, showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No value data available for distribution plot.")

st.divider()

# ── Summary Statistics ────────────────────────────────────────────────────────
st.markdown("#### 📋 Summary Statistics")
stats_df = df_f.groupby("data_type")["value"].agg(
    Count="count", Total="sum", Mean="mean", Max="max", Min="min"
).round(2).reset_index()
stats_df.columns = ["Type", "Count", "Total ($)", "Mean ($)", "Max ($)", "Min ($)"]
st.dataframe(stats_df, use_container_width=True, hide_index=True)

st.divider()

# ── Deep Dive ─────────────────────────────────────────────────────────────────
with st.expander("🔬 Record Deep Dive"):
    selected_id = st.selectbox("Select Record ID", df_f["id"].tolist())
    if selected_id:
        rec_raw = next((r for r in raw_data if r.id == selected_id), None)
        if rec_raw:
            col_l, col_r = st.columns(2)
            with col_l:
                st.write(f"**Type:** {rec_raw.data_type}")
                st.write(f"**Timestamp:** {rec_raw.timestamp.strftime('%Y-%m-%d %H:%M')}")
            with col_r:
                st.write(f"**Region:** {rec_raw.data.get('region','—') if isinstance(rec_raw.data, dict) else '—'}")
                st.write(f"**Value:** ${rec_raw.data.get('value',0):,.2f}" if isinstance(rec_raw.data, dict) else "**Value:** —")
            st.markdown("**Raw JSON:**")
            st.json(rec_raw.data)
