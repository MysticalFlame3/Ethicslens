from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class AuditSession(Base):
    __tablename__ = "audit_sessions"

    id = Column(String(36), primary_key=True)
    filename = Column(String(255))
    total_rows = Column(Integer)
    detected_columns = Column(JSON)
    composite_score = Column(Float, nullable=True)
    quality_tier = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    results = relationship("TestResult", back_populates="session", cascade="all, delete")


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("audit_sessions.id"))
    test_name = Column(String(100))
    score = Column(Integer, nullable=True)
    status = Column(String(50))
    metrics = Column(JSON)
    chart_data = Column(JSON)
    description = Column(Text)
    recommendations = Column(JSON)

    session = relationship("AuditSession", back_populates="results")
