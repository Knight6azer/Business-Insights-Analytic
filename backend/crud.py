from sqlalchemy.orm import Session
from . import models, schemas, auth

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, name=user.name, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_business_data(db: Session, data: schemas.BusinessDataCreate, user_id: int):
    db_data = models.BusinessData(**data.dict(), user_id=user_id)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

def get_business_data(db: Session, user_id: int):
    return db.query(models.BusinessData).filter(models.BusinessData.user_id == user_id).all()

def create_prediction(db: Session, prediction: schemas.PredictionCreate, result: dict, user_id: int):
    db_prediction = models.Prediction(
        **prediction.dict(),
        user_id=user_id,
        output_data=result.get("output"),
        confidence=result.get("confidence"),
        status="completed"
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

def get_predictions(db: Session, user_id: int):
    return db.query(models.Prediction).filter(models.Prediction.user_id == user_id).all()

def create_feedback(db: Session, feedback: schemas.FeedbackCreate, user_id: int):
    db_feedback = models.Feedback(**feedback.dict(), user_id=user_id)
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def get_integrations(db: Session, user_id: int):
    return db.query(models.Integration).filter(models.Integration.user_id == user_id).all()

def create_integration(db: Session, integration: schemas.IntegrationCreate, user_id: int):
    db_integration = models.Integration(**integration.dict(), user_id=user_id)
    db.add(db_integration)
    db.commit()
    db.refresh(db_integration)
    return db_integration
