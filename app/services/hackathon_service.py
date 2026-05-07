from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from fastapi import HTTPException, status
from app.models.hackathon import Hackathon
from app.models.user import User
from app.schemas.hackathon import HackathonCreate
from app.redis_client import cache_get, cache_set, cache_delete_pattern
from typing import Optional
import uuid

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

    cache_delete_pattern("hackathons:*")

    return hackathon


def get_hackathons(
    db: Session,
    page: int = 1,
    limit: int = 10,
    skill: Optional[str] = None,
    sort_by: str = "deadline"
):
    cache_key = f"hackathons:page{page}:limit{limit}:skill{skill}:sort{sort_by}"

    cached = cache_get(cache_key)
    if cached:
        return cached

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

    result = {
        "hackathons": [
            {
                "id": str(h.id),
                "creator_id": str(h.creator_id),
                "title": h.title,
                "description": h.description,
                "required_skills": h.required_skills,
                "deadline": h.deadline.isoformat(),
                "is_active": h.is_active,
                "created_at": h.created_at.isoformat()
            }
            for h in hackathons
        ],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }

    cache_set(cache_key, result, ttl=300)
    return result


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