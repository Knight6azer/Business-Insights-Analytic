from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, crud, auth, database, ml_engine

# Create Database Tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="BGAI Predictive Analytics API")

# CORS Setup
origins = [
    "http://localhost:3000", # React App
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to BGAI Predictive Analytics API"}

# Auth Routes
@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id, "name": user.name}

@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# Business Data Routes
@app.post("/business-data", response_model=schemas.BusinessData)
def create_business_data_entry(
    data: schemas.BusinessDataCreate,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return crud.create_business_data(db=db, data=data, user_id=current_user.id)

@app.get("/business-data", response_model=List[schemas.BusinessData])
def read_business_data(
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_business_data(db=db, user_id=current_user.id)

# Prediction Routes
@app.post("/predictions", response_model=schemas.Prediction)
def create_prediction(
    prediction: schemas.PredictionCreate,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Run ML Engine
    result = ml_engine.train_and_predict(prediction.model_type, prediction.input_data)
    
    # 2. Save Prediction + Result
    return crud.create_prediction(db=db, prediction=prediction, result=result, user_id=current_user.id)

@app.get("/predictions", response_model=List[schemas.Prediction])
def read_predictions(
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_predictions(db=db, user_id=current_user.id)

# Feedback Routes
@app.post("/feedback", response_model=schemas.Feedback)
def create_user_feedback(
    feedback: schemas.FeedbackCreate,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return crud.create_feedback(db=db, feedback=feedback, user_id=current_user.id)

# Integration Routes
@app.get("/integrations", response_model=List[schemas.Integration])
def read_integrations(
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_integrations(db=db, user_id=current_user.id)

@app.post("/integrations", response_model=schemas.Integration)
def add_integration(
    integration: schemas.IntegrationCreate,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return crud.create_integration(db=db, integration=integration, user_id=current_user.id)
