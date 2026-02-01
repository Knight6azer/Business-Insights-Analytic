import streamlit as st
import time
from backend import models, database, auth, crud, schemas
from sqlalchemy.orm import Session

# Page Config
st.set_page_config(
    page_title="BGAI Predictive Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Database
models.Base.metadata.create_all(bind=database.engine)

# Premium CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(to right, #f8f9fa, #e9ecef);
        color: #212529;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.02);
    }
    .stSidebar {
        background-color: #343a40;
        color: white;
    }
    h1, h2, h3 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #2c3e50;
    }
    .css-1d391kg {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Session State for Auth
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None
if 'user' not in st.session_state:
    st.session_state['user'] = None

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def login_page():
    st.title("Welcome to BGAI 🚀")
    
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.header("Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")

            if submit_button:
                db = next(get_db())
                user = crud.get_user_by_email(db, email)
                if user and auth.verify_password(password, user.password):
                    st.session_state['authentication_status'] = True
                    st.session_state['user'] = {"name": user.name, "email": user.email, "id": user.id}
                    st.success(f"Welcome back, {user.name}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Incorrect email or password")

    with tab2:
        st.header("Register")
        with st.form("register_form"):
            new_name = st.text_input("Full Name")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_button = st.form_submit_button("Register")

            if register_button:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    db = next(get_db())
                    existing_user = crud.get_user_by_email(db, new_email)
                    if existing_user:
                        st.error("Email already registered")
                    else:
                        user_create = schemas.UserCreate(
                            email=new_email, 
                            password=new_password, 
                            name=new_name,
                            company="New Company"
                        )
                        crud.create_user(db, user_create)
                        st.success("Registration successful! You can now login.")

def main_app():
    user = st.session_state['user']
    st.sidebar.title(f"Hello, {user['name']}")
    
    if st.sidebar.button("Logout"):
        st.session_state['authentication_status'] = None
        st.session_state['user'] = None
        st.rerun()
    
    st.info("👈 Select a page from the sidebar to get started.")
    
    st.markdown("""
    ## Dashboard Overview
    
    Welcome to your **Predictive Analytics Dashboard**.
    
    **Features:**
    - **📊 Analytics:** Visualize your business data.
    - **🤖 Predictions:** Run ML models on your data.
    - **📂 CRM:** Manage your customer and business data.
    - **🔌 Integrations:** Connect external services.
    
    *Built with Python, Streamlit, and Love.*
    """)

# Main Routing
if st.session_state['authentication_status']:
    main_app()
else:
    login_page()
