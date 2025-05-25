from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Video(BaseModel):
    video_id: str
    title: str
    description: str
    published_at: datetime
    view_count: int
    like_count: int
    comment_count: int
    tags: List[str]
    transcript: Optional[str] = None

class Channel(BaseModel):
    channel_id: str
    title: str
    description: str
    subscriber_count: int
    video_count: int
    videos: List[Video]

class AnalysisResult(BaseModel):
    channel_id: str
    analysis_date: datetime
    summary: str
    recommendations: List[str]
    metrics: str
    sentiment_analysis: str 