from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from fastapi import HTTPException, status
from app.models.hackathon import Hackathon
from app.models.user import User
from app.schemas.hackathon import HackathonCreate
from typing import Optional

def create_hackathon(data: HackathonCreate, current_user: User, db: Session):
    hackathon = Hackathon(
        creator_id=current_user.id,
        title=data.title,
        description=data.description,
        required_skills=data.required_skills,
        deadline=data.deadline
    )
    db.add(hackathon)
    db.commit()
    db.refresh(hackathon)
    return hackathon


def get_hackathons(
    db: Session,
    page: int = 1,
    limit: int = 10,
    skill: Optional[str] = None,
    sort_by: str = "deadline"
):
    query = db.query(Hackathon).filter(Hackathon.is_active == True)

    if skill:
        query = query.filter(
            Hackathon.required_skills.any(skill.lower())
        )

    if sort_by == "deadline":
        query = query.order_by(asc(Hackathon.deadline))
    else:
        query = query.order_by(desc(Hackathon.created_at))

    total = query.count()

    offset = (page - 1) * limit
    hackathons = query.offset(offset).limit(limit).all()

    total_pages = -(-total // limit)

    return {
        "hackathons": hackathons,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }


def get_hackathon_by_id(hackathon_id: str, db: Session):
    hackathon = db.query(Hackathon).filter(
        Hackathon.id == hackathon_id
    ).first()

    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )

    return hackathon