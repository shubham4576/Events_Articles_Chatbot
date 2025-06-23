from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class APIRequestSchema(BaseModel):
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    type: str = Field(
        default="all", description="Type of data to fetch: 'event', 'article', or 'all'"
    )


class EventSchema(BaseModel):
    # Primary key
    id: Optional[int] = None

    # Basic event information (from API)
    post_title: str
    post_content: Optional[str] = None
    enabled: Optional[str] = None

    # Event specific details
    event_dates: Optional[str] = None
    event_logo: Optional[str] = None
    location: Optional[str] = None
    venue: Optional[str] = None
    url: Optional[str] = None

    # Social media fields
    twitter_handle: Optional[str] = None
    twitter_tag: Optional[str] = None

    # User/Author information
    user_id: Optional[str] = None
    user_login: Optional[str] = None
    user_email: Optional[str] = None
    display_name: Optional[str] = None

    # Author details
    author_booth_numbers: Optional[str] = None
    author_company_contact_name: Optional[str] = None
    author_company_name__title: Optional[str] = None
    author_event: Optional[str] = None
    author_phone_number: Optional[str] = None
    author_url: Optional[str] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArticleSchema(BaseModel):
    # Primary key
    id: Optional[int] = None

    # Basic article information (from API)
    post_title: Optional[str] = None
    post_content: Optional[str] = None

    # Content descriptions (for embeddings)
    keywords: Optional[str] = None
    short_description: Optional[str] = None
    social_media_description: Optional[str] = None
    twitter_description: Optional[str] = None

    # Social and external links
    social_name: Optional[str] = None
    url: Optional[str] = None

    # User/Author information
    user_id: Optional[str] = None
    user_login: Optional[str] = None
    user_email: Optional[str] = None
    display_name: Optional[str] = None

    # Author details
    author_booth_numbers: Optional[str] = None
    author_company_contact_name: Optional[str] = None
    author_company_name__title: Optional[str] = None
    author_event: Optional[str] = None
    author_phone_number: Optional[str] = None
    author_url: Optional[str] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class APIResponseSchema(BaseModel):
    success: bool
    message: str
    events_processed: int = 0
    articles_processed: int = 0
    embeddings_created: int = 0
    data: Optional[Dict[str, Any]] = None


# Chatbot Schemas with Session-based Memory
class ChatMessageSchema(BaseModel):
    message: str = Field(..., description="User's message/question")
    session_id: str = Field(..., description="Session ID for conversation tracking and memory")


class ChatResponseSchema(BaseModel):
    response: str = Field(..., description="Chatbot's response")
    success: bool = Field(..., description="Whether the request was successful")
    session_id: str = Field(..., description="Session ID")
    timestamp: str = Field(..., description="Response timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata including session info")
    error: Optional[str] = Field(None, description="Error message if any")


class SessionHistorySchema(BaseModel):
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="Message timestamp")
    agent: Optional[str] = Field(None, description="Agent that generated the message")
    session_id: str = Field(..., description="Session ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SystemStatusSchema(BaseModel):
    chatbot_status: str = Field(..., description="Overall chatbot status")
    timestamp: str = Field(..., description="Status check timestamp")
    components: Dict[str, Any] = Field(default_factory=dict, description="Component status")
    statistics: Optional[Dict[str, Any]] = Field(None, description="System statistics")
    error: Optional[str] = Field(None, description="Error message if any")
