from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class RatingCreate(BaseModel):
    ratee_id: UUID
    team_id: UUID
    score: int
    feedback: Optional[str] = None

    @field_validator("score")
    @classmethod
    def score_valid(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Score must be between 1 and 5")
        return v

    @field_validator("feedback")
    @classmethod
    def feedback_valid(cls, v):
        if v and len(v) > 500:
            raise ValueError("Feedback must be under 500 characters")
        return v


class RatingResponse(BaseModel):
    id: UUID
    rater_id: UUID
    ratee_id: UUID
    team_id: UUID
    score: int
    feedback: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class UserRatingSummary(BaseModel):
    username: str
    average_rating: float
    total_ratings: int
    trust_score: float
    ratings: List[RatingResponse]