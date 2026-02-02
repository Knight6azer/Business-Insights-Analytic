import streamlit as st
import pandas as pd
import json
from datetime import datetime
from backend import database, crud, schemas

if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']:
    st.warning("Please login.")
    st.stop()

st.title("📂 Customer Relationship Management (CRM)")

tab1, tab2 = st.tabs(["View Data", "Add Data"])

db = database.SessionLocal()
user_id = st.session_state['user']['id']

with tab1:
    data = crud.get_business_data(db, user_id)
    if data:
        st.write(f"Total Records: {len(data)}")
        for item in data:
            with st.expander(f"{item.data_type} - {item.timestamp}"):
                st.write(f"ID: {item.id}")
                st.json(item.data)
    else:
        st.info("No business data found.")

with tab2:
    st.subheader("Add Business Data")
    
    with st.form("data_entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            data_type = st.selectbox("Data Type", ["Sales", "Marketing", "Customer Feedback", "Operational"])
            region = st.selectbox("Region", ["North", "South", "East", "West", "International"])
        with col2:
            val = st.number_input("Value ($)", min_value=0.0, step=100.0, value=1000.0)
            date = st.date_input("Date", datetime.now())

        notes = st.text_area("Notes", "Quarterly review data...")
        
        submitted = st.form_submit_button("Save Record")

        if submitted:
            try:
                # Construct structured JSON data
                structured_data = {
                    "region": region,
                    "value": val,
                    "date": str(date),
                    "notes": notes,
                    # Add a 'values' list for time-series compatibility if needed in future
                    "values": [{"date": str(date), "value": val}] 
                }
                
                new_data = schemas.BusinessDataCreate(
                    data_type=data_type,
                    data=structured_data
                )
                crud.create_business_data(db, new_data, user_id)
                st.success("Record saved successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

db.close()
