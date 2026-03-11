"""
models.py — SQLAlchemy ORM Models for BGAI
==========================================
Defines all database tables as Python classes using SQLAlchemy's
declarative base pattern. Relationships are fully typed.

Author: Ujjwal Tiwari
Version: 3.0.0
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    ForeignKey, Float, JSON, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    """Represents an authenticated platform user."""
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    email         = Column(String, unique=True, index=True, nullable=False)
    password      = Column(String, nullable=False)
    name          = Column(String, nullable=False)
    company       = Column(String, default="")
    role          = Column(String, default="user")              # user | admin
    email_verified = Column(Boolean, default=False)
    last_login    = Column(DateTime, nullable=True)             # NEW v3.0
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business_data = relationship("BusinessData", back_populates="user", cascade="all, delete-orphan")
    predictions   = relationship("Prediction",   back_populates="user", cascade="all, delete-orphan")
    feedback      = relationship("Feedback",     back_populates="user", cascade="all, delete-orphan")
    integrations  = relationship("Integration",  back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role!r}>"


class BusinessData(Base):
    """Stores user-submitted business records (sales, marketing, etc.)."""
    __tablename__ = "business_data"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    data_type   = Column(String, nullable=False)   # Sales | Marketing | …
    description = Column(Text,   default="")        # NEW v3.0 — optional notes label
    data        = Column(JSON,   nullable=False)
    timestamp   = Column(DateTime, default=datetime.utcnow)
    created_at  = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="business_data")

    def __repr__(self) -> str:
        return f"<BusinessData id={self.id} type={self.data_type!r} user={self.user_id}>"


class Prediction(Base):
    """Stores a single ML prediction run and its outputs."""
    __tablename__ = "predictions"

    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id"), nullable=False)
    name           = Column(String, default="Unnamed Prediction")
    model_type     = Column(String, nullable=False)
    input_data     = Column(JSON,   nullable=False)
    output_data    = Column(JSON,   nullable=True)
    confidence     = Column(Float,  nullable=True)
    accuracy_score = Column(Float,  nullable=True)  # NEW v3.0 — R² stored separately
    status         = Column(String, default="pending")   # pending | completed | failed
    created_at     = Column(DateTime, default=datetime.utcnow)
    updated_at     = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="predictions")

    def __repr__(self) -> str:
        return f"<Prediction id={self.id} model={self.model_type!r} status={self.status!r}>"


class Feedback(Base):
    """Captures user feedback, ratings, and suggestions."""
    __tablename__ = "feedback"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    type       = Column(String, nullable=False)   # rating | suggestion | bug
    rating     = Column(Integer, nullable=True)   # 1–5
    message    = Column(Text,    nullable=True)
    status     = Column(String, default="open")   # open | reviewed | resolved
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="feedback")

    def __repr__(self) -> str:
        return f"<Feedback id={self.id} type={self.type!r} rating={self.rating}>"


class Integration(Base):
    """Represents a third-party service integration connected to a user account."""
    __tablename__ = "integrations"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    service    = Column(String, nullable=False)
    config     = Column(JSON,   nullable=True)
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="integrations")

    def __repr__(self) -> str:
        return f"<Integration id={self.id} service={self.service!r} active={self.is_active}>"
