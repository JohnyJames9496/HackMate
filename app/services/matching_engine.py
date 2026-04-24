from sqlalchemy.orm import Session
from app.models.user import User
from app.models.profile import Profile
from app.models.team import Team, TeamMember, MemberStatus
from app.models.hackathon import Hackathon
from typing import List, Dict, Optional

# ─────────────────────────────────────────
# SCORING WEIGHTS
# ─────────────────────────────────────────
SKILL_WEIGHT = 0.40
COMPLEMENTARITY_WEIGHT = 0.30
EXPERIENCE_WEIGHT = 0.15
AVAILABILITY_WEIGHT = 0.15

# ─────────────────────────────────────────
# EXPERIENCE LEVEL SCORES
# ─────────────────────────────────────────
EXPERIENCE_SCORES = {
    "beginner": 0.25,
    "intermediate": 0.75,
    "advanced": 1.0
}

# ─────────────────────────────────────────
# AVAILABILITY SCORES
# ─────────────────────────────────────────
AVAILABILITY_SCORES = {
    "full_time": 1.0,
    "part_time": 0.6,
    "weekend": 0.4
}


def calculate_skill_score(
    user_skills: List[str],
    required_skills: List[str]
) -> float:
    if not required_skills:
        return 1.0
    if not user_skills:
        return 0.0

    user_skills_lower = set(s.lower() for s in user_skills)
    required_lower = set(s.lower() for s in required_skills)

    overlap = user_skills_lower.intersection(required_lower)
    return len(overlap) / len(required_lower)


def calculate_complementarity_score(
    user_skills: List[str],
    team_members: List[TeamMember],
    required_roles: List[str]
) -> float:
    if not required_roles:
        return 1.0

    existing_roles = set()
    for member in team_members:
        if member.status == MemberStatus.accepted:
            existing_roles.add(member.role.value.lower())

    missing_roles = set(r.lower() for r in required_roles) - existing_roles

    if not missing_roles:
        return 0.0

    user_skills_lower = set(s.lower() for s in user_skills)
    fills = 0
    for role in missing_roles:
        if role in user_skills_lower or any(
            role in skill for skill in user_skills_lower
        ):
            fills += 1

    return fills / len(missing_roles)


def calculate_experience_score(experience_level: str) -> float:
    return EXPERIENCE_SCORES.get(experience_level, 0.25)


def calculate_availability_score(availability: str) -> float:
    return AVAILABILITY_SCORES.get(availability, 0.4)


def score_user_for_team(
    profile: Profile,
    team: Team
) -> Dict:
    skill_score = calculate_skill_score(
        profile.skills or [],
        team.required_roles or []
    )

    comp_score = calculate_complementarity_score(
        profile.skills or [],
        team.members or [],
        team.required_roles or []
    )

    exp_score = calculate_experience_score(
        profile.experience_level.value
        if profile.experience_level else "beginner"
    )

    avail_score = calculate_availability_score(
        profile.availability.value
        if profile.availability else "part_time"
    )

    total_score = round(
        (skill_score * SKILL_WEIGHT) +
        (comp_score * COMPLEMENTARITY_WEIGHT) +
        (exp_score * EXPERIENCE_WEIGHT) +
        (avail_score * AVAILABILITY_WEIGHT),
        4
    )

    return {
        "total_score": total_score,
        "breakdown": {
            "skill_match": round(skill_score * SKILL_WEIGHT, 4),
            "complementarity": round(comp_score * COMPLEMENTARITY_WEIGHT, 4),
            "experience": round(exp_score * EXPERIENCE_WEIGHT, 4),
            "availability": round(avail_score * AVAILABILITY_WEIGHT, 4)
        }
    }


def get_team_recommendations_for_user(
    current_user: User,
    db: Session,
    limit: int = 10
) -> List[Dict]:
    profile = db.query(Profile).filter(
        Profile.user_id == current_user.id
    ).first()

    if not profile:
        return []

    already_in = db.query(TeamMember.team_id).filter(
        TeamMember.user_id == current_user.id
    ).subquery()

    open_teams = db.query(Team).filter(
        Team.is_open == True,
        Team.leader_id != current_user.id,
        ~Team.id.in_(already_in)
    ).all()

    scored_teams = []
    for team in open_teams:
        score_data = score_user_for_team(profile, team)
        scored_teams.append({
            "team_id": str(team.id),
            "team_name": team.name,
            "hackathon_id": str(team.hackathon_id),
            "required_roles": team.required_roles,
            "is_open": team.is_open,
            "max_size": team.max_size,
            "current_members": len([
                m for m in team.members
                if m.status == MemberStatus.accepted
            ]),
            "match_score": score_data["total_score"],
            "score_breakdown": score_data["breakdown"]
        })

    scored_teams.sort(key=lambda x: x["match_score"], reverse=True)
    return scored_teams[:limit]


def get_user_recommendations_for_team(
    team_id: str,
    current_user: User,
    db: Session,
    limit: int = 10
) -> List[Dict]:
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return []

    if team.leader_id != current_user.id:
        return []

    existing_member_ids = [
        m.user_id for m in team.members
        if m.status == MemberStatus.accepted
    ]

    users = db.query(User).filter(
        User.id != current_user.id,
        ~User.id.in_(existing_member_ids),
        User.is_active == True
    ).all()

    scored_users = []
    for user in users:
        profile = db.query(Profile).filter(
            Profile.user_id == user.id,
            Profile.ready_to_join == True
        ).first()

        if not profile:
            continue

        score_data = score_user_for_team(profile, team)
        scored_users.append({
            "user_id": str(user.id),
            "username": user.username,
            "skills": profile.skills or [],
            "experience_level": profile.experience_level.value
                if profile.experience_level else "beginner",
            "availability": profile.availability.value
                if profile.availability else "part_time",
            "trust_score": profile.trust_score,
            "match_score": score_data["total_score"],
            "score_breakdown": score_data["breakdown"]
        })

    scored_users.sort(key=lambda x: x["match_score"], reverse=True)
    return scored_users[:limit]


def get_missing_roles(team: Team) -> List[str]:
    accepted_roles = set()
    for member in team.members:
        if member.status == MemberStatus.accepted:
            accepted_roles.add(member.role.value.lower())

    required = set(r.lower() for r in (team.required_roles or []))
    missing = required - accepted_roles
    return list(missing)