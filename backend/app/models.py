from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str = "dialogue"
    data_json: str = "{}"  # script, character placements (x/y/scale), bg choice, subtitle style
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Character(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    voice_id: str  # Fish Audio voice ID
    image_path: str = ""  # cutout PNG/JPG/WebP


class Voice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    voice_id: str  # Fish Audio voice ID


class RenderJob(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int
    status: str = "queued"  # queued | scripting | tts | broll | subtitles | assembling | ready | error
    progress: int = 0
    output_path: str = ""
    error: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
