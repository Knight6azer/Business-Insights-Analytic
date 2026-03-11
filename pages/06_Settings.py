"""06_Settings.py — BGAI User Settings & Account Management"""
import json
import streamlit as st
from backend import database, crud, auth, schemas

# ── Auth Guard ──────────────────────────────────────────────────────────────
if not st.session_state.get("authentication_status"):
    st.warning("🔒 Please login from the main page.")
    st.stop()

st.title("⚙️ Settings")
st.caption("Manage your profile, security preferences, and account data.")

user = st.session_state["user"]
user_id = user["id"]

tab1, tab2, tab3, tab4 = st.tabs(["👤  Profile", "🔐  Security", "📤  Data", "ℹ️  About"])

# ────────────────────────────────── TAB 1: Profile
with tab1:
    st.markdown("#### Profile Information")
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name    = st.text_input("Full Name", value=user["name"])
            email_disp  = st.text_input("Email Address", value=user["email"], disabled=True)
        with col2:
            new_company = st.text_input("Company", value=user.get("company", "") or "")
            role_disp   = st.text_input("Role", value=user.get("role", "user").upper(), disabled=True)

        save_profile = st.form_submit_button("💾 Save Profile", use_container_width=True)

    if save_profile:
        db = database.SessionLocal()
        updated = crud.update_user(
            db, user_id,
            schemas.UserUpdate(name=new_name, company=new_company),
        )
        db.close()
        if updated:
            st.session_state["user"]["name"]    = updated.name
            st.session_state["user"]["company"] = updated.company or ""
            st.success("✅ Profile updated successfully!")
            st.rerun()
        else:
            st.error("Could not update profile.")

    st.divider()
    st.markdown(f"""
    <div style="background:rgba(17,24,39,0.6); border:1px solid rgba(255,255,255,0.07);
                border-radius:10px; padding:1rem;">
        <div style="color:#64748b; font-size:0.8rem;">ACCOUNT INFO</div>
        <div style="margin-top:0.6rem; color:#94a3b8; font-size:0.85rem;">
            User ID: <span style="color:#c084fc; font-weight:600;">#{user_id}</span>
            &nbsp;&nbsp;·&nbsp;&nbsp;
            Role: <span style="color:#34d399; font-weight:600;">{user.get('role','user').upper()}</span>
        </div>
    </div>""", unsafe_allow_html=True)


# ────────────────────────────────── TAB 2: Security
with tab2:
    st.markdown("#### Change Password")
    with st.form("pw_change_form"):
        current_pw = st.text_input("Current Password", type="password")
        new_pw     = st.text_input("New Password",     type="password")
        confirm_pw = st.text_input("Confirm New Password", type="password")
        change_btn = st.form_submit_button("🔐 Update Password", use_container_width=True)

    if change_btn:
        if not all([current_pw, new_pw, confirm_pw]):
            st.error("All fields are required.")
        elif new_pw != confirm_pw:
            st.error("New passwords do not match.")
        else:
            # Verify current password
            db = database.SessionLocal()
            db_user = crud.get_user_by_id(db, user_id)
            if not db_user or not auth.verify_password(current_pw, db_user.password):
                db.close()
                st.error("Current password is incorrect.")
            else:
                valid, msg = auth.validate_password_strength(new_pw)
                if not valid:
                    db.close()
                    st.warning(f"⚠️ {msg}")
                else:
                    crud.change_password(db, user_id, new_pw)
                    db.close()
                    st.success("✅ Password updated successfully!")

    st.divider()
    st.markdown("#### Password Requirements")
    st.markdown("""
    - Minimum **8 characters**
    - At least one **uppercase letter**
    - At least one **digit** (0–9)
    - At least one **special character** (!@#$%^&*…)
    """)


# ────────────────────────────────── TAB 3: Data
with tab3:
    st.markdown("#### Export My Data")
    db = database.SessionLocal()
    all_data    = crud.get_business_data(db, user_id)
    all_preds   = crud.get_predictions(db, user_id)
    db.close()

    export_obj = {
        "user": {
            "name":    user["name"],
            "email":   user["email"],
            "company": user.get("company", ""),
        },
        "business_data": [
            {
                "id":        r.id,
                "type":      r.data_type,
                "timestamp": str(r.timestamp),
                "data":      r.data,
            }
            for r in all_data
        ],
        "predictions": [
            {
                "id":         p.id,
                "name":       p.name,
                "model":      p.model_type,
                "confidence": p.confidence,
                "r2_score":   p.accuracy_score,
                "status":     p.status,
                "created_at": str(p.created_at),
            }
            for p in all_preds
        ],
    }

    st.download_button(
        "⬇ Download All My Data (JSON)",
        data=json.dumps(export_obj, indent=2),
        file_name="bgai_my_data_export.json",
        mime="application/json",
        use_container_width=True,
    )

    st.divider()
    st.markdown("#### 🚨 Danger Zone")
    st.warning("**Delete All Business Data** — This action is irreversible and will permanently remove all your data records.")

    with st.expander("⚠️ I understand — show delete option"):
        confirm_text = st.text_input(
            "Type  DELETE  to confirm",
            placeholder="DELETE",
            key="danger_confirm",
        )
        if st.button("🗑 Delete All Business Data", type="primary"):
            if confirm_text == "DELETE":
                db = database.SessionLocal()
                count = crud.delete_all_user_data(db, user_id)
                db.close()
                st.success(f"✅ Deleted {count} records.")
                st.rerun()
            else:
                st.error("Type exactly  DELETE  to confirm.")


# ────────────────────────────────── TAB 4: About
with tab4:
    st.markdown("#### About BGAI")

    st.markdown("""
    <div style="background:rgba(17,24,39,0.7); border:1px solid rgba(139,92,246,0.2);
                border-radius:14px; padding:1.5rem;">
        <div style="font-size:1.8rem; font-weight:800;
                    background:linear-gradient(90deg,#c084fc,#818cf8);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            BGAI v3.0.0
        </div>
        <div style="color:#94a3b8; font-size:0.85rem; margin-top:0.4rem;">
            Business Growth AI — Enterprise Predictive Analytics Suite
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Tech Stack**
        | Layer | Technology |
        |---|---|
        | Frontend | Streamlit 1.42+ |
        | Backend | Python 3.13 |
        | Database | SQLite / SQLAlchemy ORM |
        | ML Engine | Scikit-Learn |
        | Auth | Passlib (PBKDF2) + JWT |
        | Schemas | Pydantic v2 |
        """)
    with col2:
        st.markdown("""
        **Build Info**
        | Key | Value |
        |---|---|
        | Version | v3.0.0 |
        | Release | March 2026 |
        | Status | Production |
        | License | MIT |
        | Author | Ujjwal Tiwari |
        """)

    st.divider()
    st.caption("Architected by Ujjwal Tiwari · GitHub: Knight6azer/Business-Insights-Analytic")
