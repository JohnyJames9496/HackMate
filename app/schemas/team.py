from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from enum import Enum

class TeamRole(str, Enum):
    Frontend = "Frontend"
    Backend = "Backend"
    ML = "ML"
    UI_UX = "UI_UX"
    DevOps = "DevOps"
    Other = "Other"

class MemberStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class TeamCreate(BaseModel):
    hackathon_id: UUID
    name: str
    description: Optional[str] = None
    max_size: int = 4
    required_roles: Optional[List[TeamRole]] = []

    @field_validator("name")
    @classmethod
    def name_valid(cls, v):
        if len(v) < 3:
            raise ValueError("Team name must be at least 3 characters")
        if len(v) > 255:
            raise ValueError("Team name must be under 255 characters")
        return v.strip()

    @field_validator("max_size")
    @classmethod
    def size_valid(cls, v):
        if v < 2 or v > 10:
            raise ValueError("Team size must be between 2 and 10")
        return v

class TeamApply(BaseModel):
    role: TeamRole = TeamRole.Other

class TeamApplicationAction(BaseModel):
    member_id: UUID
    action: str

    @field_validator("action")
    @classmethod
    def action_valid(cls, v):
        if v not in ["accept", "reject"]:
            raise ValueError("Action must be 'accept' or 'reject'")
        return v

class MemberResponse(BaseModel):
    id: UUID
    user_id: UUID
    role: TeamRole
    status: MemberStatus
    joined_at: datetime

    model_config = {"from_attributes": True}

class TeamResponse(BaseModel):
    id: UUID
    hackathon_id: UUID
    leader_id: UUID
    name: str
    description: Optional[str]
    max_size: int
    required_roles: List[str]
    is_open: bool
    created_at: datetime
    members: List[MemberResponse] = []

    model_config = {"from_attributes": True}

class TeamListResponse(BaseModel):
    teams: List[TeamResponse]
    total: int
    page: int
    limit: int
    total_pages: int