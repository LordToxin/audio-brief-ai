from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ApiKeyModel(BaseModel):
    id: Optional[int] = None
    key: str
    client_name: str
    tier: str = "pro"  # free, pro, enterprise
    monthly_limit: int = 500
    used_count: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None


class ActionItem(BaseModel):
    task: str
    assignee: Optional[str] = "Unassigned"
    priority: str = "Medium"  # High, Medium, Low


class IntelligenceBrief(BaseModel):
    summary: str
    key_points: List[str] = Field(default_factory=list)
    action_items: List[ActionItem] = Field(default_factory=list)
    sentiment: str = "Neutral"
    topics: List[str] = Field(default_factory=list)


class JobResponse(BaseModel):
    job_id: str
    title: str
    status: str  # PENDING, PROCESSING, COMPLETED, FAILED
    file_name: str
    file_size_bytes: int
    duration_seconds: float = 0.0
    transcript: Optional[str] = None
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    action_items: Optional[List[ActionItem]] = None
    sentiment: Optional[str] = None
    topics: Optional[List[str]] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


class JobListItem(BaseModel):
    job_id: str
    title: str
    status: str
    file_name: str
    duration_seconds: float
    created_at: str
    completed_at: Optional[str] = None


class CreateApiKeyRequest(BaseModel):
    client_name: str
    tier: str = "pro"
    monthly_limit: int = 500
