from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.schemas.hackathon import HackathonCreate, HackathonResponse, HackathonListResponse
from app.services.hackathon_service import create_hackathon, get_hackathons, get_hackathon_by_id
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/hackathons", tags=["Hackathons"])


@router.post("/", response_model=HackathonResponse)
def create(
    data: HackathonCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_hackathon(data, current_user, db)


@router.get("/", response_model=HackathonListResponse)
def list_hackathons(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50),
    skill: Optional[str] = Query(default=None),
    sort_by: str = Query(default="deadline", pattern="^(deadline|created_at)$"),
    db: Session = Depends(get_db)
):
    return get_hackathons(db, page, limit, skill, sort_by)


@router.get("/{hackathon_id}", response_model=HackathonResponse)
def get_one(
    hackathon_id: str,
    db: Session = Depends(get_db)
):
    return get_hackathon_by_id(hackathon_id, db)