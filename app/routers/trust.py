from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.profile import Profile
from app.services.trust_engine import refresh_trust_score
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/trust", tags=["Trust"])


@router.post("/refresh")
def refresh_my_trust_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = refresh_trust_score(current_user, db)
    return result


@router.get("/score/{username}")
def get_user_trust_score(
    username: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.query(Profile).filter(
        Profile.user_id == user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {
        "username": username,
        "trust_score": profile.trust_score,
        "github_activity_score": profile.github_activity_score,
        "profile_completeness": profile.profile_completeness,
        "reliability_score": profile.reliability_score,
        "average_rating": profile.average_rating,
        "hackathons_joined": profile.hackathons_joined,
        "hackathons_completed": profile.hackathons_completed
    }