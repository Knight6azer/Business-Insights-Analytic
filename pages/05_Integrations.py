import streamlit as st
from backend import database, crud, schemas

if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']:
    st.warning("Please login.")
    st.stop()

st.title("🔌 Integrations")

db = database.SessionLocal()
user_id = st.session_state['user']['id']

st.subheader("Active Integrations")
integrations = crud.get_integrations(db, user_id)

if integrations:
    for integ in integrations:
        status_icon = "🟢" if integ.is_active else "🔴"
        st.info(f"{status_icon} **{integ.service}** (Added: {integ.created_at.date()})")
else:
    st.write("No active integrations.")

st.divider()

st.subheader("Add New Integration")
with st.form("new_integration"):
    service_name = st.selectbox("Select Service", ["Salesforce", "HubSpot", "Slack", "Google Sheets", "Custom API"])
    api_key = st.text_input("API Key / Config String", type="password")
    
    if st.form_submit_button("Connect"):
        try:
            new_integ = schemas.IntegrationCreate(
                service=service_name,
                config={"api_key": api_key} # Mock config
            )
            crud.create_integration(db, new_integ, user_id)
            st.success(f"Connected to {service_name}!")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to connect: {e}")

db.close()
