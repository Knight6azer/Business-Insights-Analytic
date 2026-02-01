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
    data_type = st.selectbox("Data Type", ["Sales", "Marketing", "Customer Feedback", "Operational"])
    
    # Simple JSON builder
    st.write("Enter Data Content")
    json_text = st.text_area("JSON Content", '{"region": "North", "value": 5000, "notes": "Q1 Target hit"}')
    
    if st.button("Save Record"):
        try:
            parsed_data = json.loads(json_text)
            new_data = schemas.BusinessDataCreate(
                data_type=data_type,
                data=parsed_data
            )
            crud.create_business_data(db, new_data, user_id)
            st.success("Record saved successfully!")
            st.rerun()
        except json.JSONDecodeError:
            st.error("Invalid JSON format.")
        except Exception as e:
            st.error(f"Error: {e}")

db.close()
