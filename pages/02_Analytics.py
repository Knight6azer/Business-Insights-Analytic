import streamlit as st
import pandas as pd
import plotly.express as px
from backend import database, crud

# Auth Check
if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']:
    st.warning("Please login from the main page.")
    st.stop()

st.title("📈 Analytics")

db = database.SessionLocal()
user_id = st.session_state['user']['id']

try:
    business_data = crud.get_business_data(db, user_id)
finally:
    db.close()

if not business_data:
    st.info("No business data available. Please add data in the CRM page.")
    st.stop()

# Prepare Data
data_list = []
for item in business_data:
    row = item.__dict__.copy()
    if '_sa_instance_state' in row:
        del row['_sa_instance_state']
    # Flatten the 'data' json column if possible or just use metadata
    # For now, let's visualize the metadata counts
    data_list.append(row)

df = pd.DataFrame(data_list)

# Visualization 1: Data Type Distribution
st.subheader("Data Distribution by Type")
fig_type = px.pie(df, names='data_type', title='Records by Type')
st.plotly_chart(fig_type, use_container_width=True)

# Visualization 2: Timeline
st.subheader("Upload Timeline")
fig_line = px.line(df, x='timestamp', y='id', title='Uploads over Time', markers=True) # ID is proxy for count accumulation if sequential
st.plotly_chart(fig_line, use_container_width=True)

# Advanced: Detailed View (if 'values' in JSON)
st.subheader("Deep Dive")
selected_id = st.selectbox("Select Data Record", df['id'])
selected_record = df[df['id'] == selected_id].iloc[0]

st.write(f"**Type:** {selected_record['data_type']}")
st.json(selected_record['data'])

if 'values' in selected_record['data']:
    try:
        df_detail = pd.DataFrame(selected_record['data']['values'])
        st.write("Preview:")
        st.dataframe(df_detail.head())
        
        # Try to plot if numeric columns exist
        numeric_cols = df_detail.select_dtypes(include=['float', 'int']).columns
        if len(numeric_cols) > 0:
            col_to_plot = st.selectbox("Select Column to Visualize", numeric_cols)
            fig_detail = px.line(df_detail, y=col_to_plot, title=f"Trend of {col_to_plot}")
            st.plotly_chart(fig_detail, use_container_width=True)
    except Exception as e:
        st.error(f"Could not parse details: {e}")
