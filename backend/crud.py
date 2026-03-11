"""
crud.py — Database CRUD Operations for BGAI
============================================
All database read/write/delete operations are centralised here.
Functions use explicit type hints for readability and IDE support.

Author: Ujjwal Tiwari
Version: 3.0.0
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from . import models, schemas, auth


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Return the User row matching *email*, or None."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """Return the User row matching *user_id*, or None."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Hash password and persist a new User record."""
    hashed_pw = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        name=user.name,
        password=hashed_pw,
        company=user.company or "",
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, updates: schemas.UserUpdate) -> Optional[models.User]:
    """Partially update a User's public profile fields."""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    if updates.name is not None:
        db_user.name = updates.name
    if updates.company is not None:
        db_user.company = updates.company
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user


def update_last_login(db: Session, user_id: int) -> None:
    """Stamp the last_login timestamp for a user after successful authentication."""
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db_user.last_login = datetime.utcnow()
        db.commit()


def change_password(db: Session, user_id: int, new_password: str) -> bool:
    """Hash and store a new password. Returns True on success."""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    db_user.password = auth.get_password_hash(new_password)
    db_user.updated_at = datetime.utcnow()
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Business Data
# ---------------------------------------------------------------------------

def create_business_data(
    db: Session, data: schemas.BusinessDataCreate, user_id: int
) -> models.BusinessData:
    """Persist a new BusinessData record for *user_id*."""
    db_data = models.BusinessData(
        data_type=data.data_type,
        data=data.data,
        description=data.description or "",
        user_id=user_id,
    )
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


def get_business_data(db: Session, user_id: int) -> List[models.BusinessData]:
    """Return all BusinessData records for *user_id*, newest first."""
    return (
        db.query(models.BusinessData)
        .filter(models.BusinessData.user_id == user_id)
        .order_by(models.BusinessData.created_at.desc())
        .all()
    )


def get_business_data_by_type(
    db: Session, user_id: int, data_type: str
) -> List[models.BusinessData]:
    """Filter business data by type (e.g. 'Sales')."""
    return (
        db.query(models.BusinessData)
        .filter(
            models.BusinessData.user_id == user_id,
            models.BusinessData.data_type == data_type,
        )
        .order_by(models.BusinessData.created_at.desc())
        .all()
    )


def delete_business_data(db: Session, record_id: int, user_id: int) -> bool:
    """Delete a single BusinessData record owned by *user_id*. Returns True if deleted."""
    record = (
        db.query(models.BusinessData)
        .filter(models.BusinessData.id == record_id, models.BusinessData.user_id == user_id)
        .first()
    )
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True


def delete_all_user_data(db: Session, user_id: int) -> int:
    """Delete all BusinessData for *user_id*. Returns count of deleted rows."""
    count = (
        db.query(models.BusinessData)
        .filter(models.BusinessData.user_id == user_id)
        .delete()
    )
    db.commit()
    return count


# ---------------------------------------------------------------------------
# Predictions
# ---------------------------------------------------------------------------

def create_prediction(
    db: Session,
    prediction: schemas.PredictionCreate,
    result: dict,
    user_id: int,
) -> models.Prediction:
    """Persist a Prediction record with the ML engine output."""
    metrics = result.get("metrics", {})
    db_pred = models.Prediction(
        name=prediction.name,
        model_type=prediction.model_type,
        input_data=prediction.input_data,
        output_data=result,
        confidence=result.get("confidence"),
        accuracy_score=metrics.get("r2_score"),
        status="completed" if "error" not in result else "failed",
        user_id=user_id,
    )
    db.add(db_pred)
    db.commit()
    db.refresh(db_pred)
    return db_pred


def get_predictions(db: Session, user_id: int) -> List[models.Prediction]:
    """Return all predictions for *user_id*, newest first."""
    return (
        db.query(models.Prediction)
        .filter(models.Prediction.user_id == user_id)
        .order_by(models.Prediction.created_at.desc())
        .all()
    )


def get_predictions_filtered(
    db: Session, user_id: int, status: Optional[str] = None
) -> List[models.Prediction]:
    """Return predictions optionally filtered by *status*."""
    q = db.query(models.Prediction).filter(models.Prediction.user_id == user_id)
    if status:
        q = q.filter(models.Prediction.status == status)
    return q.order_by(models.Prediction.created_at.desc()).all()


def delete_prediction(db: Session, pred_id: int, user_id: int) -> bool:
    """Delete a Prediction record owned by *user_id*."""
    record = (
        db.query(models.Prediction)
        .filter(models.Prediction.id == pred_id, models.Prediction.user_id == user_id)
        .first()
    )
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------

def create_feedback(db: Session, feedback: schemas.FeedbackCreate, user_id: int) -> models.Feedback:
    """Persist a user feedback entry."""
    db_fb = models.Feedback(**feedback.model_dump(), user_id=user_id)
    db.add(db_fb)
    db.commit()
    db.refresh(db_fb)
    return db_fb


# ---------------------------------------------------------------------------
# Integrations
# ---------------------------------------------------------------------------

def get_integrations(db: Session, user_id: int) -> List[models.Integration]:
    """Return all integrations for *user_id*."""
    return (
        db.query(models.Integration)
        .filter(models.Integration.user_id == user_id)
        .order_by(models.Integration.created_at.desc())
        .all()
    )


def create_integration(
    db: Session, integration: schemas.IntegrationCreate, user_id: int
) -> models.Integration:
    """Persist a new service integration."""
    db_integ = models.Integration(**integration.model_dump(), user_id=user_id)
    db.add(db_integ)
    db.commit()
    db.refresh(db_integ)
    return db_integ


def toggle_integration(db: Session, integ_id: int, user_id: int) -> Optional[models.Integration]:
    """Flip the is_active flag on an integration. Returns the updated record or None."""
    record = (
        db.query(models.Integration)
        .filter(models.Integration.id == integ_id, models.Integration.user_id == user_id)
        .first()
    )
    if not record:
        return None
    record.is_active = not record.is_active
    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record


# ---------------------------------------------------------------------------
# Aggregated Stats (Dashboard KPIs)
# ---------------------------------------------------------------------------

def get_user_stats(db: Session, user_id: int) -> dict:
    """
    Return a dict with aggregated KPI counts for the dashboard summary card.
    """
    predictions   = get_predictions(db, user_id)
    data_records  = get_business_data(db, user_id)
    integrations  = get_integrations(db, user_id)

    confidences = [p.confidence for p in predictions if p.confidence is not None]
    avg_confidence = round(sum(confidences) / len(confidences), 4) if confidences else 0.0

    return {
        "total_predictions":     len(predictions),
        "total_data_records":    len(data_records),
        "active_integrations":   sum(1 for i in integrations if i.is_active),
        "avg_confidence":        avg_confidence,
        "completed_predictions": sum(1 for p in predictions if p.status == "completed"),
        "failed_predictions":    sum(1 for p in predictions if p.status == "failed"),
    }
