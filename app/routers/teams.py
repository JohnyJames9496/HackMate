from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.schemas.team import (
    TeamCreate, TeamApply, TeamApplicationAction,
    TeamResponse, TeamListResponse, MemberResponse
)
from app.services.team_service import (
    create_team, apply_to_team, handle_application, get_teams
)
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.post("/", response_model=TeamResponse)
def create(
    data: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_team(data, current_user, db)


@router.get("/", response_model=TeamListResponse)
def list_teams(
    hackathon_id: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    return get_teams(db, hackathon_id, page, limit)


@router.get("/{team_id}", response_model=TeamResponse)
def get_one(
    team_id: str,
    db: Session = Depends(get_db)
):
    from app.services.team_service import get_teams
    from app.models.team import Team
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.post("/{team_id}/apply", response_model=MemberResponse)
def apply(
    team_id: str,
    data: TeamApply,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return apply_to_team(team_id, data, current_user, db)


@router.post("/{team_id}/application", response_model=MemberResponse)
def manage_application(
    team_id: str,
    data: TeamApplicationAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return handle_application(team_id, data, current_user, db)