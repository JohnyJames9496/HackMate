from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.rating import RatingCreate, RatingResponse, UserRatingSummary
from app.services.rating_service import create_rating, get_user_ratings
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/ratings", tags=["Ratings"])


@router.post("/", response_model=RatingResponse)
def rate_teammate(
    data: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_rating(data, current_user, db)


@router.get("/{username}", response_model=UserRatingSummary)
def get_ratings(
    username: str,
    db: Session = Depends(get_db)
):
    return get_user_ratings(username, db)