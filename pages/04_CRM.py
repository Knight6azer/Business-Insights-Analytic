"""04_CRM.py — BGAI Customer Relationship / Data Management"""
import io
import json
import streamlit as st
import pandas as pd
from datetime import datetime
from backend import database, crud, schemas

# ── Auth Guard ──────────────────────────────────────────────────────────────
if not st.session_state.get("authentication_status"):
    st.warning("🔒 Please login from the main page.")
    st.stop()

st.title("📂 CRM — Business Data Manager")
st.caption("Add, view, filter, edit and export your structured business records.")

user_id = st.session_state["user"]["id"]
db = database.SessionLocal()
try:
    all_data = crud.get_business_data(db, user_id)
finally:
    db.close()

tab1, tab2 = st.tabs(["📋  View & Manage", "➕  Add Record"])

# ───────────────────────────────────────── TAB 1
with tab1:
    if not all_data:
        st.info("💡 No records yet. Switch to 'Add Record' or use Integrations → Generate Demo Data.")
    else:
        # Summary cards
        total_value = sum(
            float(r.data.get("value", 0)) for r in all_data if isinstance(r.data, dict)
        )
        k1, k2, k3 = st.columns(3)
        k1.metric("Total Records", len(all_data))
        k2.metric("Total Value ($)", f"${total_value:,.0f}")
        k3.metric("Types", len(set(r.data_type for r in all_data)))

        st.divider()

        # Filter bar
        col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
        with col_f1:
            type_opts = ["All"] + sorted(set(r.data_type for r in all_data))
            sel_type  = st.selectbox("Filter Type", type_opts, key="crm_type_filter")
        with col_f2:
            region_opts = ["All"] + sorted(set(
                r.data.get("region", "Unknown")
                for r in all_data if isinstance(r.data, dict)
            ))
            sel_region = st.selectbox("Filter Region", region_opts, key="crm_region_filter")

        # Apply filter
        filtered = all_data
        if sel_type != "All":
            filtered = [r for r in filtered if r.data_type == sel_type]
        if sel_region != "All":
            filtered = [r for r in filtered if isinstance(r.data, dict) and r.data.get("region") == sel_region]

        # Build display DataFrame
        rows = []
        for item in filtered:
            d = item.data if isinstance(item.data, dict) else {}
            rows.append({
                "ID":        item.id,
                "Type":      item.data_type,
                "Region":    d.get("region", "—"),
                "Value ($)": float(d.get("value", 0)),
                "Date":      d.get("date", "—"),
                "Notes":     d.get("notes", "—"),
                "Added":     item.timestamp.strftime("%b %d, %Y"),
            })
        df_display = pd.DataFrame(rows)

        # CSV download
        csv_buf = io.StringIO()
        df_display.to_csv(csv_buf, index=False)
        st.download_button(
            "⬇ Export to CSV",
            data=csv_buf.getvalue(),
            file_name="bgai_crm_export.csv",
            mime="text/csv",
        )

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Per-record delete
        st.divider()
        st.markdown("#### 🗑 Delete a Record")
        if rows:
            del_id = st.selectbox("Select Record ID to Delete", [r["ID"] for r in rows])
            if st.button("Delete Record", type="secondary"):
                db2 = database.SessionLocal()
                success = crud.delete_business_data(db2, del_id, user_id)
                db2.close()
                if success:
                    st.success(f"Record #{del_id} deleted.")
                    st.rerun()
                else:
                    st.error("Could not delete — record not found.")


# ───────────────────────────────────────── TAB 2
with tab2:
    st.markdown("#### Add New Business Record")
    with st.form("data_entry_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            data_type = st.selectbox("Data Type", ["Sales", "Marketing", "Customer Feedback", "Operational", "HR", "Finance"])
            region    = st.selectbox("Region", ["North", "South", "East", "West", "International"])
        with col_b:
            val  = st.number_input("Value ($)", min_value=0.0, step=100.0, value=1000.0)
            date = st.date_input("Date", datetime.now())

        notes = st.text_area("Notes / Description", placeholder="Quarterly review data…")
        submitted = st.form_submit_button("💾 Save Record", use_container_width=True)

        if submitted:
            try:
                structured = {
                    "region": region,
                    "value":  val,
                    "date":   str(date),
                    "notes":  notes,
                    "values": [{"date": str(date), "value": val}],
                }
                new_data_obj = schemas.BusinessDataCreate(
                    data_type=data_type,
                    data=structured,
                    description=notes[:100] if notes else "",
                )
                db3 = database.SessionLocal()
                crud.create_business_data(db3, new_data_obj, user_id)
                db3.close()
                st.success("✅ Record saved successfully!")
                st.rerun()
            except Exception as exc:
                st.error(f"Error: {exc}")
