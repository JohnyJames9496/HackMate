from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.team import Team
from app.schemas.matching import TeamRecommendationList, UserRecommendationList
from app.services.matching_engine import (
    get_team_recommendations_for_user,
    get_user_recommendations_for_team,
    get_missing_roles
)
from app.utils.dependencies import get_current_user
from fastapi import HTTPException

router = APIRouter(prefix="/recommendations", tags=["Matching"])


@router.get("/teams", response_model=TeamRecommendationList)
def recommend_teams_for_user(
    limit: int = Query(default=10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    recommendations = get_team_recommendations_for_user(
        current_user, db, limit
    )
    return {
        "recommendations": recommendations,
        "total": len(recommendations)
    }


@router.get("/users/{team_id}", response_model=UserRecommendationList)
def recommend_users_for_team(
    team_id: str,
    limit: int = Query(default=10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if team.leader_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only team leader can see recommendations"
        )

    recommendations = get_user_recommendations_for_team(
        team_id, current_user, db, limit
    )

    missing = get_missing_roles(team)

    return {
        "recommendations": recommendations,
        "total": len(recommendations),
        "team_id": team_id,
        "missing_roles": missing
    }