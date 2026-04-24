from pydantic import BaseModel
from uuid import UUID
from typing import List, Dict, Optional

class ScoreBreakdown(BaseModel):
    skill_match: float
    complementarity: float
    experience: float
    availability: float

class TeamRecommendation(BaseModel):
    team_id: str
    team_name: str
    hackathon_id: str
    required_roles: List[str]
    is_open: bool
    max_size: int
    current_members: int
    match_score: float
    score_breakdown: ScoreBreakdown

class UserRecommendation(BaseModel):
    user_id: str
    username: str
    skills: List[str]
    experience_level: str
    availability: str
    trust_score: float
    match_score: float
    score_breakdown: ScoreBreakdown

class TeamRecommendationList(BaseModel):
    recommendations: List[TeamRecommendation]
    total: int

class UserRecommendationList(BaseModel):
    recommendations: List[UserRecommendation]
    total: int
    team_id: str
    missing_roles: List[str]