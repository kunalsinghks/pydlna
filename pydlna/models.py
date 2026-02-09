from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import enum

class MediaType(str, enum.Enum):
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    UNKNOWN = "unknown"

class MediaItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    file_path: str = Field(index=True, unique=True)
    filename: str
    parent_path: str = Field(index=True)
    
    title: str
    media_type: MediaType
    mime_type: str
    size: int
    duration: Optional[float] = None  # Seconds
    
    # Metadata
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    
    # Track info
    subtitle_tracks: int = Field(default=0)
    audio_tracks: int = Field(default=1)
    
    thumbnail_path: Optional[str] = None
    
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
