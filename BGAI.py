import streamlit as st
import traceback
import time

# Page config MUST be first Streamlit command
st.set_page_config(
    page_title="BGAI — Business Growth AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    from backend import models, database, auth, crud, schemas
    models.Base.metadata.create_all(bind=database.engine)
except Exception as e:
    st.error("CRITICAL IMPORT ERROR — check your backend setup.")
    st.code(traceback.format_exc())
    st.stop()

# ─────────────────────────────────────────────
#  GLOBAL CSS — Premium Cyber Dark Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }

/* ── Background ─────────────────────────────── */
.stApp {
    background: radial-gradient(ellipse at top left, #1e0a3c 0%, #0f172a 45%, #020617 100%);
    color: #e2e8f0;
}

/* ── Sidebar ─────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b0f1e 0%, #0f172a 100%);
    border-right: 1px solid rgba(139,92,246,0.15);
}
[data-testid="stSidebarNav"] a { color: #94a3b8 !important; }
[data-testid="stSidebarNav"] a:hover { color: #c084fc !important; }

/* ── Buttons ──────────────────────────────────── */
.stButton>button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: #fff !important;
    border: 1px solid rgba(139,92,246,0.5);
    border-radius: 10px;
    padding: 0.55rem 1.4rem;
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.4px;
    text-transform: uppercase;
    transition: all 0.25s ease;
    box-shadow: 0 0 14px rgba(124,58,237,0.35);
}
.stButton>button:hover {
    background: linear-gradient(135deg, #8b5cf6, #6366f1);
    box-shadow: 0 0 26px rgba(139,92,246,0.65);
    transform: translateY(-2px);
}
.stButton>button:active { transform: translateY(1px); }

/* ── Cards / Expanders ────────────────────────── */
div[data-testid="stExpander"], div[data-testid="stForm"],
div[data-baseweb="card"] {
    background: rgba(15, 23, 42, 0.75) !important;
    backdrop-filter: blur(18px);
    border: 1px solid rgba(139,92,246,0.18);
    border-radius: 14px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.45);
}

/* ── Metric cards ─────────────────────────────── */
[data-testid="stMetric"] {
    background: rgba(17,24,39,0.70);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    backdrop-filter: blur(12px);
    transition: transform 0.2s;
}
[data-testid="stMetric"]:hover { transform: translateY(-3px); }
[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.8rem; }
[data-testid="stMetricValue"] { color: #c084fc !important; font-size: 1.9rem !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] { font-size: 0.85rem !important; }

/* ── Typography ────────────────────────────────── */
h1 {
    background: linear-gradient(90deg, #c084fc, #818cf8, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800; letter-spacing: -1px;
}
h2, h3 { color: #e0e7ff !important; font-weight: 700; }
p, label, li, .stMarkdown { color: #cbd5e1 !important; }

/* ── Inputs ────────────────────────────────────── */
.stTextInput>div>div>input,
.stNumberInput>div>div>input,
.stDateInput>div>div>input,
.stTextArea textarea {
    background-color: rgba(30,41,59,0.85) !important;
    color: #f1f5f9 !important;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 9px;
    transition: all 0.2s;
}
.stTextInput>div>div>input:focus,
.stNumberInput>div>div>input:focus { border-color: #8b5cf6; box-shadow: 0 0 0 2px rgba(139,92,246,0.3); }

div[data-baseweb="select"]>div {
    background-color: rgba(30,41,59,0.85) !important;
    color: #f1f5f9 !important;
}

/* ── Tabs ──────────────────────────────────────── */
button[data-baseweb="tab"] { color: #64748b; font-weight: 500; }
button[data-baseweb="tab"][aria-selected="true"] { color: #c084fc !important; border-bottom: 2px solid #c084fc !important; }

/* ── Dataframe ─────────────────────────────────── */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* ── Divider ───────────────────────────────────── */
hr { border-color: rgba(139,92,246,0.2); }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Session State Bootstrap
# ─────────────────────────────────────────────
for key, default in [
    ("authentication_status", None),
    ("user", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─────────────────────────────────────────────
#  Login / Register Page
# ─────────────────────────────────────────────
def login_page():
    # Hero header
    st.markdown("""
    <div style="text-align:center; padding: 2.5rem 0 1rem;">
        <div style="font-size:3.2rem; font-weight:800;
                    background:linear-gradient(90deg,#c084fc,#818cf8,#38bdf8);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            BGAI
        </div>
        <div style="color:#94a3b8; font-size:1.05rem; margin-top:0.3rem; letter-spacing:1px;">
            Business Growth AI &nbsp;·&nbsp; Predictive Analytics Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Feature pills
    st.markdown("""
    <div style="display:flex; justify-content:center; gap:0.7rem; flex-wrap:wrap; margin-bottom:2rem;">
        <span style="background:rgba(124,58,237,0.2); color:#c084fc; border:1px solid rgba(124,58,237,0.4);
                     border-radius:20px; padding:0.3rem 0.9rem; font-size:0.8rem;">📊 Analytics Engine</span>
        <span style="background:rgba(79,70,229,0.2); color:#818cf8; border:1px solid rgba(79,70,229,0.4);
                     border-radius:20px; padding:0.3rem 0.9rem; font-size:0.8rem;">🤖 ML Predictions</span>
        <span style="background:rgba(56,189,248,0.15); color:#38bdf8; border:1px solid rgba(56,189,248,0.3);
                     border-radius:20px; padding:0.3rem 0.9rem; font-size:0.8rem;">🔌 Integrations</span>
        <span style="background:rgba(16,185,129,0.15); color:#34d399; border:1px solid rgba(16,185,129,0.3);
                     border-radius:20px; padding:0.3rem 0.9rem; font-size:0.8rem;">🔒 Secure Auth</span>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        tab1, tab2 = st.tabs(["🔐  Login", "📝  Register"])

        with tab1:
            with st.form("login_form", clear_on_submit=False):
                email    = st.text_input("Email Address", placeholder="you@company.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submit   = st.form_submit_button("Login →", use_container_width=True)

            if submit:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    db = next(get_db())
                    user = crud.get_user_by_email(db, email)
                    if user and auth.verify_password(password, user.password):
                        crud.update_last_login(db, user.id)
                        st.session_state["authentication_status"] = True
                        st.session_state["user"] = {
                            "name":    user.name,
                            "email":   user.email,
                            "id":      user.id,
                            "company": user.company or "",
                            "role":    user.role,
                        }
                        with st.spinner("Authenticating…"):
                            time.sleep(0.6)
                        st.success(f"Welcome back, {user.name}! 🎉")
                        time.sleep(0.8)
                        st.rerun()
                    else:
                        st.error("Incorrect email or password.")

        with tab2:
            with st.form("register_form", clear_on_submit=False):
                col_a, col_b = st.columns(2)
                with col_a:
                    new_name    = st.text_input("Full Name", placeholder="Jane Smith")
                    new_email   = st.text_input("Email", placeholder="jane@company.com")
                with col_b:
                    company     = st.text_input("Company", placeholder="Acme Corp")
                    new_pw      = st.text_input("Password", type="password", placeholder="Min 8 chars")
                confirm_pw = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
                register   = st.form_submit_button("Create Account →", use_container_width=True)

            if register:
                if not all([new_name, new_email, new_pw, confirm_pw]):
                    st.error("All fields are required.")
                elif new_pw != confirm_pw:
                    st.error("Passwords do not match.")
                else:
                    valid, msg = auth.validate_password_strength(new_pw)
                    if not valid:
                        st.warning(f"⚠️ {msg}")
                    else:
                        db = next(get_db())
                        if crud.get_user_by_email(db, new_email):
                            st.error("An account with this email already exists.")
                        else:
                            user_obj = schemas.UserCreate(
                                email=new_email,
                                password=new_pw,
                                name=new_name,
                                company=company,
                            )
                            crud.create_user(db, user_obj)
                            st.success("✅ Account created! You can now login.")


# ─────────────────────────────────────────────
#  Home Page (post-login)
# ─────────────────────────────────────────────
def main_app():
    user = st.session_state["user"]

    # Sidebar user card
    st.sidebar.markdown(f"""
    <div style="padding:1rem; border-radius:10px; background:rgba(124,58,237,0.12);
                border:1px solid rgba(124,58,237,0.25); margin-bottom:1rem;">
        <div style="font-size:1.1rem; font-weight:700; color:#c084fc;">👤 {user['name']}</div>
        <div style="font-size:0.75rem; color:#64748b; margin-top:0.3rem;">{user['email']}</div>
        <div style="font-size:0.75rem; color:#94a3b8;">{user.get('company','') or 'No company'}</div>
        <div style="margin-top:0.5rem;">
            <span style="background:rgba(16,185,129,0.15); color:#34d399;
                         border-radius:12px; padding:0.15rem 0.6rem; font-size:0.75rem;">
                ● {user.get('role','user').upper()}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("🚪  Logout", use_container_width=True):
        st.session_state["authentication_status"] = None
        st.session_state["user"] = None
        st.rerun()

    # Home content
    st.title("BGAI — Enterprise Predictive Analytics Suite")
    st.markdown(
        "Navigate using the **sidebar** to access any module. "
        "Use **Integrations → Generate Demo Data** to populate the system quickly."
    )

    st.divider()

    # Live KPI strip from DB
    db = next(get_db())
    stats = crud.get_user_stats(db, user["id"])
    db.close()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 Total Predictions",  stats["total_predictions"])
    c2.metric("📂 Data Records",       stats["total_data_records"])
    c3.metric("🔌 Active Integrations", stats["active_integrations"])
    c4.metric("🎯 Avg Confidence",
              f"{stats['avg_confidence']*100:.1f}%" if stats["avg_confidence"] else "—")

    st.divider()

    # Architecture overview cards
    st.markdown("### 🏗️ Platform Modules")
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        st.markdown("""
        <div style="background:rgba(124,58,237,0.08); border:1px solid rgba(124,58,237,0.2);
                    border-radius:12px; padding:1.2rem; height:100%;">
            <div style="font-size:1.5rem;">📊</div>
            <div style="font-weight:700; color:#c084fc; margin:0.4rem 0;">Analytics Engine</div>
            <div style="color:#94a3b8; font-size:0.88rem;">
                Multi-chart real-time visualization with Plotly. Pie, area, scatter &amp; heatmap views.
                Date-range filters and CSV export built-in.
            </div>
        </div>""", unsafe_allow_html=True)

    with r1c2:
        st.markdown("""
        <div style="background:rgba(79,70,229,0.08); border:1px solid rgba(79,70,229,0.2);
                    border-radius:12px; padding:1.2rem; height:100%;">
            <div style="font-size:1.5rem;">🤖</div>
            <div style="font-weight:700; color:#818cf8; margin:0.4rem 0;">ML Prediction Layer</div>
            <div style="color:#94a3b8; font-size:0.88rem;">
                Linear, Polynomial, Random Forest &amp; Gradient Boosting models.
                Real R², MAE, RMSE metrics with 5-step confidence-interval forecasts.
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    r2c1, r2c2 = st.columns(2)

    with r2c1:
        st.markdown("""
        <div style="background:rgba(56,189,248,0.07); border:1px solid rgba(56,189,248,0.2);
                    border-radius:12px; padding:1.2rem; height:100%;">
            <div style="font-size:1.5rem;">📂</div>
            <div style="font-weight:700; color:#38bdf8; margin:0.4rem 0;">CRM &amp; Data Layer</div>
            <div style="color:#94a3b8; font-size:0.88rem;">
                ACID-compliant SQLAlchemy ORM. Structured JSON storage with inline editing,
                per-record delete, and full CSV export capability.
            </div>
        </div>""", unsafe_allow_html=True)

    with r2c2:
        st.markdown("""
        <div style="background:rgba(16,185,129,0.07); border:1px solid rgba(16,185,129,0.2);
                    border-radius:12px; padding:1.2rem; height:100%;">
            <div style="font-size:1.5rem;">🔒</div>
            <div style="font-weight:700; color:#34d399; margin:0.4rem 0;">Security &amp; Auth</div>
            <div style="color:#94a3b8; font-size:0.88rem;">
                PBKDF2-SHA256 password hashing, JWT session tokens, password-strength
                enforcement, and role-based access control for all routes.
            </div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div style="text-align:center; color:#475569; font-size:0.78rem;">
        BGAI v3.0.0 &nbsp;·&nbsp; Python 3.13 &nbsp;·&nbsp; Streamlit &nbsp;·&nbsp; SQLAlchemy &nbsp;·&nbsp; Scikit-Learn
        &nbsp;·&nbsp; Architected by Ujjwal Tiwari
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Router
# ─────────────────────────────────────────────
if st.session_state["authentication_status"]:
    main_app()
else:
    login_page()
