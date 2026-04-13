from sqlalchemy import Column, String, Boolean, Float, Integer, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
import enum

class ExperienceLevel(enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class Availability(enum.Enum):
    part_time = "part_time"
    full_time = "full_time"
    weekend = "weekend"

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    skills = Column(ARRAY(String), default=[])
    experience_level = Column(Enum(ExperienceLevel), default=ExperienceLevel.beginner)
    availability = Column(Enum(Availability), default=Availability.part_time)
    github_url = Column(String(255), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    ready_to_join = Column(Boolean, default=False)
    github_activity_score = Column(Float, default=0.0)
    profile_completeness = Column(Float, default=0.0)
    reliability_score = Column(Float, default=1.0)
    trust_score = Column(Float, default=0.0)
    hackathons_joined = Column(Integer, default=0)
    hackathons_completed = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)

    user = relationship("User", backref="profile")

    def __repr__(self):
        return f"<Profile user_id={self.user_id}>"