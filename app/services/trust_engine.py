from sqlalchemy.orm import Session
from app.models.profile import Profile
from app.models.user import User
from app.utils.github_client import fetch_github_data, calculate_github_activity_score
from typing import Dict

def calculate_profile_completeness(profile: Profile) -> float:
    fields = {
        "bio": profile.bio,
        "skills": profile.skills,
        "github_url": profile.github_url,
        "linkedin_url": profile.linkedin_url,
        "experience_level": profile.experience_level,
        "availability": profile.availability,
    }
    filled = sum(1 for v in fields.values() if v)
    return round(filled / len(fields), 4)


def calculate_reliability_score(profile: Profile) -> float:
    if profile.hackathons_joined == 0:
        return 1.0
    return round(
        profile.hackathons_completed / profile.hackathons_joined,
        4
    )


def calculate_trust_score(profile: Profile) -> float:
    github_weight = 0.30
    completeness_weight = 0.25
    reliability_weight = 0.25
    rating_weight = 0.20

    rating_score = profile.average_rating / 5.0 if profile.average_rating else 0.5

    trust = (
        (profile.github_activity_score * github_weight) +
        (profile.profile_completeness * completeness_weight) +
        (profile.reliability_score * reliability_weight) +
        (rating_score * rating_weight)
    )
    return round(trust, 4)


def refresh_trust_score(user: User, db: Session) -> Dict:
    profile = db.query(Profile).filter(
        Profile.user_id == user.id
    ).first()

    if not profile:
        return {"error": "Profile not found"}

    if profile.github_url:
        github_data = fetch_github_data(profile.github_url)
        profile.github_activity_score = calculate_github_activity_score(
            github_data
        )
        profile.github_languages = github_data.get("languages", {})
        profile.github_repo_count = github_data.get("public_repos", 0)

    profile.profile_completeness = calculate_profile_completeness(profile)
    profile.reliability_score = calculate_reliability_score(profile)
    profile.trust_score = calculate_trust_score(profile)

    db.commit()
    db.refresh(profile)

    return {
        "trust_score": profile.trust_score,
        "github_activity_score": profile.github_activity_score,
        "profile_completeness": profile.profile_completeness,
        "reliability_score": profile.reliability_score,
        "average_rating": profile.average_rating,
        "github_repo_count": profile.github_repo_count,
        "github_languages": profile.github_languages
    }