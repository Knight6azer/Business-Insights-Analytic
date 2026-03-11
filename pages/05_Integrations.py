"""05_Integrations.py — BGAI Integration Marketplace"""
import random
from datetime import datetime, timedelta
import streamlit as st
from backend import database, crud, schemas

# ── Auth Guard ──────────────────────────────────────────────────────────────
if not st.session_state.get("authentication_status"):
    st.warning("🔒 Please login from the main page.")
    st.stop()

st.title("🔌 Integrations")
st.caption("Connect third-party data sources and manage active service integrations.")

user_id = st.session_state["user"]["id"]
db = database.SessionLocal()
try:
    integrations = crud.get_integrations(db, user_id)
finally:
    db.close()

# ── Active Integrations ───────────────────────────────────────────────────────
st.markdown("#### ✅ Active Integrations")
if integrations:
    for integ in integrations:
        dot   = "🟢" if integ.is_active else "🔴"
        label = "Active" if integ.is_active else "Inactive"
        col_a, col_b, col_c = st.columns([4, 2, 2])
        with col_a:
            st.markdown(f"""
            <div style="background:rgba(17,24,39,0.7); border:1px solid rgba(255,255,255,0.08);
                        border-radius:10px; padding:0.8rem; display:flex; align-items:center; gap:1rem;">
                <div style="font-size:1.4rem;">{dot}</div>
                <div>
                    <div style="font-weight:700; color:#e0e7ff;">{integ.service}</div>
                    <div style="font-size:0.76rem; color:#64748b;">Connected {integ.created_at.strftime('%b %d, %Y')}</div>
                </div>
            </div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"<div style='padding-top:0.5rem; color:#94a3b8;'>{label}</div>", unsafe_allow_html=True)
        with col_c:
            if st.button("Toggle", key=f"toggle_{integ.id}"):
                db2 = database.SessionLocal()
                crud.toggle_integration(db2, integ.id, user_id)
                db2.close()
                st.rerun()
else:
    st.info("No integrations connected yet.")

st.divider()

# ── Integration Marketplace ───────────────────────────────────────────────────
st.markdown("#### 🛒 Integration Marketplace")

SERVICES = {
    "Salesforce":    {"icon": "☁️",  "desc": "Sync CRM leads, opportunities, and account data."},
    "HubSpot":       {"icon": "🧲",  "desc": "Pull marketing contacts and campaign analytics."},
    "Slack":         {"icon": "💬",  "desc": "Send prediction alerts and reports to channels."},
    "Google Sheets": {"icon": "📊",  "desc": "Import/export business data from spreadsheets."},
    "Stripe":        {"icon": "💳",  "desc": "Pull revenue, subscription, and refund metrics."},
    "GitHub":        {"icon": "🐙",  "desc": "Track engineering velocity and deployment events."},
    "Zapier":        {"icon": "⚡",  "desc": "Connect 5000+ apps with no-code automation."},
    "Custom API":    {"icon": "🔧",  "desc": "Define a custom REST endpoint for data ingestion."},
}

connected = {i.service for i in integrations}
rows_of_4 = [list(SERVICES.items())[i:i+4] for i in range(0, len(SERVICES), 4)]

for row in rows_of_4:
    cols = st.columns(len(row))
    for col, (name, info) in zip(cols, row):
        already = name in connected
        with col:
            badge = "✓ Connected" if already else "Connect"
            badge_color = "#34d399" if already else "#c084fc"
            st.markdown(f"""
            <div style="background:rgba(17,24,39,0.75); border:1px solid rgba(255,255,255,0.08);
                        border-radius:12px; padding:1rem; text-align:center; min-height:140px;">
                <div style="font-size:1.8rem;">{info['icon']}</div>
                <div style="font-weight:700; color:#e0e7ff; margin:0.4rem 0; font-size:0.9rem;">{name}</div>
                <div style="color:#64748b; font-size:0.72rem;">{info['desc']}</div>
                <div style="margin-top:0.6rem; color:{badge_color}; font-size:0.78rem;
                            font-weight:600;">{badge}</div>
            </div>""", unsafe_allow_html=True)
            if not already:
                if st.button(f"＋ {name}", key=f"add_{name}", use_container_width=True):
                    db3 = database.SessionLocal()
                    crud.create_integration(
                        db3,
                        schemas.IntegrationCreate(service=name, config={"source": "marketplace"}),
                        user_id,
                    )
                    db3.close()
                    st.success(f"Connected to {name}!")
                    st.rerun()

st.divider()

# ── Quick Actions ─────────────────────────────────────────────────────────────
st.markdown("#### ⚡ Quick Actions")
col_q1, col_q2 = st.columns(2)

with col_q1:
    if st.button("🎲 Generate Demo Data (10 Records)", use_container_width=True):
        try:
            regions = ["North", "South", "East", "West"]
            types   = ["Sales", "Marketing", "Finance", "Operational"]
            count   = 0
            db4 = database.SessionLocal()
            for _ in range(10):
                t    = random.choice(types)
                date = datetime.now() - timedelta(days=random.randint(0, 60))
                val  = random.randint(1000, 75000)
                payload = {
                    "region": random.choice(regions),
                    "value":  val,
                    "date":   str(date.date()),
                    "notes":  "Auto-generated by Demo Tool",
                    "values": [{"date": str(date.date()), "value": val}],
                }
                crud.create_business_data(
                    db4,
                    schemas.BusinessDataCreate(data_type=t, data=payload, description="Demo record"),
                    user_id,
                )
                count += 1
            db4.close()
            st.success(f"✅ Generated {count} demo records! Check Analytics.")
        except Exception as exc:
            st.error(f"Error: {exc}")

with col_q2:
    if st.button("🚀 Generate 5 Demo Predictions", use_container_width=True):
        from backend import ml_engine
        try:
            db5 = database.SessionLocal()
            models_list = ["Linear Regression", "Polynomial Regression", "Random Forest", "Gradient Boosting", "Linear Regression"]
            demo_data   = {"values": [{"month": i, "sales": 1000 + i * 150 + random.randint(-100, 100)} for i in range(1, 9)]}
            count = 0
            for model in models_list:
                result = ml_engine.train_and_predict(model, demo_data)
                crud.create_prediction(
                    db5,
                    schemas.PredictionCreate(name=f"Demo — {model}", model_type=model, input_data=demo_data),
                    result, user_id,
                )
                count += 1
            db5.close()
            st.success(f"✅ Generated {count} demo predictions! Check Predictions → History.")
        except Exception as exc:
            st.error(f"Error: {exc}")
