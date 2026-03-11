"""
schemas.py — Pydantic Data Transfer Objects for BGAI
=====================================================
All request / response validation shapes live here.
Upgraded to Pydantic v2 configuration style.

Author: Ujjwal Tiwari
Version: 3.0.0
"""

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


# ---------------------------------------------------------------------------
# Token
# ---------------------------------------------------------------------------

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    name: str


class TokenData(BaseModel):
    email: Optional[str] = None


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str
    company: Optional[str] = ""


class UserUpdate(BaseModel):
    """Partial update schema — all fields optional."""
    name:    Optional[str] = None
    company: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id:             int
    company:        Optional[str] = None
    role:           str
    email_verified: bool
    last_login:     Optional[datetime] = None
    created_at:     datetime


# ---------------------------------------------------------------------------
# Business Data
# ---------------------------------------------------------------------------

class BusinessDataBase(BaseModel):
    data_type:   str
    data:        Dict[str, Any]
    description: Optional[str] = ""


class BusinessDataCreate(BusinessDataBase):
    pass


class BusinessData(BusinessDataBase):
    model_config = ConfigDict(from_attributes=True)

    id:         int
    user_id:    int
    timestamp:  datetime
    created_at: datetime


# ---------------------------------------------------------------------------
# Predictions
# ---------------------------------------------------------------------------

class MetricsSchema(BaseModel):
    r2_score:    Optional[float] = None
    mae:         Optional[float] = None
    rmse:        Optional[float] = None
    cv_r2_mean:  Optional[float] = None


class PredictionBase(BaseModel):
    name:       Optional[str] = "Unnamed Prediction"
    model_type: str
    input_data: Dict[str, Any]


class PredictionCreate(PredictionBase):
    pass


class Prediction(PredictionBase):
    model_config = ConfigDict(from_attributes=True)

    id:             int
    user_id:        int
    output_data:    Optional[Dict[str, Any]] = None
    confidence:     Optional[float] = None
    accuracy_score: Optional[float] = None
    status:         str
    created_at:     datetime


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------

class FeedbackCreate(BaseModel):
    type:    str                    # rating | suggestion | bug
    rating:  Optional[int] = None  # 1–5
    message: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def rating_range(cls, v):
        if v is not None and not (1 <= v <= 5):
            raise ValueError("Rating must be between 1 and 5")
        return v


class Feedback(FeedbackCreate):
    model_config = ConfigDict(from_attributes=True)

    id:         int
    user_id:    int
    status:     str
    created_at: datetime


# ---------------------------------------------------------------------------
# Integration
# ---------------------------------------------------------------------------

class IntegrationCreate(BaseModel):
    service: str
    config:  Dict[str, Any]


class Integration(IntegrationCreate):
    model_config = ConfigDict(from_attributes=True)

    id:         int
    user_id:    int
    is_active:  bool
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Dashboard Summary (aggregated KPI response)
# ---------------------------------------------------------------------------

class DashboardSummary(BaseModel):
    total_predictions:     int
    total_data_records:    int
    active_integrations:   int
    avg_confidence:        float
    completed_predictions: int
    failed_predictions:    int
