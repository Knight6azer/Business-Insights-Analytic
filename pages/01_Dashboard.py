import streamlit as st
import pandas as pd
from backend import database, crud

# Auth Check
if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']:
    st.warning("Please login from the main page.")
    st.stop()

st.title("📊 Dashboard")

# Get Data
db = database.SessionLocal()
user_id = st.session_state['user']['id']

try:
    predictions = crud.get_predictions(db, user_id)
    business_data = crud.get_business_data(db, user_id)
    integrations = crud.get_integrations(db, user_id)
finally:
    db.close()

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Predictions", len(predictions))
col2.metric("Data Entries", len(business_data))
col3.metric("Active Integrations", len(integrations))

# Recent Activity
st.subheader("Recent Predictions")
if predictions:
    df_pred = pd.DataFrame([p.__dict__ for p in predictions])
    # Cleanup sqlalchemy object
    if '_sa_instance_state' in df_pred.columns:
        df_pred = df_pred.drop(columns=['_sa_instance_state'])
    st.dataframe(df_pred[['name', 'model_type', 'status', 'created_at']].tail(5))
else:
    st.info("No predictions yet. Go to the Predictions page to start.")

st.subheader("Recent Data Uploads")
if business_data:
    df_data = pd.DataFrame([d.__dict__ for d in business_data])
    if '_sa_instance_state' in df_data.columns:
        df_data = df_data.drop(columns=['_sa_instance_state'])
    st.dataframe(df_data[['data_type', 'timestamp']].tail(5))
else:
    st.info("No business data uploaded.")
