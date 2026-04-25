from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from app.models.rating import Rating
from app.models.team import Team, TeamMember, MemberStatus
from app.models.profile import Profile
from app.models.user import User
from app.schemas.rating import RatingCreate
from app.services.trust_engine import calculate_trust_score

def create_rating(data: RatingCreate, current_user: User, db: Session):
    if str(data.ratee_id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot rate yourself"
        )

    rater_member = db.query(TeamMember).filter(
        TeamMember.team_id == data.team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.status == MemberStatus.accepted
    ).first()

    if not rater_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this team"
        )

    ratee_member = db.query(TeamMember).filter(
        TeamMember.team_id == data.team_id,
        TeamMember.user_id == data.ratee_id,
        TeamMember.status == MemberStatus.accepted
    ).first()

    if not ratee_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user you are rating is not a member of this team"
        )

    existing = db.query(Rating).filter(
        Rating.rater_id == current_user.id,
        Rating.ratee_id == data.ratee_id,
        Rating.team_id == data.team_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already rated this teammate"
        )

    rating = Rating(
        rater_id=current_user.id,
        ratee_id=data.ratee_id,
        team_id=data.team_id,
        score=data.score,
        feedback=data.feedback
    )
    db.add(rating)
    db.commit()

    update_average_rating(data.ratee_id, db)

    db.refresh(rating)
    return rating


def update_average_rating(user_id, db: Session):
    avg = db.query(func.avg(Rating.score)).filter(
        Rating.ratee_id == user_id
    ).scalar()

    profile = db.query(Profile).filter(
        Profile.user_id == user_id
    ).first()

    if profile:
        profile.average_rating = round(float(avg or 0), 2)
        profile.trust_score = calculate_trust_score(profile)
        db.commit()


def get_user_ratings(username: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    profile = db.query(Profile).filter(
        Profile.user_id == user.id
    ).first()

    ratings = db.query(Rating).filter(
        Rating.ratee_id == user.id
    ).all()

    return {
        "username": username,
        "average_rating": profile.average_rating if profile else 0.0,
        "total_ratings": len(ratings),
        "trust_score": profile.trust_score if profile else 0.0,
        "ratings": ratings
    }