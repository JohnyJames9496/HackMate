from fastapi import FastAPI
from app.config import PROJECT_NAME
from app.models import User, Profile, Hackathon, Team, TeamMember, Rating
from app.routers import auth, profile, hackathons, teams, matching, trust, ratings
from app.redis_client import get_redis

app = FastAPI(title=PROJECT_NAME)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(hackathons.router)
app.include_router(teams.router)
app.include_router(matching.router)
app.include_router(trust.router)
app.include_router(ratings.router)

@app.get("/")
def home():
    return {"message": f"Welcome to {PROJECT_NAME}!"}

@app.get("/health")
def health_check():
    redis = get_redis()
    redis_status = "connected" if redis else "not configured"
    try:
        if redis:
            redis.ping()
            redis_status = "connected"
    except Exception:
        redis_status = "error"

    return {
        "status": "ok",
        "project": PROJECT_NAME,
        "redis": redis_status
    }

@app.get("/about")
def about():
    return {
        "project": PROJECT_NAME,
        "version": "0.13.0",
        "description": "Hackathon team formation platform"
    }