import streamlit as st
from backend import database, crud

if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']:
    st.warning("Please login.")
    st.stop()

st.title("⚙️ Settings")

user = st.session_state['user']

st.header("Profile Settings")
st.text_input("Full Name", value=user['name'], disabled=True)
st.text_input("Email", value=user['email'], disabled=True)
st.text_input("User ID", value=str(user['id']), disabled=True)

st.info("To change your password or update details, please contact system administrator.")

st.divider()

st.header("Application Info")
st.write("**BGAI Predictive Analytics System**")
st.write("Version: 1.0.0 (Python Edition)")
st.write("Backend: FastAPI Logic")
st.write("Frontend: Streamlit")
