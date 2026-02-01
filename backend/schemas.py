from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    company: Optional[str] = None
    role: str
    email_verified: bool
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    name: str

# Business Data Schemas
class BusinessDataBase(BaseModel):
    data_type: str
    data: Dict[str, Any]

class BusinessDataCreate(BusinessDataBase):
    pass

class BusinessData(BusinessDataBase):
    id: int
    user_id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        orm_mode = True

# Prediction Schemas
class PredictionBase(BaseModel):
    name: Optional[str] = None
    model_type: str
    input_data: Dict[str, Any]

class PredictionCreate(PredictionBase):
    pass

class Prediction(PredictionBase):
    id: int
    user_id: int
    output_data: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

# Feedback Schemas
class FeedbackCreate(BaseModel):
    type: str # rating, suggestion, issue
    rating: Optional[int] = None
    message: Optional[str] = None

class Feedback(FeedbackCreate):
    id: int
    user_id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

# Integration Schemas
class IntegrationCreate(BaseModel):
    service: str
    config: Dict[str, Any]

class Integration(IntegrationCreate):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
