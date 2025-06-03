"""
Pydantic models for chat API endpoints
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    message: str = Field(..., description="User message to process")
    provider: str = Field(default="openai", description="LLM provider to use")
    model: Optional[str] = Field(default=None, description="Specific model to use")
    browser_config: Optional[Dict[str, Any]] = Field(default=None, description="Browser configuration")


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class ChatSessionResponse(BaseModel):
    id: str
    messages: List[ChatMessageResponse]
    created_at: datetime
    updated_at: datetime
    status: str


class ChatSessionCreateResponse(BaseModel):
    session_id: str
    message: str


class ChatSessionListResponse(BaseModel):
    sessions: List[ChatSessionResponse]


class ChatProvidersResponse(BaseModel):
    providers: Dict[str, List[str]]


class ChatSessionDeleteResponse(BaseModel):
    success: bool
    message: str


class ChatSessionCancelResponse(BaseModel):
    success: bool
    message: str


class ChatSessionExportResponse(BaseModel):
    session_data: Optional[Dict[str, Any]]
    success: bool
    message: str

