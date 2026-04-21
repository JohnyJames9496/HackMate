from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone
import uuid
import enum

class TeamRole(enum.Enum):
    Frontend = "Frontend"
    Backend = "Backend"
    ML = "ML"
    UI_UX = "UI_UX"
    DevOps = "DevOps"
    Other = "Other"

class MemberStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class Team(Base):
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hackathon_id = Column(UUID(as_uuid=True), ForeignKey("hackathons.id", ondelete="CASCADE"), nullable=False)
    leader_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    max_size = Column(Integer, default=4)
    required_roles = Column(ARRAY(String), default=[])
    is_open = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    hackathon = relationship("Hackathon", backref="teams")
    leader = relationship("User", backref="led_teams")
    members = relationship("TeamMember", backref="team", lazy="joined")

    def __repr__(self):
        return f"<Team {self.name}>"


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(TeamRole), default=TeamRole.Other)
    status = Column(Enum(MemberStatus), default=MemberStatus.pending)
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", backref="team_memberships")

    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="unique_team_member"),
    )

    def __repr__(self):
        return f"<TeamMember team={self.team_id} user={self.user_id}>"