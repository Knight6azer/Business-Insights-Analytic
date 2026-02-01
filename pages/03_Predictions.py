import streamlit as st
import pandas as pd
import json
from backend import database, crud, ml_engine, schemas

if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']:
    st.warning("Please login.")
    st.stop()

st.title("🤖 Predictions")

tab1, tab2 = st.tabs(["New Prediction", "History"])

with tab1:
    st.subheader("Run New Prediction")
    
    pred_name = st.text_input("Prediction Name", "My Sales Forecast")
    model_type = st.selectbox("Model Type", ["Linear Regression", "Forecasting (Arima - Demo)", "Random Forest (Demo)"])
    
    input_method = st.radio("Input Data Method", ["Upload CSV", "Manual JSON", "Use Demo Data"])
    
    input_data = None
    
    if input_method == "Upload CSV":
        uploaded_file = st.file_uploader("Upload CSV (must contain numeric columns)", type="csv")
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("Preview:", df.head())
            input_data = {"values": df.to_dict(orient="records")}
            
    elif input_method == "Manual JSON":
        json_str = st.text_area("JSON Input", '{"values": [{"x": 1, "y": 10}, {"x": 2, "y": 20}]}')
        try:
            input_data = json.loads(json_str)
        except:
            st.error("Invalid JSON")
            
    elif input_method == "Use Demo Data":
        st.info("Using sample sales data.")
        input_data = {
            "values": [
                {"month": 1, "sales": 1200},
                {"month": 2, "sales": 1350},
                {"month": 3, "sales": 1250},
                {"month": 4, "sales": 1600},
                {"month": 5, "sales": 1800},
                {"month": 6, "sales": 2100}
            ]
        }
        st.write(input_data)

    if st.button("Run Prediction"):
        if input_data:
            with st.spinner("Running ML Engine..."):
                try:
                    # Logic from backend/main.py
                    result = ml_engine.train_and_predict(model_type, input_data)
                    
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success("Prediction Complete!")
                        
                        # Display Results
                        st.json(result)
                        
                        if "forecast" in result:
                             df_forecast = pd.DataFrame(result["forecast"])
                             st.line_chart(df_forecast.set_index("step")["value"])
                        
                        # Save to DB
                        db = database.SessionLocal()
                        user_id = st.session_state['user']['id']
                        prediction_data = schemas.PredictionCreate(
                            name=pred_name,
                            model_type=model_type,
                            input_data=input_data
                        )
                        crud.create_prediction(db, prediction_data, result, user_id)
                        db.close()
                        st.toast("Saved to History")
                except Exception as e:
                    st.error(f"Error during execution: {e}")
        else:
            st.warning("Please provide input data.")

with tab2:
    st.subheader("Prediction History")
    db = database.SessionLocal()
    user_id = st.session_state['user']['id']
    history = crud.get_predictions(db, user_id)
    db.close()
    
    if history:
        for item in history:
            with st.expander(f"{item.name} - {item.model_type} ({item.status})"):
                st.write(f"Confidence: {item.confidence}")
                st.json(item.output_data)
    else:
        st.info("No history yet.")
