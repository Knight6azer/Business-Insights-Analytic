"""03_Predictions.py — BGAI ML Predictions Interface"""
import io
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from backend import database, crud, ml_engine, schemas

# ── Auth Guard ──────────────────────────────────────────────────────────────
if not st.session_state.get("authentication_status"):
    st.warning("🔒 Please login from the main page.")
    st.stop()

st.title("🤖 Predictions")
st.caption("Train ML models on your business data and generate future forecasts.")

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font_color="#cbd5e1",
    xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor="rgba(255,255,255,0.07)"),
    margin=dict(t=40, b=20, l=10, r=10),
)

tab1, tab2 = st.tabs(["🚀  New Prediction", "📋  History"])

# ────────────────────────────────────────────────────────────
with tab1:
    st.markdown("#### 1. Select Model")

    MODEL_INFO = {
        "Linear Regression": {
            "icon": "📏",
            "desc": "Best for linear trends. Fast and interpretable.",
            "color": "#818cf8",
        },
        "Polynomial Regression": {
            "icon": "〰️",
            "desc": "Captures non-linear curves. Uses degree-2 features.",
            "color": "#c084fc",
        },
        "Random Forest": {
            "icon": "🌲",
            "desc": "Ensemble of 200 trees. Supports cross-validation.",
            "color": "#34d399",
        },
        "Gradient Boosting": {
            "icon": "⚡",
            "desc": "Sequential boosting. High accuracy on small datasets.",
            "color": "#f59e0b",
        },
    }

    model_cols = st.columns(len(MODEL_INFO))
    model_type = st.session_state.get("selected_model", "Linear Regression")

    for idx, (name, info) in enumerate(MODEL_INFO.items()):
        with model_cols[idx]:
            selected = model_type == name
            border_col = info["color"] if selected else "rgba(255,255,255,0.08)"
            bg_col     = f"rgba(0,0,0,0.3)" if selected else "rgba(0,0,0,0.15)"
            st.markdown(f"""
            <div style="border:2px solid {border_col}; background:{bg_col};
                        border-radius:10px; padding:0.9rem; text-align:center;
                        cursor:pointer; min-height:110px;">
                <div style="font-size:1.6rem;">{info['icon']}</div>
                <div style="font-weight:700; color:{info['color']}; font-size:0.85rem;">{name}</div>
                <div style="color:#64748b; font-size:0.72rem; margin-top:0.3rem;">{info['desc']}</div>
            </div>""", unsafe_allow_html=True)

    model_type = st.selectbox(
        "Confirm Model", list(MODEL_INFO.keys()),
        index=list(MODEL_INFO.keys()).index(model_type),
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("#### 2. Name & Input Data")

    pred_name = st.text_input("Prediction Name", "Sales Forecast Q1")

    input_method = st.radio(
        "Input Method", ["Use Demo Data", "Upload CSV", "Manual JSON"],
        horizontal=True,
    )

    input_data = None
    if input_method == "Upload CSV":
        file = st.file_uploader("CSV file (must contain numeric columns)", type="csv")
        if file:
            csv_df = pd.read_csv(file)
            st.write("Preview:", csv_df.head(5))
            input_data = {"values": csv_df.to_dict(orient="records")}

    elif input_method == "Manual JSON":
        json_str = st.text_area(
            "JSON body",
            '{"values": [{"month": 1, "sales": 1200}, {"month": 2, "sales": 1350}]}',
            height=120,
        )
        try:
            input_data = json.loads(json_str)
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON — fix syntax errors above.")

    else:  # Demo data
        input_data = {
            "values": [
                {"month": 1,  "sales": 1200},
                {"month": 2,  "sales": 1350},
                {"month": 3,  "sales": 1250},
                {"month": 4,  "sales": 1600},
                {"month": 5,  "sales": 1800},
                {"month": 6,  "sales": 2100},
                {"month": 7,  "sales": 2400},
                {"month": 8,  "sales": 2300},
            ]
        }
        st.info("Using 8-month demo sales dataset.")

    st.divider()
    run_btn = st.button("▶ Run Prediction Engine", use_container_width=True)

    if run_btn:
        if not input_data:
            st.warning("Please provide input data first.")
        else:
            with st.spinner("Training model and generating forecast…"):
                result = ml_engine.train_and_predict(model_type, input_data)

            if "error" in result:
                st.error(f"ML Error: {result['error']}")
            else:
                st.success("✅ Prediction complete!")

                # ── Metric Badges ──────────────────────────────────────────
                st.markdown("#### 📊 Model Performance")
                metrics = result.get("metrics", {})
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("R² Score",   f"{metrics.get('r2_score', 0):.4f}")
                m2.metric("MAE",        f"{metrics.get('mae', 0):.2f}")
                m3.metric("RMSE",       f"{metrics.get('rmse', 0):.2f}")
                m4.metric("Confidence", f"{result.get('confidence', 0)*100:.1f}%")

                if metrics.get("cv_r2_mean") is not None:
                    st.info(f"5-Fold Cross-Validation R² Mean: **{metrics['cv_r2_mean']:.4f}**")

                # ── Forecast Chart with Confidence Interval ─────────────────
                st.markdown("#### 🔮 5-Step Forecast with Confidence Intervals")
                forecast = result.get("forecast", [])
                if forecast:
                    df_fc = pd.DataFrame(forecast)

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_fc["step"], y=df_fc["upper"],
                        mode="lines", line=dict(width=0),
                        name="Upper CI", showlegend=False,
                    ))
                    fig.add_trace(go.Scatter(
                        x=df_fc["step"], y=df_fc["lower"],
                        mode="lines", fill="tonexty",
                        fillcolor="rgba(139,92,246,0.20)",
                        line=dict(width=0), name="95% Confidence Band",
                    ))
                    fig.add_trace(go.Scatter(
                        x=df_fc["step"], y=df_fc["value"],
                        mode="lines+markers",
                        line=dict(color="#c084fc", width=3),
                        marker=dict(size=8, color="#c084fc"),
                        name="Forecast",
                    ))
                    fig.update_layout(
                        **PLOTLY_LAYOUT,
                        xaxis_title="Future Step",
                        yaxis_title=result.get("target_column", "Value"),
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # ── Save to DB ─────────────────────────────────────────────
                db = database.SessionLocal()
                db_pred = crud.create_prediction(
                    db,
                    schemas.PredictionCreate(
                        name=pred_name,
                        model_type=model_type,
                        input_data=input_data,
                    ),
                    result,
                    st.session_state["user"]["id"],
                )
                db.close()
                st.toast(f"💾 Saved as '{pred_name}'")


# ────────────────────────────────────────────────────────────
with tab2:
    st.markdown("#### Prediction History")

    db = database.SessionLocal()
    user_id = st.session_state["user"]["id"]
    history = crud.get_predictions(db, user_id)
    db.close()

    if not history:
        st.info("No predictions yet. Run one from the New Prediction tab.")
    else:
        # Filter bar
        status_filter = st.selectbox(
            "Filter by status", ["all", "completed", "failed", "pending"]
        )
        if status_filter != "all":
            history = [p for p in history if p.status == status_filter]

        for item in history:
            badge     = "🟢" if item.status == "completed" else "🔴"
            conf_str  = f"{item.confidence*100:.1f}%" if item.confidence else "—"
            r2_str    = f"{item.accuracy_score:.4f}" if item.accuracy_score else "—"
            with st.expander(f"{badge} {item.name or 'Unnamed'} — {item.model_type} — {item.created_at.strftime('%b %d, %Y')}"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Status",     item.status.capitalize())
                c2.metric("Confidence", conf_str)
                c3.metric("R²",         r2_str)

                if item.output_data and "forecast" in item.output_data:
                    df_h = pd.DataFrame(item.output_data["forecast"])
                    fig_h = px.line(
                        df_h, x="step", y="value",
                        color_discrete_sequence=["#818cf8"],
                    )
                    fig_h.update_layout(**PLOTLY_LAYOUT, height=200)
                    st.plotly_chart(fig_h, use_container_width=True)

                del_btn = st.button(f"🗑 Delete", key=f"del_{item.id}")
                if del_btn:
                    db = database.SessionLocal()
                    crud.delete_prediction(db, item.id, user_id)
                    db.close()
                    st.success("Deleted.")
                    st.rerun()
