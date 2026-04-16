from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class TestResultSchema(BaseModel):
    id: int
    session_id: str
    test_name: str
    score: Optional[int]
    status: str
    metrics: Optional[Dict[str, Any]]
    chart_data: Optional[Dict[str, Any]]
    description: str
    recommendations: Optional[List[str]]

    class Config:
        from_attributes = True


class AuditSessionSchema(BaseModel):
    id: str
    filename: str
    total_rows: int
    detected_columns: Optional[Dict[str, Any]]
    composite_score: Optional[float]
    quality_tier: Optional[str]
    created_at: datetime
    results: List[TestResultSchema] = []

    class Config:
        from_attributes = True


class SessionListItem(BaseModel):
    id: str
    filename: str
    total_rows: int
    composite_score: Optional[float]
    quality_tier: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
