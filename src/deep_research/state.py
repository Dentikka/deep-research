"""Pydantic модели для состояния исследования."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class Finding(BaseModel):
    """Найденный источник информации."""
    
    source: str = Field(..., description="Источник: tavily, github, arxiv")
    url: str
    title: str
    content: str
    score: float = Field(default=0.0, description="Релевантность 0-1")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ResearchState(BaseModel):
    """Состояние сессии исследования."""
    
    # Идентификация
    session_id: str
    query: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Планирование
    plan: List[str] = Field(default_factory=list)
    current_step: int = Field(default=0)
    
    # Данные
    findings: List[Finding] = Field(default_factory=list)
    
    # Контроль
    user_feedback: Optional[str] = None
    status: str = Field(default="active")  # active, paused, completed
    
    # Результат
    final_report: Optional[str] = None
    report_path: Optional[str] = None
    
    # Метрики
    total_tokens: int = Field(default=0)
    search_calls: int = Field(default=0)
    
    class Config:
        arbitrary_types_allowed = True
