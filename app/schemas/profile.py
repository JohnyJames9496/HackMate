from pydantic import BaseModel, HttpUrl, field_validator
from uuid import UUID
from typing import Optional, List
from enum import Enum

class ExperienceLevel(str,Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
class Availability(str,Enum):
    part_time = "part_time"
    full_time = "full_time"
    weekend = "weekend"

class ProfileUpdate(BaseModel):
    bio:Optional[str]=None
    skills:Optional[List[str]]=None
    experience_level:Optional[ExperienceLevel] =None
    availability:Optional[Availability]=None
    github_url:Optional[str]=None
    linkedin_url:Optional[str]=None
    ready_to_join:Optional[bool]=None

    @field_validator("skills")
    @classmethod
    def skills_valid(cls,v):
        if v and len(v) > 20:
            raise ValueError("Maximum 20 skills allowed")
        if v:
            return [skills.strip().lower() for skills in v]
        return v
    
    @field_validator("bio")
    @classmethod
    def bio_valid(cls,v):
        if v and len(v) > 500:
            raise ValueError("Bio must be less than 500 characters")
        return v

class ProfileResponse(BaseModel):
    id : UUID
    user_id :UUID
    bio:Optional[str]=None
    skills:List[str]
    experience_level:ExperienceLevel
    availability:Availability
    github_url:Optional[str]=None
    linkedin_url:Optional[str]=None
    ready_to_join:bool
    github_activity_score:float
    profile_completeness:float
    reliability_score:float
    trust_score:float
    hackathons_joined:int
    hackathons_completed:int
    average_rating:float

    model_config = {"from_attributes": True}

class FullUserResponse(BaseModel):
    id : UUID
    email:str
    username:str
    is_active:bool
    profile: Optional[ProfileResponse]=None

    model_config = {"from_attributes":True}

    