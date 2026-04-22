from fastapi import FastAPI
from app.config import PROJECT_NAME
from app.models import User,Profile
from app.routers import auth,profile,hackathons,teams
app = FastAPI(title=PROJECT_NAME)


app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(hackathons.router)
app.include_router(teams.router)
@app.get("/")
def home():
  return {"message": f"{PROJECT_NAME} is alive"}

@app.get('/health')
def health():
  return {"status" : "Ok",
          "Project": PROJECT_NAME}
@app.get('/about')
def about():
  return {"project": PROJECT_NAME,
          "version": "0.8.0",
          "description": "Hackathon team formation platform"
          }
