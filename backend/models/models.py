from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class DocumentType(str, enum.Enum):
    W2 = "W2"
    FORM_1099 = "1099"
    FORM_1098 = "1098"
    RECEIPT = "receipt"
    INVESTMENT = "investment"
    OTHER = "other"

class FilingStatus(str, enum.Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    FILED = "filed"
    PAID = "paid"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    ssn_last4 = Column(String)           # Only store last 4 digits
    created_at = Column(DateTime, default=datetime.utcnow)
    documents = relationship("Document", back_populates="owner")
    tax_returns = relationship("TaxReturn", back_populates="owner")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    file_path = Column(String)
    doc_type = Column(Enum(DocumentType), default=DocumentType.OTHER)
    status = Column(String, default="processing")   # processing | done | error
    extracted_data = Column(Text)                    # JSON string from Document AI
    tax_year = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship("User", back_populates="documents")

class TaxReturn(Base):
    __tablename__ = "tax_returns"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tax_year = Column(Integer)
    filing_status = Column(String)                   # single, married_joint, etc.
    total_income = Column(Float, default=0.0)
    total_deductions = Column(Float, default=0.0)
    taxable_income = Column(Float, default=0.0)
    tax_owed = Column(Float, default=0.0)
    refund_amount = Column(Float, default=0.0)
    ai_summary = Column(Text)
    status = Column(Enum(FilingStatus), default=FilingStatus.DRAFT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = relationship("User", back_populates="tax_returns")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tax_return_id = Column(Integer, ForeignKey("tax_returns.id"))
    amount = Column(Float)
    stripe_payment_intent = Column(String)
    status = Column(String, default="pending")       # pending | succeeded | failed
    created_at = Column(DateTime, default=datetime.utcnow)
