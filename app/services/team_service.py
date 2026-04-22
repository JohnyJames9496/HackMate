from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from app.models.team import Team, TeamMember, MemberStatus
from app.models.user import User
from app.schemas.team import TeamCreate, TeamApply, TeamApplicationAction

def create_team(data: TeamCreate, current_user: User, db: Session):
    hackathon = db.query(Team).filter(
        Team.hackathon_id == data.hackathon_id,
        Team.leader_id == current_user.id
    ).first()

    if hackathon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a team in this hackathon"
        )

    team = Team(
        hackathon_id=data.hackathon_id,
        leader_id=current_user.id,
        name=data.name,
        description=data.description,
        max_size=data.max_size,
        required_roles=[r.value for r in data.required_roles]
    )
    db.add(team)
    db.flush()

    leader_member = TeamMember(
        team_id=team.id,
        user_id=current_user.id,
        status=MemberStatus.accepted
    )
    db.add(leader_member)
    db.commit()
    db.refresh(team)

    return team


def apply_to_team(team_id: str, data: TeamApply, current_user: User, db: Session):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    if not team.is_open:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team is not accepting applications"
        )

    if team.leader_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are the leader of this team"
        )

    existing = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already applied to this team"
        )

    accepted_count = db.query(func.count(TeamMember.id)).filter(
        TeamMember.team_id == team_id,
        TeamMember.status == MemberStatus.accepted
    ).scalar()

    if accepted_count >= team.max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team is already full"
        )

    application = TeamMember(
        team_id=team_id,
        user_id=current_user.id,
        role=data.role,
        status=MemberStatus.pending
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return application


def handle_application(
    team_id: str,
    data: TeamApplicationAction,
    current_user: User,
    db: Session
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    if team.leader_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the team leader can accept or reject applications"
        )

    member = db.query(TeamMember).filter(
        TeamMember.id == data.member_id,
        TeamMember.team_id == team_id,
        TeamMember.status == MemberStatus.pending
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    if data.action == "accept":
        accepted_count = db.query(func.count(TeamMember.id)).filter(
            TeamMember.team_id == team_id,
            TeamMember.status == MemberStatus.accepted
        ).scalar()

        if accepted_count >= team.max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team is already full"
            )

        member.status = MemberStatus.accepted

        accepted_count += 1
        if accepted_count >= team.max_size:
            team.is_open = False

    else:
        member.status = MemberStatus.rejected

    db.commit()
    db.refresh(member)
    return member


def get_teams(
    db: Session,
    hackathon_id: str = None,
    page: int = 1,
    limit: int = 10
):
    query = db.query(Team)

    if hackathon_id:
        query = query.filter(Team.hackathon_id == hackathon_id)

    total = query.count()
    offset = (page - 1) * limit
    teams = query.offset(offset).limit(limit).all()

    return {
        "teams": teams,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": -(-total // limit)
    }