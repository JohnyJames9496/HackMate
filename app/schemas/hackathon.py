from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class HackathonCreate(BaseModel):
    title: str
    description: Optional[str] = None
    required_skills: Optional[List[str]] = []
    deadline: datetime

    @field_validator("title")
    @classmethod
    def title_valid(cls, v):
        if len(v) < 5:
            raise ValueError("Title must be at least 5 characters")
        if len(v) > 255:
            raise ValueError("Title must be under 255 characters")
        return v.strip()

    @field_validator("required_skills")
    @classmethod
    def skills_valid(cls, v):
        if v:
            return [s.strip().lower() for s in v]
        return v

    @field_validator("deadline")
    @classmethod
    def deadline_valid(cls, v):
        if v < datetime.now(v.tzinfo):
            raise ValueError("Deadline must be in the future")
        return v


class HackathonResponse(BaseModel):
    id: UUID
    creator_id: UUID
    title: str
    description: Optional[str]
    required_skills: List[str]
    deadline: datetime
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class HackathonListResponse(BaseModel):
    hackathons: List[HackathonResponse]
    total: int
    page: int
    limit: int
    total_pages: int