from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime

class CategoryOption(BaseModel):
    id: str = Field(..., description="categoryId (categories.id)")
    label: str = Field(..., description='categories."categoryValue"')

class TimeSeriesPoint(BaseModel):
    categoryId: str
    snapshotTs: datetime
    concurrentUserCount: int
    openLiveCount: int | None = None

class StreamCard(BaseModel):
    rank: int
    categoryId: str
    liveTitle: str | None = None
    channelName: str | None = None
    stream_url: str | None = None
    secure_url: str | None = None
    channelImageUrl: str | None = None
    liveImageUrl: str | None = None
    concurrentUserCount: int | None = None
